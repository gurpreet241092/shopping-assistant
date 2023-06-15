from flask_app import app


def log_info(msg):
    app.logger.info(msg)


def log_error(msg):
    app.logger.error(msg)
