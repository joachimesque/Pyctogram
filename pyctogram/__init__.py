import json
import logging
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

log_file = os.getenv('APP_LOG')
logging.basicConfig(filename=log_file,
                    format=('%(asctime)s - %(name)s - %(levelname)s - '
                            '%(message)s'),
                    datefmt='%Y/%m/%d %H:%M:%S')
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
appLog = logging.getLogger('pyctogram')


def smart_truncate(content, length=100, suffix='…'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    with app.app_context():
        app_settings = os.getenv('APP_SETTINGS')
        app.config.from_object(app_settings)

        # set up extensions
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        login_manager.login_view = 'users.login'

    if app.debug:
        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy'
                          ).handlers = logging.getLogger('werkzeug').handlers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('flake8').propagate = False
        appLog.setLevel(logging.DEBUG)

    from .model import Account, List, Media, User  # noqa

    from .feed.account import account_blueprint  # noqa
    from .feed.feed import feed_blueprint  # noqa
    from .feed.importer import import_blueprint  # noqa
    from .feed.list import list_blueprint  # noqa
    from .feed.media import media_blueprint  # noqa
    from .users.auth import users_blueprint  # noqa
    app.register_blueprint(account_blueprint)
    app.register_blueprint(feed_blueprint)
    app.register_blueprint(import_blueprint)
    app.register_blueprint(list_blueprint)
    app.register_blueprint(media_blueprint)
    app.register_blueprint(users_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.template_filter()
    def json_loads(data):
        return json.loads(data)

    @app.template_filter()
    def format_timestamp(ts, date_format='%Y-%m-%d'):
        return datetime.fromtimestamp(ts).strftime(date_format)

    @app.template_filter()
    def thumbnail_320(thumbnails):
        return json.loads(thumbnails)[3]['src']

    @app.template_filter()
    def parse_text(text):
        text = smart_truncate(text, length=180)
        caption = re.sub(
            r'(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])',
            r'<a href="\1" target="_blank">\1</a>', text)
        caption = re.sub(r'(\A|\s)@(\w+)',
                       r'\1@<a href="http://www.instagram.com/\2">\2</a>',
                         caption)
        caption = re.sub(r'(\A|\s)#(\w+)',
                       r'\1#<a href="https://www.instagram.com/explore/tags/\2/">\2</a>',
                         caption)
        return caption

    @app.template_global()
    def account_is_hidden(account, current_user):
        """Check if an account is in the current user feed (= default list)."""
        default_list = List.query.filter_by(
            user_id=current_user.id, is_default=True).first()
        return account not in default_list.accounts

    @app.template_global()
    def registration_is_allowed():
        return os.getenv('ALLOW_REGISTRATION') == 'true'

    @app.cli.command()
    def dropdb():
        """Empty database for dev environments."""
        filename = urlparse(app.config['SQLALCHEMY_DATABASE_URI']).path[1:]
        if os.path.isfile(filename):
            os.remove(filename)
            print('Database dropped.')

    @app.cli.command()
    def update():
        """Update media for all accounts"""
        from .helpers.import_accounts import update_media
        failed_accounts = update_media()
        if failed_accounts:
            accounts_list = ', '.join(failed_accounts)
            print('Update done. Errors were encountered for the following '
                  f'accounts: {accounts_list} (see logs for more information)')
        else:
            print('Update done.')

    return app
