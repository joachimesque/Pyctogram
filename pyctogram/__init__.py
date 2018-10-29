import logging
import os
from urllib.parse import urlparse

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
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

    if app.debug:
        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy'
                          ).handlers = logging.getLogger('werkzeug').handlers
        logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
        logging.getLogger('flake8').propagate = False
        appLog.setLevel(logging.DEBUG)

    from .model import Account, List, Media, User  # noqa

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return render_template('404.html'), 404

    @app.route("/")
    def index():
        return 'rewriting in progress'

    @app.cli.command()
    def dropdb():
        """Empty database for dev environments."""
        filename = urlparse(app.config['SQLALCHEMY_DATABASE_URI']).path[1:]
        if os.path.isfile(filename):
            os.remove(filename)
            print('Database dropped.')

    return app
