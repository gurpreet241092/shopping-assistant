import base64
import json
import traceback
from urllib.parse import urlencode

from flask import make_response, redirect, request, jsonify, g
from flask_restful import Api

from flask_app import app
from src.chatGPT.chatbot import get_chat_message_reply

from src.constants import BASE_PREFIX
from src.core.error_response import ErrorResponse
from src.logging.logging_helper import log_info
from src.models.product import product_schema
from src.prefix_handler import PrefixMiddleware

import openai
from typesense.exceptions import ObjectNotFound

from src.resources.product_resource import ProductResource
from src.resources.search_product_resource import SearchProductResource, SearchBulkProductResource
from src.resources.shopify_pull_resource import ShopifyPullResource
from src.search.typesense_client import search_client, extract_product_from_documents

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=BASE_PREFIX)

openai.api_key = app.config["OPEN_AI_API_KEY"]
# log_info(app.config["OPEN_AI_API_KEY"])

api = Api(app)
api.add_resource(ProductResource, "/products")
api.add_resource(SearchProductResource, "/search-products")
api.add_resource(SearchBulkProductResource, "/search-products/bulk")
api.add_resource(ShopifyPullResource, "/shopify/pull")


@app.route("/chat/<chat_id>", methods=['POST'])
def chat(chat_id):
    # log_info(f"Chat Id received: {chat_id}")
    log_info(str(request.data))
    data = json.loads(request.data)
    log_info(f"Body: {json.dumps(data)}")

    response = get_chat_message_reply(chat_id, data["prompt"])
    return make_response(response, 200)

@app.route("/chat-products/<chat_id>", methods=['POST'])
def chat_products(chat_id):
    # log_info(f"Chat Id received: {chat_id}")
    log_info(str(request.data))
    data = json.loads(request.data)
    log_info(f"Body: {json.dumps(data)}")

    response = get_chat_message_reply(chat_id, data["prompt"])
    query_string_value = "query"
    query_string_value = "keywords"
    try:
        request_json = json.loads(response)
        query = request_json[query_string_value] if request_json[query_string_value] != "" else "*"
        all_filters = []
        # Tags
        if len(request_json["tags"]) > 0 and False:
            tag_string = ",".join(list(request_json["tags"]))
            # all_filters.append(f"tags:[{tag_string}]")
            query = f"{tag_string}, {query}"

        # Filters
        final_filter = {}
        # if len(request_json["filters"]) > 0:
        #     for filter_object in list(request_json["filters"]):
        #         for key in filter_object:
        #             if key not in ["color", "size"]:
        #                 continue
        #             if type(filter_object[key]) == list:
        #                 string_value = ",".join(filter_object[key])
        #             else:
        #                 string_value = str(filter_object[key])
        #             all_filters.append(f"variants.{key}:[{string_value}]")

        if len(request_json["filters"]) > 0:
            for filter_object in list(request_json["filters"]):
                for key in filter_object:
                    app.logger.info(f"query: {query}")
                    app.logger.info(f"key: {key}")
                    app.logger.info(f"filter_object: {filter_object}")
                    if key not in ["color", "size"]:
                        continue
                    # Remove the color thing from query string
                    query.replace(key, "")
                    final_filter[key] = [] if key not in final_filter else final_filter[key]
                    if type(filter_object[key]) == list:
                        final_filter[key] = final_filter[key] + filter_object[key]
                        # Replace the filter values from query string
                        for item in filter_object[key]:
                            query.replace(item, "")
                    else:
                        final_filter[key].append(str(filter_object[key]))
                        query.replace(str(filter_object[key]), "")
                    app.logger.info(f"query after: {query}")

        for key in final_filter:
            value = ",".join(final_filter[key])
            all_filters.append(f"variants.{key}:[{value}]")

        app.logger.info(all_filters)
        request_object = {
            'q': query.strip(),
            'query_by': 'title, tags, body_html',
            'filter_by': " && ".join(all_filters),
            'per_page': 35
        }
        app.logger.info(request_object)
        # search_response = search_client.collections['product'].documents.search(request_object)
        # product_details = list(map(extract_product_from_documents, search_response["hits"]))
        return make_response({
            "openai_response": request_json,
            "user_response": request_json["responseForUser"],
            "search_query": request_object,
            # "count": search_response["found"],
            # "product_details": product_details,
            # "response": response
        }, 200)
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
        return ErrorResponse("INTERNAL_ERROR", "internal error while searching product", 500).to_response()


@app.route("/health")
def health():
    return make_response("{}", 200)


# @app.route("/user")
# @token_required
# def user_details():
#     user = {'name': g.email, 'email': g.email, 'userRole': g.user_role}
#     return make_response(json.dumps(user))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    try:
        retrieve_response = search_client.collections['product'].retrieve()
        app.logger.info(retrieve_response)
    except ObjectNotFound as onf:
        search_client.collections.create(product_schema)


# To start server as https

# if __name__ == '__main__':
#   context = ('localhost.crt', 'localhost.key')
#   app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=context)
