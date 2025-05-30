"""empty message

Revision ID: e6ff12b18bef
Revises: 026f42f4f654
Create Date: 2021-12-01 12:32:41.850361

"""
from alembic import op
from sqlalchemy import MetaData, Table

# revision identifiers, used by Alembic.
revision = '4eff12b18bef'
down_revision = '3eed22dc70ca'
branch_labels = None
depends_on = None


def upgrade():
    """Load all of the lookup data."""
    bind = op.get_bind()
    meta = MetaData()
    office_types_table = Table('office_types', meta, autoload_with=bind)

    op.bulk_insert(
        office_types_table,
        [
            {
                'identifier':'registeredOffice', 'description':'Registered Office'
            },
            {
                'identifier':'recordsOffice', 'description':'Records Office'
            },
            {
                'identifier':'custodialOffice', 'description':'Custodial Office'
            },
            {
                'identifier':'businessOffice', 'description':'Business Office'
            },
            {
                'identifier':'liquidationRecordsOffice', 'description':'Liquidation Records Office'
            },
        ]
    )

    configurations_table = Table('configurations', meta, autoload_with=bind)
    op.bulk_insert(
        configurations_table,
        [
            {
                'name': 'NUM_DISSOLUTIONS_ALLOWED',
                'val': '2',
                'short_description': 'Number of involuntary dissolutions per day.',
                'full_description': 'Number of involuntary dissolutions per day.'
            },
            {
                'name': 'MAX_DISSOLUTIONS_ALLOWED',
                'val': '2500',
                'short_description': 'Max number of involuntary dissolutions permitted per day.',
                'full_description': 'Max number of involuntary dissolutions permitted per day. This is used to validate the upper limit for NUM_DISSOLUTIONS_ALLOWED.'
            },
            {
                'name': 'DISSOLUTIONS_STAGE_1_SCHEDULE',
                'val': '* * * * * ',
                'short_description': 'Cron string for which days new involuntary dissolutions can be initiated.',
                'full_description': 'Cron string for which days new involuntary dissolutions can be initiated.'
            },
            {
                'name': 'DISSOLUTIONS_STAGE_2_SCHEDULE',
                'val': '* * * * * ',
                'short_description': 'Schedule for running stage 2 of dissolution process.',
                'full_description': 'Schedule for running stage 2 of dissolution process.'
            },
            {
                'name': 'DISSOLUTIONS_STAGE_3_SCHEDULE',
                'val': '* * * * * ',
                'short_description': 'Schedule for running stage 3 of dissolution process.',
                'full_description': 'Schedule for running stage 3 of dissolution process.'
            },
        ]
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    pass
