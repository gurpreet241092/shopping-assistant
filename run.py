import base64
import json
from urllib.parse import urlencode

from flask import make_response, redirect, request, jsonify, g
from flask_restful import Api

from flask_app import app
from src.chatGPT.chatbot import get_chat_message_reply

from src.constants import BASE_PREFIX
from src.logging.logging_helper import log_info
from src.prefix_handler import PrefixMiddleware

import openai

from src.resources.product_resource import ProductResource
from src.resources.search_product_resource import SearchProductResource, SearchBulkProductResource
from src.resources.shopify_pull_resource import ShopifyPullResource

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

# To start server as https

# if __name__ == '__main__':
#   context = ('localhost.crt', 'localhost.key')
#   app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=context)
