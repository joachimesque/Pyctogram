from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required

from pyctogram.model import List

feed_blueprint = Blueprint('feed', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config[
               'ALLOWED_EXTENSIONS']


@feed_blueprint.route("/", defaults={'page': 1})
@feed_blueprint.route("/page/<int:page>")
@login_required
def index(page):
    posts = []
    pagination = None
    per_page = current_app.config['PER_PAGE']
    default_list = List.query.filter_by(
        user_id=current_user.id,
        is_default=True
    ).first()

    if default_list:
        pagination = default_list.get_media_paginate(page=page,
                                                     per_page=per_page)
        posts = pagination.items

    return render_template('feed/index.html', posts=posts,
                           pagination=pagination)
