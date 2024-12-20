from datetime import datetime, timezone
from tombstone.tombstone_base_data import ALIAS, OFFICE, PARTY, PARTY_ROLE, RESOLUTION, SHARE_CLASSES
import copy
import pandas as pd
from sqlalchemy import Connection, text


def format_business_data(data: dict) -> dict:
    business_data = data['businesses'][0]
    # Note: only ACT or HIS
    state = business_data['state']
    business_data['state'] = 'ACTIVE' if state == 'ACT' else 'HISTORICAL'

    formatted_business = {
        **business_data,
        'fiscal_year_end_date': business_data['founding_date'],
        'last_ledger_timestamp': business_data['founding_date'],
        'last_modified': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    }

    if (last_ar_date := business_data['last_ar_date']):
        last_ar_year = int(last_ar_date.split('-')[0])
        formatted_business['last_ar_year'] = last_ar_year

    return formatted_business


def format_address_data(address_data: dict, prefix: str) -> dict:
    # Note: all corps have a format type of null or FOR
    address_type = 'mailing' if prefix == 'ma_' else 'delivery'
    
    street = address_data[f'{prefix}addr_line_1']
    street_additional_elements = []
    if (line_2 := address_data[f'{prefix}addr_line_2']) and (line_2 := line_2.strip()):
        street_additional_elements.append(line_2)
    if (line_3 := address_data[f'{prefix}addr_line_3']) and (line_3 := line_3.strip()):
        street_additional_elements.append(line_3)
    street_additional = ' '.join(street_additional_elements)

    if not (delivery_instructions := address_data[f'{prefix}delivery_instructions']) \
        or not (delivery_instructions := delivery_instructions.strip()):
        delivery_instructions = ''

    formatted_address = {
        'address_type': address_type,
        'street': street,
        'street_additional': street_additional,
        'city': address_data[f'{prefix}city'],
        'region': address_data[f'{prefix}province'],
        'country': address_data[f'{prefix}country_typ_cd'],
        'postal_code': address_data[f'{prefix}postal_cd'],
        'delivery_instructions': delivery_instructions
    }
    return formatted_address


def format_offices_data(data: dict) -> list[dict]:
    offices_data = data['offices']
    formatted_offices = []

    for x in offices_data:
        # Note: only process RC and RG now (done in SQL)
        # TODO: support other office types
        office = copy.deepcopy(OFFICE)
        office['offices']['office_type'] = 'recordsOffice' if x['o_office_typ_cd'] == 'RC' else 'registeredOffice'

        mailing_address = format_address_data(x, 'ma_')
        delivery_address = format_address_data(x, 'da_')

        office['addresses'].append(mailing_address)
        office['addresses'].append(delivery_address)

        formatted_offices.append(office)
    
    return formatted_offices


def format_parties_data(data: dict) -> list[dict]:
    parties_data = data['parties']

    if not parties_data:
        return []

    formatted_parties = []

    df = pd.DataFrame(parties_data)
    grouped_parties = df.groupby('cp_full_name')
    for _, group in grouped_parties:
        party = copy.deepcopy(PARTY)
        party_info = group.iloc[0].to_dict()
        party['parties']['first_name'] = party_info['cp_first_name']
        party['parties']['middle_initial'] = party_info['cp_middle_name']
        party['parties']['last_name'] = party_info['cp_last_name']
        party['parties']['party_type'] = 'person'

        # Note: can be index 0
        if (ma_index := group['cp_mailing_addr_id'].first_valid_index()) is not None:
            mailing_addr_data = group.loc[ma_index].to_dict()
        else:
            mailing_addr_data = None
        
        if (da_index := group['cp_delivery_addr_id'].first_valid_index()) is not None:
            delivery_addr_data = group.loc[da_index].to_dict()
        else:
            delivery_addr_data = None

        if mailing_addr_data:
            mailing_address = format_address_data(mailing_addr_data, 'ma_')
            party['addresses'].append(mailing_address)
        if delivery_addr_data:
            delivery_address = format_address_data(delivery_addr_data, 'da_')
            party['addresses'].append(delivery_address)

        formatted_party_roles = party['party_roles']
        for _, r in group.iterrows():
            if (role_code := r['cp_party_typ_cd']) not in ['INC', 'DIR']:
                continue
            role = 'incorporator' if role_code == 'INC' else 'director'
            party_role = copy.deepcopy(PARTY_ROLE)
            party_role['role'] = role
            party_role['appointment_date'] = r['cp_appointment_dt_str']
            party_role['cessation_date'] = r['cp_cessation_dt_str']
            formatted_party_roles.append(party_role)
        
        formatted_parties.append(party)
    
    return formatted_parties


