# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here.

All items are loaded, or have Constants defined here that
are loaded into the Flask configuration.
All modules and lookups get their configuration from the
Flask config, rather than reading environment variables directly
or by accessing this configuration directly.
"""

import os
import sys

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'legal_api.config.DevConfig',
    'testing': 'legal_api.config.TestConfig',
    'production': 'legal_api.config.ProdConfig',
    'default': 'legal_api.config.ProdConfig',
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        config = ProdConfig()
    elif config_name == 'testing':
        config = TestConfig()
    elif config_name == 'development':
        config = DevConfig()
    else:
        raise KeyError(f'Unknown configuration: {config_name}')
    return config


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    SERVICE_NAME = 'legal-api'
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DEPLOYMENT_PLATFORM = os.getenv('DEPLOYMENT_PLATFORM', 'OCP')

    # API Endpoints
    AUTH_API_URL = os.getenv('AUTH_API_URL', '')
    AUTH_API_VERSION = os.getenv('AUTH_API_VERSION', '')
    BUSINESS_API_URL = os.getenv('BUSINESS_API_URL', '')
    BUSINESS_API_VERSION_2 = os.getenv('BUSINESS_API_VERSION_2', '')
    LEGAL_API_URL = os.getenv('LEGAL_API_URL', '')
    LEGAL_API_VERSION_2 = os.getenv('LEGAL_API_VERSION_2', '')
    NAMEX_API_URL = os.getenv('NAMEX_API_URL', '')
    NAMEX_API_VERSION = os.getenv('NAMEX_API_VERSION', '')
    PAY_API_URL = os.getenv('PAY_API_URL', '')
    PAY_API_VERSION = os.getenv('PAY_API_VERSION', '')
    REPORT_API_URL = os.getenv('REPORT_API_URL', '')
    REPORT_API_VERSION = os.getenv('REPORT_API_VERSION', '')
    REPORT_API_GOTENBERG_AUDIENCE = os.getenv('REPORT_API_GOTENBERG_AUDIENCE', '')
    REPORT_API_GOTENBERG_URL = os.getenv('REPORT_API_GOTENBERG_URL', 'https://')

    COLIN_URL = f"{os.getenv('COLIN_API_URL', '')}{os.getenv('COLIN_API_VERSION', '')}"
    # LEGAL_API_BASE_URL = f'{BUSINESS_API_URL + BUSINESS_API_VERSION_2}/businesses'

    # This is to use reverse proxy to make filingLink, commentLink, documentLink etc. work
    # Change to use BUSINESS API GW URL once the Migration to GCP is complete
    LEGAL_API_BASE_URL = f'{LEGAL_API_URL + LEGAL_API_VERSION_2}/businesses'

    # Temporary while there is inconsistency between OCP / GCP versions of 1pass env
    if NAMEX_API_VERSION and NAMEX_API_VERSION[-1] == '/':
        # remove the slash
        NAMEX_API_VERSION = NAMEX_API_VERSION[:-1]
    NAMEX_SVC_URL = f'{NAMEX_API_URL + NAMEX_API_VERSION}'
    PAYMENT_SVC_URL = f'{PAY_API_URL + PAY_API_VERSION}/payment-requests'
    AUTH_SVC_URL = f'{AUTH_API_URL + AUTH_API_VERSION}'
    REPORT_SVC_URL = f'{REPORT_API_URL + REPORT_API_VERSION}/reports'
    NAICS_API_URL = f'{BUSINESS_API_URL + BUSINESS_API_VERSION_2}/naics'

    REPORT_TEMPLATE_PATH = os.getenv('REPORT_PATH', 'report-templates')
    FONTS_PATH = os.getenv('FONTS_PATH', 'fonts')

    GO_LIVE_DATE = os.getenv('GO_LIVE_DATE')

    LD_SDK_KEY = os.getenv('LD_SDK_KEY', None)
    SECRET_KEY = 'a secret'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALEMBIC_INI = 'migrations/alembic.ini'
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')

    # POSTGRESQL
    if DB_UNIX_SOCKET := os.getenv('DATABASE_UNIX_SOCKET', None):
        SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}'
    else:
        SQLALCHEMY_DATABASE_URI = (
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv('JWT_OIDC_WELL_KNOWN_CONFIG')
    JWT_OIDC_ALGORITHMS = os.getenv('JWT_OIDC_ALGORITHMS')
    JWT_OIDC_JWKS_URI = os.getenv('JWT_OIDC_JWKS_URI')
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')
    JWT_OIDC_AUDIENCE = os.getenv('JWT_OIDC_AUDIENCE')
    JWT_OIDC_CLIENT_SECRET = os.getenv('JWT_OIDC_CLIENT_SECRET')
    JWT_OIDC_CACHING_ENABLED = os.getenv('JWT_OIDC_CACHING_ENABLED')
    JWT_OIDC_USERNAME = os.getenv('JWT_OIDC_USERNAME', 'username')
    JWT_OIDC_FIRSTNAME = os.getenv('JWT_OIDC_FIRSTNAME', 'firstname')
    JWT_OIDC_LASTNAME = os.getenv('JWT_OIDC_LASTNAME', 'lastname')
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv('JWT_OIDC_JWKS_CACHE_TIMEOUT'))
        if not JWT_OIDC_JWKS_CACHE_TIMEOUT:
            JWT_OIDC_JWKS_CACHE_TIMEOUT = 300
    except (TypeError, ValueError):
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300

    # NAMEX PROXY Settings
    NAMEX_AUTH_SVC_URL = os.getenv('NAMEX_AUTH_SVC_URL', 'http://')
    NAMEX_SERVICE_CLIENT_USERNAME = os.getenv('NAMEX_SERVICE_CLIENT_USERNAME')
    NAMEX_SERVICE_CLIENT_SECRET = os.getenv('NAMEX_SERVICE_CLIENT_SECRET')

    # service accounts
    ACCOUNT_SVC_AUTH_URL = os.getenv('ACCOUNT_SVC_AUTH_URL')
    ACCOUNT_SVC_CLIENT_ID = os.getenv('ACCOUNT_SVC_CLIENT_ID')
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv('ACCOUNT_SVC_CLIENT_SECRET')
    ACCOUNT_SVC_TIMEOUT = os.getenv('ACCOUNT_SVC_TIMEOUT')

    # legislative timezone for future effective dating
    LEGISLATIVE_TIMEZONE = os.getenv('LEGISLATIVE_TIMEZONE', 'America/Vancouver')

    # Minio configuration values
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_ACCESS_SECRET = os.getenv('MINIO_ACCESS_SECRET')
    MINIO_BUCKET_BUSINESSES = os.getenv('MINIO_BUCKET_BUSINESSES', 'businesses')
    MINIO_SECURE = True

    # determines which year of NAICS data will be used to drive NAICS search
    NAICS_YEAR = int(os.getenv('NAICS_YEAR', '2022'))
    # determines which version of NAICS data will be used to drive NAICS search
    NAICS_VERSION = int(os.getenv('NAICS_VERSION', '1'))

    # Traction ACA-Py tenant settings to issue credentials from
    TRACTION_API_URL = os.getenv('TRACTION_API_URL')
    TRACTION_TENANT_ID = os.getenv('TRACTION_TENANT_ID')
    TRACTION_API_KEY = os.getenv('TRACTION_API_KEY')
    TRACTION_PUBLIC_SCHEMA_DID = os.getenv('TRACTION_PUBLIC_SCHEMA_DID')
    TRACTION_PUBLIC_ISSUER_DID = os.getenv('TRACTION_PUBLIC_ISSUER_DID')

    # Web socket settings
    WS_ALLOWED_ORIGINS = os.getenv('WS_ALLOWED_ORIGINS')

    # Digital Business Card configuration values (required to issue credentials)
    BUSINESS_SCHEMA_NAME = os.getenv('BUSINESS_SCHEMA_NAME')
    BUSINESS_SCHEMA_VERSION = os.getenv('BUSINESS_SCHEMA_VERSION')
    BUSINESS_SCHEMA_ID = os.getenv('BUSINESS_SCHEMA_ID')
    BUSINESS_CRED_DEF_ID = os.getenv('BUSINESS_CRED_DEF_ID')
    WALLET_CRED_DEF_ID = os.getenv('WALLET_CRED_DEF_ID')

    # Cache stuff
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    try:
        CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    except (TypeError, ValueError):
        CACHE_DEFAULT_TIMEOUT = 300

    # MRAS
    MRAS_SVC_URL = os.getenv('MRAS_SVC_URL')
    MRAS_SVC_API_KEY = os.getenv('MRAS_SVC_API_KEY')

    # involuntary dissolution
    STAGE_1_DELAY = int(os.getenv('STAGE_1_DELAY', '42'))
    STAGE_2_DELAY = int(os.getenv('STAGE_2_DELAY', '30'))

    # Transparency Register
    TR_START_DATE = os.getenv('TR_START_DATE', '').strip()  # i.e. '2025-02-01'

    # Pub/Sub
    GCP_AUTH_KEY = os.getenv('GCP_AUTH_KEY', None)
    AUDIENCE = os.getenv(
        'AUDIENCE', 'https://pubsub.googleapis.com/google.pubsub.v1.Subscriber'
    )
    PUBLISHER_AUDIENCE = os.getenv(
        'PUBLISHER_AUDIENCE', 'https://pubsub.googleapis.com/google.pubsub.v1.Publisher'
    )
    SUB_AUDIENCE = os.getenv('SUB_AUDIENCE', '')
    SUB_SERVICE_ACCOUNT = os.getenv('SUB_SERVICE_ACCOUNT', '')
    SBC_CONNECT_GCP_QUEUE_DEBUG = (
        os.getenv('SBC_CONNECT_GCP_QUEUE_DEBUG', 'false').lower() == 'true'
    )
    BUSINESS_EVENTS_TOPIC = os.getenv('BUSINESS_EVENTS_TOPIC', 'business-bn')
    BUSINESS_EMAILER_TOPIC = os.getenv('BUSINESS_EMAILER_TOPIC', 'business-emailer')
    BUSINESS_FILER_TOPIC = os.getenv('BUSINESS_FILER_TOPIC', 'business-filer')

    # NATS / STAN
    NATS_SERVERS = os.getenv('NATS_SERVERS')
    NATS_CLIENT_NAME = os.getenv('NATS_CLIENT_NAME', 'entity.legal_api')
    NATS_CLUSTER_ID = os.getenv('NATS_CLUSTER_ID', 'test-cluster')
    NATS_FILER_SUBJECT = os.getenv('NATS_FILER_SUBJECT', 'entity.filing.filer')
    NATS_ENTITY_EVENT_SUBJECT = os.getenv('NATS_ENTITY_EVENT_SUBJECT', 'entity.events')
    NATS_EMAILER_SUBJECT = os.getenv('NATS_EMAILER_SUBJECT', 'entity.email')
    NATS_QUEUE = os.getenv('NATS_QUEUE', 'entity-filer-worker')

    # Document Service
    DOCUMENT_API_URL = os.getenv('DOCUMENT_API_URL')
    DOCUMENT_API_VERSION = os.getenv('DOCUMENT_API_VERSION')
    DOCUMENT_SVC_URL = ''
    if DOCUMENT_API_URL and DOCUMENT_API_VERSION:
        DOCUMENT_SVC_URL = f'{DOCUMENT_API_URL + DOCUMENT_API_VERSION}/documents'
    DOCUMENT_PRODUCT_CODE = 'BUSINESS'
    DOCUMENT_API_KEY = os.getenv('DOCUMENT_API_KEY')

    TESTING = False
    DEBUG = False


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """reates the Development Config object."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', '')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', '')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    # POSTGRESQL
    if DB_UNIX_SOCKET := os.getenv('DATABASE_UNIX_SOCKET', None):
        SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}'
    else:
        SQLALCHEMY_DATABASE_URI = (
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )

    # URLs
    AUTH_SVC_URL = os.getenv('AUTH_SVC_URL', 'http://test-auth-url')

    # Transparency Register - test cases set this explicitly as needed
    TR_START_DATE = ''

    # JWT OIDC settings
    # JWT_OIDC_TEST_MODE will set jwt_manager to use
    JWT_OIDC_TEST_MODE = True
    JWT_OIDC_TEST_AUDIENCE = 'example'
    JWT_OIDC_TEST_ISSUER = 'https://example.localdomain/auth/realms/example'
    JWT_OIDC_TEST_KEYS = {
        'keys': [
            {
                'kid': 'flask-jwt-oidc-test-client',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',  # noqa: E501
                'e': 'AQAB',
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {
        'keys': [
            {
                'kid': 'flask-jwt-oidc-test-client',
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'n': 'AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR',  # noqa: E501
                'e': 'AQAB',
                'd': 'C0G3QGI6OQ6tvbCNYGCqq043YI_8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhskURaDwk4-8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh_xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0',  # noqa: E501
                'p': 'APXcusFMQNHjh6KVD_hOUIw87lvK13WkDEeeuqAydai9Ig9JKEAAfV94W6Aftka7tGgE7ulg1vo3eJoLWJ1zvKM',
                'q': 'AOjX3OnPJnk0ZFUQBwhduCweRi37I6DAdLTnhDvcPTrrNWuKPg9uGwHjzFCJgKd8KBaDQ0X1rZTZLTqi3peT43s',
                'dp': 'AN9kBoA5o6_Rl9zeqdsIdWFmv4DB5lEqlEnC7HlAP-3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhc',
                'dq': 'ANtbSY6njfpPploQsF9sU26U0s7MsuLljM1E8uml8bVJE1mNsiu9MgpUvg39jEu9BtM2tDD7Y51AAIEmIQex1nM',
                'qi': 'XLE5O360x-MhsdFXx8Vwz4304-MJg-oGSJXCK_ZWYOB_FGXFRTfebxCsSYi0YwJo-oNu96bvZCuMplzRI1liZw',
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_PEM = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDfn1nKQshOSj8xw44oC2klFWSNLmK3BnHONCJ1bZfq0EQ5gIfg
tlvB+Px8Ya+VS3OnK7Cdi4iU1fxO9ktN6c6TjmmmFevk8wIwqLthmCSF3r+3+h4e
ddj7hucMsXWv05QUrCPoL6YUUz7Cgpz7ra24rpAmK5z7lsV+f3BEvXkrUQIDAQAB
AoGAC0G3QGI6OQ6tvbCNYGCqq043YI/8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhs
kURaDwk4+8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh/
xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0CQQD13LrBTEDR44ei
lQ/4TlCMPO5bytd1pAxHnrqgMnWovSIPSShAAH1feFugH7ZGu7RoBO7pYNb6N3ia
C1idc7yjAkEA6Nfc6c8meTRkVRAHCF24LB5GLfsjoMB0tOeEO9w9Ous1a4o+D24b
AePMUImAp3woFoNDRfWtlNktOqLel5PjewJBAN9kBoA5o6/Rl9zeqdsIdWFmv4DB
5lEqlEnC7HlAP+3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhcCQQDb
W0mOp436T6ZaELBfbFNulNLOzLLi5YzNRPLppfG1SRNZjbIrvTIKVL4N/YxLvQbT
NrQw+2OdQACBJiEHsdZzAkBcsTk7frTH4yGx0VfHxXDPjfTj4wmD6gZIlcIr9lZg
4H8UZcVFN95vEKxJiLRjAmj6g273pu9kK4ymXNEjWWJn
-----END RSA PRIVATE KEY-----"""

    # Minio variables
    MINIO_ENDPOINT = 'localhost:9000'
    MINIO_ACCESS_KEY = 'minio'
    MINIO_ACCESS_SECRET = 'minio123'
    MINIO_BUCKET_BUSINESSES = 'businesses'
    MINIO_SECURE = False

    # determines which year of NAICS data will be used to drive NAICS search
    NAICS_YEAR = 2022
    # determines which version of NAICS data will be used to drive NAICS search
    NAICS_VERSION = 1

    LEGAL_API_BASE_URL = 'https://LEGAL_API_BASE_URL/api/v2/businesses'
    PAYMENT_SVC_URL = 'https://PAY_SVC_URL/api/v1/payment-requests'

    BUSINESS_SCHEMA_ID = os.getenv('BUSINESS_SCHEMA_ID', 'TEST_BUSINESS_SCHEMA_ID')
    BUSINESS_CRED_DEF_ID = os.getenv('BUSINESS_CRED_DEF_ID', 'TEST_BUSINESS_SCHEMA_ID')

    TRACTION_API_URL = os.getenv('TRACTION_API_URL', 'https://TRACTION_API_URL')
    TRACTION_TENANT_ID = os.getenv('TRACTION_TENANT_ID', 'TRACTION_TENANT_ID')
    TRACTION_API_KEY = os.getenv('TRACTION_API_KEY', 'TRACTION_API_KEY')
    TRACTION_PUBLIC_SCHEMA_DID = os.getenv('TRACTION_PUBLIC_SCHEMA_DID', 'TRACTION_PUBLIC_SCHEMA_DID')
    TRACTION_PUBLIC_ISSUER_DID = os.getenv('TRACTION_PUBLIC_ISSUER_DID', 'TRACTION_PUBLIC_ISSUER_DID')

    DOCUMENT_API_URL = 'http://document-api.com'
    DOCUMENT_API_VERSION = os.getenv('DOCUMENT_API_VERSION', '/api/v1')
    DOCUMENT_SVC_URL = f'{DOCUMENT_API_URL + DOCUMENT_API_VERSION}/documents'


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print('WARNING: SECRET_KEY being set as a one-shot', file=sys.stderr)

    TESTING = False
    DEBUG = False
