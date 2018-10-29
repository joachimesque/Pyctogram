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


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = 'development key'
