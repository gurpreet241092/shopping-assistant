import typesense

from flask_app import app

host = app.config["TYPESENSE_HOST"]
port = app.config["TYPESENSE_PORT"]

search_client = typesense.Client({
    'nodes': [{
        'host': host,  # For Typesense Cloud use xxx.a1.typesense.net
        'port': port,       # For Typesense Cloud use 443
        'protocol': 'http'    # For Typesense Cloud use https
    }],
    'api_key': 'xyz',
    'connection_timeout_seconds': 2
})