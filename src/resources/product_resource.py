import json

from flask import make_response, request
from flask_login import login_required
from flask_restful import Resource

from flask_app import app
from src.core.error_response import ErrorResponse, InvalidUrlException
from src.search.typesense_client import search_client


class ProductResource(Resource):

    def get(self):
        try:
            export_output = search_client.collections['products'].documents.export()
            single_doc = search_client.collections['products'].documents['1'].retrieve()
            return make_response(json.dumps(export_output), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("BAD_REQUEST", "invalid request", 400).to_response()

    def post(self):
        request_json = json.loads(request.data)
        app.logger.info("Processing request:" + str(request.data))
        try:
            search_client.collections['products'].documents.create(request_json)
            return make_response(json.dumps({}), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while creating product", 500).to_response()

    def put(self):
        request_json = json.loads(request.data)
        app.logger.info("Processing request:" + str(request.data))
        try:
            # Upsert
            search_client.collections['products'].documents.upsert(request_json)
            # Or Update? decide
            search_client.collections['products'].documents[request_json.id].update(request_json)
            return make_response(json.dumps({}), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while creating product", 500).to_response()

    def delete(self):
        request_json = json.loads(request.data)
        app.logger.info("Processing request:" + str(request.data))
        try:
            search_client.collections['product'].documents['1'].delete()
            return make_response("{}", 200)
        except InvalidUrlException as e:
            return ErrorResponse("INVALID_URL", "invalid url for fetching catalog", 400).to_response()
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while fetching catalog", 500).to_response()
