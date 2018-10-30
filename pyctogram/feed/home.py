from flask import Blueprint, render_template
from flask_login import current_user, login_required

feed_blueprint = Blueprint('feed', __name__)


@feed_blueprint.route("/", defaults={'page': 1})
@feed_blueprint.route("/page/<int:page>")
@login_required
def index(page):
    # Work in progress
    posts = []
    pagination = None
    return render_template('feed/index.html', posts=posts,
                           pagination=pagination)
