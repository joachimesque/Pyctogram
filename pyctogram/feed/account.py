from flask import Blueprint, abort, current_app, render_template, request
from flask_login import login_required

from pyctogram.model import Account

account_blueprint = Blueprint('account', __name__)


@account_blueprint.route("/@<account_name>", defaults={'page': 1})
@account_blueprint.route("/@<account_name>/page/<int:page>")
@login_required
def profile(account_name, page):
    display_as_feed = False
    if request.args.get('display') == 'feed':
        display_as_feed = True

    account = Account.query.filter_by(account_name=account_name).first()
    if not account:
        abort(404)
    per_page = current_app.config['PER_PAGE']
    pagination = account.get_media_paginate(page=page,
                                            per_page=per_page)
    posts = pagination.items
    return render_template('profile/index.html',
                           author=account,
                           posts=posts,
                           pagination=pagination,
                           display_as_feed=display_as_feed)
