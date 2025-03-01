# Copyright © 2023 Province of British Columbia
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
import random

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'legal_api.config.DevConfig',
    'testing': 'legal_api.config.TestConfig',
    'production': 'legal_api.config.ProdConfig',
    'default': 'legal_api.config.ProdConfig'
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


class _Config():  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    # used to identify versioning flag
    SERVICE_NAME = 'digital-credentials'
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SENTRY_DSN = os.getenv('SENTRY_DSN') or ''
    SENTRY_DSN = '' if SENTRY_DSN.lower() == 'null' else SENTRY_DSN
    LD_SDK_KEY = os.getenv('LD_SDK_KEY', None)

    # variables
    LEGISLATIVE_TIMEZONE = os.getenv(
        'LEGISLATIVE_TIMEZONE', 'America/Vancouver')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # POSTGRESQL
    DB_USER = os.getenv('ENTITY_DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('ENTITY_DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('ENTITY_DATABASE_NAME', '')
    DB_HOST = os.getenv('ENTITY_DATABASE_HOST', '')
    DB_PORT = os.getenv('ENTITY_DATABASE_PORT', '5432')
    # pylint: disable=consider-using-f-string
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )

    NATS_CONNECTION_OPTIONS = {
        'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
        'name': os.getenv('NATS_CLIENT_NAME', 'entity.filing.worker')

    }
    STAN_CONNECTION_OPTIONS = {
        'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
        'client_id': str(random.SystemRandom().getrandbits(0x58)),
        'ping_interval': 1,
        'ping_max_out': 5,
    }

    SUBSCRIPTION_OPTIONS = {
        'subject': os.getenv('NATS_ENTITY_EVENT_SUBJECT', 'entity.events'),
        'queue': os.getenv('NATS_QUEUE', 'error'),
        'durable_name': os.getenv('NATS_QUEUE', 'error') + '_durable',
    }

    ENTITY_EVENT_PUBLISH_OPTIONS = {
        'subject': os.getenv('NATS_ENTITY_EVENT_SUBJECT', 'entity.events'),
    }

    # Traction ACA-Py tenant settings to issue credentials from
    TRACTION_API_URL = os.getenv('TRACTION_API_URL')
    TRACTION_TENANT_ID = os.getenv('TRACTION_TENANT_ID')
    TRACTION_API_KEY = os.getenv('TRACTION_API_KEY')
    TRACTION_PUBLIC_SCHEMA_DID = os.getenv('TRACTION_PUBLIC_SCHEMA_DID')
    TRACTION_PUBLIC_ISSUER_DID = os.getenv('TRACTION_PUBLIC_ISSUER_DID')

    # Digital Business Card configuration values (required to issue credentials)
    BUSINESS_SCHEMA_NAME = os.getenv('BUSINESS_SCHEMA_NAME')
    BUSINESS_SCHEMA_VERSION = os.getenv('BUSINESS_SCHEMA_VERSION')
    BUSINESS_SCHEMA_ID = os.getenv('BUSINESS_SCHEMA_ID')
    BUSINESS_CRED_DEF_ID = os.getenv('BUSINESS_CRED_DEF_ID')


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Creates the Development Config object."""

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
    DEPLOYMENT_ENV = 'testing'
    # pylint: disable=consider-using-f-string
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    TESTING = False
    DEBUG = False
