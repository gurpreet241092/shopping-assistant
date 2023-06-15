import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

class Config:
    OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
    ROOT_URL = "https://localhost:5000"
    FALLBACK_WEBAPP_URL = "https://localhost:3000"
    PROFILE = "dev"
    TYPESENSE_HOST = "localhost"
    TYPESENSE_PORT = "8108"
    SHOPIFY_TOKEN = os.getenv('SHOPIFY_TOKEN')
    SHOPIFY_MERCHANT = os.getenv('SHOPIFY_MERCHANT')


