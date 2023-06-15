import logging
import os
from flask import Flask
from flask_login import LoginManager
from flask.logging import default_handler
from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy

from config import load_config
from src.constants import USERS_CACHE
from src.logging.formatter import formatter
# from src.core.cache_manager import get_cache

app = Flask(__name__)
CORS(app)

config = load_config()
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config.from_object(config)
# DB = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

default_handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)


# @login_manager.user_loader
# def load_user(user_id):
#     return get_cache(USERS_CACHE).get(user_id)
