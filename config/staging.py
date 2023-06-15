import os

from config.default import Config


class StagingConfig(Config):
    ROOT_URL = "https://admin.staging.shop.com"
    FALLBACK_WEBAPP_URL = "https://admin.staging.shop.com"
    PROFILE = "staging"
    TYPESENSE_HOST = "localhost"
    TYPESENSE_PORT = "8108"