def format_share_series_data(share_series_data: dict) -> dict:
    formatted_series = {
        'name': share_series_data['srs_series_nme'],
        'priority': int(share_series_data['srs_series_id']) if share_series_data['srs_series_id'] else None,
        'max_share_flag': share_series_data['srs_max_share_ind'],
        'max_shares': int(share_series_data['srs_share_quantity']) if share_series_data['srs_share_quantity'] else None,
        'special_rights_flag': share_series_data['srs_spec_right_ind']
    }

    return formatted_series


def format_share_classes_data(data: dict) -> list[dict]:
    share_classes_data = data['share_classes']

    if not share_classes_data:
        return []

    formatted_share_classes = []

    df = pd.DataFrame(share_classes_data)
    grouped_share_classes = df.groupby('ssc_share_class_id')

    for share_class_id, group in grouped_share_classes:
        share_class = copy.deepcopy(SHARE_CLASSES)
        share_class_info = group.iloc[0].to_dict()

        priority = int(share_class_info['ssc_share_class_id']) if share_class_info['ssc_share_class_id'] else None
        max_shares = int(share_class_info['ssc_share_quantity']) if share_class_info['ssc_share_quantity'] else None
        par_value = float(share_class_info['ssc_par_value_amt']) if share_class_info['ssc_par_value_amt'] else None
        
        # TODO: map NULL or custom input value of ssc_other_currency
        if (currency := share_class_info['ssc_currency_typ_cd']) == 'OTH':
            currency = share_class_info['ssc_other_currency']

        share_class['share_classes']['name'] = share_class_info['ssc_class_nme']
        share_class['share_classes']['priority'] = priority
        share_class['share_classes']['max_share_flag'] = share_class_info['ssc_max_share_ind']
        share_class['share_classes']['max_shares'] = max_shares
        share_class['share_classes']['par_value_flag'] = share_class_info['ssc_par_value_ind']
        share_class['share_classes']['par_value'] = par_value
        share_class['share_classes']['currency'] = currency
        share_class['share_classes']['special_rights_flag'] = share_class_info['ssc_spec_rights_ind']

        # Note: srs_share_class_id should be either None or equal to share_class_id
        matching_series = group[group['srs_share_class_id']==share_class_id]
        formatted_series = share_class['share_series']
        for _, r in matching_series.iterrows():
            formatted_series.append(format_share_series_data(r.to_dict()))

        formatted_share_classes.append(share_class)

    return formatted_share_classes


def format_aliases_data(data: dict) -> list[dict]:
    aliases_data = data['aliases']
    formatted_aliases = []

    for x in aliases_data:
        if x['cn_corp_name_typ_cd'] != 'TR':
            continue
        alias = copy.deepcopy(ALIAS)
        alias['alias'] = x['cn_corp_name']
        alias['type'] = 'TRANSLATION'
        formatted_aliases.append(alias)

    return formatted_aliases


def format_resolutions_data(data: dict) -> list[dict]:
    resolutions_data = data['resolutions']
    formatted_resolutions = []

    for x in resolutions_data:
        resolution = copy.deepcopy(RESOLUTION)
        resolution['resolution_date'] = x['r_resolution_dt_str']
        resolution['type'] = 'SPECIAL'
        formatted_resolutions.append(resolution)

    return formatted_resolutions


def get_snapshot_data_formatters() -> dict:
    ret = {
        'businesses': format_business_data,
        'offices': format_offices_data,
        'parties': format_parties_data,
        'share_classes': format_share_classes_data,
        'aliases': format_aliases_data,
        'resolutions': format_resolutions_data
    }
    return ret



def load_data(conn: Connection, table_name: str, data: dict) -> int:
    columns = ', '.join(data.keys())
    values = ', '.join([format_value(v) for v in data.values()])
    query = f"""insert into {table_name} ({columns}) values ({values}) returning id"""

    result = conn.execute(text(query))
    id = result.scalar()

    return id


def format_value(value) -> str:
    if value is None:
        return 'NULL'
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        # Note: handle single quote issue
        value = str(value).replace("'", "''")
        return f"'{value}'"
