from src.search.typesense_client import search_client

product_schema = {
    'name': 'product',
    "enable_nested_fields": True,
    'fields': [
        {'name': '.*', 'type': 'auto'}
    ]
}
# search_client.collections['product'].delete()
# search_client.collections.create(product_schema)
