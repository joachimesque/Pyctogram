import os

from flask import current_app


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        current_app.root_path, 'uploads'
    )
    ALLOWED_EXTENSIONS = {'txt', 'json'}
    DEFAULT_USER_ID = 1
    DEFAULT_LIST_INFO = {'shortname': '_feed',
                         'longname': 'Feed',
                         'description': 'Default Feed List'}
    DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'}  # noqa


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = 'development key'
