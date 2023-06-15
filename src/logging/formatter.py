import logging
from flask import g, has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.remote_addr = request.remote_addr
        else:
            record.remote_addr = "-"

        if g.__contains__("username"):
            record.username = g.username
        else:
            record.username = "-"

        return super().format(record)


formatter = RequestFormatter("%(remote_addr)s [%(asctime)s] [%(username)s] %(levelname)s in %(module)s: %(message)s")
