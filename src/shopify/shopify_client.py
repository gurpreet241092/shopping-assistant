import json

import shopify
import os

from flask_app import app
from src.search.typesense_client import search_client

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

SHOPIFY_TOKEN = app.config["SHOPIFY_TOKEN"]
SHOPIFY_MERCHANT = app.config["SHOPIFY_MERCHANT"]

if SHOPIFY_TOKEN is None:
    SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN")
    SHOPIFY_MERCHANT = os.getenv("SHOPIFY_MERCHANT")

# Find other ways to set session
# api_session = shopify.Session(merchant, "", token)
# shopify.Session.setup(api_key=API_KEY, secret=SHARED_SECRET)

# shopify.ShopifyResource.activate_session(api_session)


def get_data(object_name):
    all_data = []
    attribute = getattr(shopify, object_name)
    data = attribute.find(since_id=0, limit=20)
    for row in data:
        all_data.append(row.to_dict())
    while data.has_next_page() and False:
        data = data.next_page()
        for row in data:
            all_data.append(row.to_dict())
    return all_data


def get_product_id(product_merchant, product_id):
    return str(f"{product_merchant}_{product_id}")


def map_shopify_product(product):
    p = product.to_dict()
    product_merchant = "sahiltraders"
    p["merchant"] = product_merchant
    p["id"] = get_product_id(product_merchant, p["id"])
    for variant in p["variants"]:
        for opt_index, opt in enumerate(p["options"]):
            variant[opt["name"]] = variant[f"option{opt_index + 1}"]
    return p


def save_shopify_products(data):
    json_string_list = list(map(map_shopify_product, data))
    # json_string = "\n".join(map(json.dumps, json_string_list))
    # print(json_string)
    search_client.collections['product'].documents.import_(json_string_list, {"action": "upsert"})


def get_and_save_product():
    object_name = 'Product'
    attribute = getattr(shopify, object_name)
    data = attribute.find(since_id=0, limit=20)
    save_shopify_products(data)
    counter = 1
    while data.has_next_page():
        counter = counter + 1
        print(f"Counter: {counter}")
        data = data.next_page()
        save_shopify_products(data)
    return counter


if __name__ == '__main__':
    # p: shopify.resources.product.Product = shopify.Product()
    api_session = shopify.Session(SHOPIFY_MERCHANT, "2023-04", SHOPIFY_TOKEN)
    shopify.ShopifyResource.activate_session(api_session)
    #
    # retrieve_all_response = search_client.collections.retrieve()
    # print(retrieve_all_response)
    # print("\n\n")


    # get_and_save_product()

    retrieve_all_response = search_client.collections.retrieve()
    print(retrieve_all_response)
    print("\n\n")

    print(search_client.collections['product'].documents.search({
        "filter_by": "variants.color:[black,pink]",
        "q": "dresses girls",
        "query_by": "title, tags, body_html",
        "per_page": 10
    }))

    # export_output = search_client.collections['product'].documents.export()
    # print(export_output)

    # p = shopify.Product.find(8326529909032)
    # p2 = p.to_dict()
    # p2["merchant"] = "sahiltraders"
    # print(p2)
    #
    # print(map_shopify_product(p))


    # products = get_data('Product')
    # print(products)
    # print(len(products))
    # for p in products[0:2]:
    #     print(json.dumps(p.to_dict()))
    # # List all the things available at shopify.
    # all_directory = dir(shopify)
    # print(all_directory)
