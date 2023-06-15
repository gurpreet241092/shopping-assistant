import json
import shopify
from flask import make_response, request
from flask_login import login_required
from flask_restful import Resource

from flask_app import app
from src.core.error_response import ErrorResponse
from src.shopify.shopify_client import get_data


class ShopifyPullResource(Resource):

    def post(self):
        app.logger.info("Processing request:" + str(request.data))
        request_json = json.loads(request.data)
        request_json = {
            'tenant_code': 'abc'
        }
        try:
            products = get_data('Product')
            print(products)
            # List all the things available at shopify.
            all_directory = dir(shopify)
            print(all_directory)
            app.logger.info(f"Response of Search:")
            return make_response(json.dumps({}), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while searching product", 500).to_response()

