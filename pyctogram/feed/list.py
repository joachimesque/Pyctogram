from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from pyctogram import db
from pyctogram.helpers import forms
from pyctogram.model import List

list_blueprint = Blueprint('list', __name__)


@list_blueprint.route("/lists")
@login_required
def list_lists():
    return render_template('lists/index.html', lists=current_user.lists)


@list_blueprint.route("/list/<shortname>", defaults={'page': 1})
@list_blueprint.route("/list/<shortname>/page/<int:page>")
@login_required
def list_feed(shortname, page):
    the_list = List.query.filter_by(
        user_id=current_user.id, shortname=shortname).first()
    if not the_list:
        abort(404)

    per_page = current_app.config['PER_PAGE']
    pagination = the_list.get_media_paginate(page=page,
                                             per_page=per_page)
    posts = pagination.items
    return render_template('lists/feed.html',
                           the_list=the_list,
                           posts=posts,
                           pagination=pagination)


@list_blueprint.route("/list/<shortname>/edit", methods=['POST', 'GET'])
@login_required
def list_edit(shortname):
    # only the current_user can modify his own lists
    the_list = List.query.filter_by(
        user_id=current_user.id, shortname=shortname).first()
    if not the_list:
        abort(404)

    if request.method == 'POST':
        returned_list, errors = forms.check_list_form(
            request_form=request.form)

        if errors != {}:
            for error in errors.values():
                flash(str(error))
            return render_template('lists/edit.html', errors=errors)

        the_list.shortname = returned_list["shortname"]
        the_list.longname = returned_list["longname"]
        the_list.description = returned_list["description"]
        db.session.commit()
        return redirect(url_for('list.list_accounts',
                                shortname=the_list.shortname))

    return render_template('lists/edit.html', list=the_list)


@list_blueprint.route("/list/<shortname>/accounts")
@login_required
def list_accounts(shortname):
    the_list = List.query.filter_by(
        user_id=current_user.id, shortname=shortname).first()
    if not the_list:
        abort(404)
    return render_template('lists/accounts.html',
                           the_list=the_list,
                           accounts=the_list.accounts)
