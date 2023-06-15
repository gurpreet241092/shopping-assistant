from flask import make_response
import json


class ErrorResponse:

    def __init__(self, _type, message, status_code):
        self.type = _type
        self.message = message
        self.status_code = status_code

    def to_response(self):
        if self.status_code is None:
            self.status_code = 200
        return make_response(json.dumps(self.__dict__), self.status_code)


class InvalidResourceException(Exception):
    pass


class InvalidUrlException(Exception):
    pass


class InternalServiceException(Exception):

    def __init__(self, status: int, text: str):
        self.status = status
        self.text = text
