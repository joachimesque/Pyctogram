from flask import Blueprint, current_app, render_template
from flask_login import login_required

feed_blueprint = Blueprint('feed', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config[
               'ALLOWED_EXTENSIONS']


@feed_blueprint.route("/", defaults={'page': 1})
@feed_blueprint.route("/page/<int:page>")
@login_required
def index(page):
    # Work in progress
    posts = []
    pagination = None
    return render_template('feed/index.html', posts=posts,
                           pagination=pagination)
