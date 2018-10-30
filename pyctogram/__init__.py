import logging
import os
from urllib.parse import urlparse

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
appLog = logging.getLogger('pyctogram')


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
        login_manager.login_message = ('Veuillez vous connecter ou vous '
                                       'enregistrer pour accéder à cette page')

    if app.debug:
        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy'
                          ).handlers = logging.getLogger('werkzeug').handlers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('flake8').propagate = False
        appLog.setLevel(logging.DEBUG)

    from .model import Account, List, Media, User  # noqa

    from .feed.home import feed_blueprint  # noqa
    from .feed.importer import import_blueprint  # noqa
    from .users.auth import users_blueprint  # noqa
    app.register_blueprint(feed_blueprint)
    app.register_blueprint(import_blueprint)
    app.register_blueprint(users_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.cli.command()
    def dropdb():
        """Empty database for dev environments."""
        filename = urlparse(app.config['SQLALCHEMY_DATABASE_URI']).path[1:]
        if os.path.isfile(filename):
            os.remove(filename)
            print('Database dropped.')

    return app
