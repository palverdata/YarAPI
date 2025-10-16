from os import getenv
import os
from typing import Protocol

from dotenv import load_dotenv


class ConfigProtocol(Protocol):
    """A protocol that defines the attributes of the Config class.

    This is used to type hint the Config class.
    """

    solr9_username: str
    solr9_password: str
    solr9_base_url: str
    socialdata_api_key: str
    concurrency: int

    debug: bool
    ensemble_api_key: str
    apify_key: str
    serp_key: str
    mongo_url: str
    mongo_db_name: str

    nucleus_base_url: str
    nucleus_client_id: str
    nucleus_service_account: str

    app_proxy_url: str

    short_backoff_log: bool

    cache_ttl_seconds: int


class Config(ConfigProtocol):
    """A class that loads environment variables
    and exposes them as attributes."""

    def __init__(self):
        load_dotenv()

    def __getattr__(self, name):
        return getenv(name.upper())

    @property
    def concurrency(self) -> int:
        return int(getenv("CONCURRENCY", 2))

    @property
    def debug(self) -> bool:
        return bool(int(getenv("DEBUG", 1)))

    @property
    def ensemble_api_key(self) -> str:
        return getenv("ENSEMBLE_API_KEY")

    @property
    def apify_key(self) -> str:
        return getenv("APIFY_KEY")

    @property
    def mongo_url(self) -> str:
        return getenv("MONGO_URL", "mongodb://localhost:27017")

    @property
    def mongo_db_name(self) -> str:
        return getenv("MONGO_DB_NAME", "olho_gordo")

    @property
    def nats_batch_size(self) -> int:
        return int(getenv("NATS_BATCH_SIZE", 1))

    @property
    def nucleus_base_url(self) -> str:
        return getenv("NUCLEUS_BASE_URL", "https://nucleus.anax.com.br")

    @property
    def nucleus_client_id(self) -> str:
        return getenv("NUCLEUS_CLIENT_ID", "sentinel")

    @property
    def nucleus_service_account(self) -> str:
        return getenv("NUCLEUS_SERVICE_ACCOUNT", "sentinel")

    @property
    def app_proxy_url(self) -> str:
        return getenv("APP_PROXY_URL")

    @property
    def short_backoff_log(self) -> bool:
        return bool(int(getenv("SHORT_BACKOFF_LOG", 0)))

    @property
    def serp_key(self) -> str:
        return getenv("SERP_KEY")

    @property
    def secret_key(self) -> str:
        key = os.getenv("SECRET_KEY")
        if not key:
            print(
                "WARNING: SECRET_KEY environment variable not set. Using a temporary key."
            )
            print(
                "Please set a strong, persistent SECRET_KEY in your .env file for production."
            )
            key = os.urandom(32).hex()
        return key

    @property
    def cache_ttl_seconds(self) -> int:
        return int(getenv("CACHE_TTL_SECONDS", 60))


config = Config()
