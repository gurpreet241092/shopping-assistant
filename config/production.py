import os

from config.default import Config


class ProductionConfig(Config):
    ROOT_URL = "https://admin.shop.com"
    FALLBACK_WEBAPP_URL = "https://admin.shop.com"
    PROFILE = "prod"
    TYPESENSE_HOST = "localhost"
    TYPESENSE_PORT = "8108"
