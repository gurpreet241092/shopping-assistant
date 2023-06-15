import json

from flask import make_response, request
from flask_login import login_required
from flask_restful import Resource

from flask_app import app
from src.core.error_response import ErrorResponse
from src.search.typesense_client import search_client


class SearchProductResource(Resource):

    def post(self):
        app.logger.info("Processing request:" + str(request.data))
        request_json = json.loads(request.data)
        request_json = {
            'q': 'hunger',
            'query_by': 'title',
            'sort_by': 'ratings_count:desc'
        }
        try:
            output = search_client.collections['product'].documents.search(request_json)
            app.logger.info(f"Response of Search: {output}")
            return make_response(json.dumps(output), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while searching product", 500).to_response()



class SearchBulkProductResource(Resource):

    def post(self):
        app.logger.info("Processing request:" + str(request.data))
        request_json = json.loads(request.data)
        query_list = request_json["queryList"]
        collection_filter = request_json["collection_filter"]
        query_list = [
            {
                'q': 'hunger',
                'query_by': 'title',
            },
            {
                'q': 'suzanne',
                'query_by': 'authors',
            }
        ]
        collection_filter = {'collection': 'product', 'sort_by': 'ratings_count:desc'}
        try:
            output = search_client.multi_search.perform({'searches': query_list}, collection_filter)
            app.logger.info(f"Response of bulk search: {output}")
            return make_response(json.dumps(output), 200)
        except Exception as e:
            app.logger.info(e)
            return ErrorResponse("INTERNAL_ERROR", "internal error while bulk searching product", 500).to_response()
