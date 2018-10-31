from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required

from pyctogram.model import List, Media

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
    default_list = List.query.filter_by(
        user_id=current_user.id,
        shortname=current_app.config['DEFAULT_LIST_INFO']['shortname']
    ).first()

    if not default_list:
        return render_template('feed/index.html', posts=posts,
                               pagination=pagination)

    posts = default_list.media

    return render_template('feed/index.html', posts=posts,
                           pagination=pagination)
