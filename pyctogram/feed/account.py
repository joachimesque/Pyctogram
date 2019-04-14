from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from pyctogram import db
from pyctogram.helpers.redirection import get_redirection
from pyctogram.model import Account, List

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


@account_blueprint.route("/@<account_name>/lists")
@login_required
def profile_lists(account_name):
    account = Account.query.filter_by(account_name=account_name).first()
    if not account:
        abort(404)

    lists = account.user_lists(user_id=current_user.id)

    return render_template('profile/lists.html',
                           author=account,
                           lists=lists)


@account_blueprint.route("/feed/hide/<account_name>")
@login_required
def hide_account(account_name):
    """
    Remove an account from the default list (= feed)
    """
    origin = request.args.get('origin', default='')
    account = Account.query.filter_by(account_name=account_name).first()
    default_list = List.query.filter_by(
        user_id=current_user.id, is_default=True).first()
    if not account or not default_list:
        abort(404)

    if account in default_list.accounts:
        default_list.accounts.remove(account)
        db.session.commit()

    per_page = current_app.config['PER_PAGE']
    # We're gonna transform that one to get the right page.
    media_shortcode = origin.split(':')[1]

    # TODO: calculate new page
    # new_page = l.get_page_number_where_shortcode_is_displayed_in_list(
    # list_id = list_id, media_shortcode = media_shortcode)
    new_page = 1

    origin = origin[:origin.rfind(':') + 1] + str(int(new_page / per_page) + 1)

    redirection = get_redirection(origin=origin,
                                  media_shortcode=media_shortcode,
                                  media_owner=account_name)

    return redirect(redirection)


@account_blueprint.route("/feed/unhide/<account_name>")
@login_required
def show_account(account_name):
    """
    Add an account to the default list (= feed)
    """
    origin = request.args.get('origin', default='')
    account = Account.query.filter_by(account_name=account_name).first()
    default_list = List.query.filter_by(
        user_id=current_user.id, is_default=True).first()
    if not account or not default_list:
        abort(404)

    if account not in default_list.accounts:
        default_list.accounts.append(account)
        db.session.commit()

    if origin[0:7] == 'profile':
        redirection = get_redirection(origin, '')
    else:
        redirection = url_for('feed.list_hidden_accounts')

    return redirect(redirection)
