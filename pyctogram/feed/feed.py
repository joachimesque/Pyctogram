from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, url_for)
from flask_login import current_user, login_required

from pyctogram.helpers.import_accounts import update_media
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


@feed_blueprint.route("/feed/hidden-accounts")
@login_required
def list_hidden_accounts():
    hidden_accounts = []
    default_list = List.query.filter_by(
        user_id=current_user.id,
        is_default=True
    ).first()

    if not default_list:
        abort(404)
    for account in current_user.accounts:
        if account not in default_list.accounts:
            hidden_accounts.append(account)
    return render_template('feed/hidden.html', accounts=hidden_accounts)


@feed_blueprint.route("/feed/update-feed")
@login_required
def update_feed():
    default_list = List.query.filter_by(
        user_id=current_user.id,
        is_default=True
    ).first()

    failed_accounts = update_media(list_id=default_list.id)
    if failed_accounts:
        accounts_list = ', '.join(failed_accounts)
        flash('Errors were encountered for the following accounts:'
              f' {accounts_list}', 'error')

    return redirect(url_for('feed.index'))
