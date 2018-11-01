from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from pyctogram import db
from pyctogram.helpers import forms
from pyctogram.helpers.redirection import get_redirection
from pyctogram.model import Account, List

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


@list_blueprint.route("/list/create", methods=['POST', 'GET'],
                      defaults={'account_name' : ''})
@list_blueprint.route("/list/create/autoadd/<account_name>",
                      methods=['POST', 'GET'])
@login_required
def list_create(account_name):
    origin = request.args.get('origin', default='')

    if request.method == 'POST':

        origin = request.args.get('origin', default='')
        new_list_data, errors = forms.check_list_form(request_form=request.form)

        if errors != {}:
            for error in errors.values():
                flash(str(error))
            return redirect(url_for('list.list_create',
                                    shortname=new_list_data['shortname'],
                                    account_name=account_name))

        new_list = List(user_id=current_user.id,
                        shortname=new_list_data['shortname'],
                        longname=new_list_data['longname'],
                        description=new_list_data['description'])
        db.session.add(new_list)
        db.session.commit()

        if account_name != '':
            return redirect(url_for('list.list_add_user',
                                    shortname=new_list_data['shortname'],
                                    account_name=account_name,
                                    origin=origin))
        else:
            return redirect(url_for('list.list_accounts',
                                    shortname=new_list_data['shortname']))

    return render_template('lists/create.html', account_name=account_name,
                           origin=origin)


@list_blueprint.route("/list/<shortname>/add/<account_name>")
@login_required
def list_add_user(shortname, account_name):
    origin = request.args.get('origin', default='')

    the_list = List.query.filter_by(shortname=shortname).first()
    account = Account.query.filter_by(account_name=account_name).first()
    if not account or not the_list:
        abort(404)

    if account not in the_list.accounts:
        the_list.accounts.append(account)
        db.session.commit()

    if origin == '':
        redirection = url_for('list.list_feed', shortname=shortname)
    else:
        redirection = get_redirection(origin=origin,
                                      media_shortcode='',
                                      media_owner=account_name)
    return redirect(redirection)


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


@list_blueprint.route("/list/<shortname>/delete", methods=["GET", "POST"])
@login_required
def list_delete(shortname):
    if request.method == 'POST':
        if request.form['submit'] == 'submit':
            # only the current_user can delet his own lists
            the_list = List.query.filter_by(
                user_id=current_user.id, shortname=shortname).first()
            if not the_list:
                abort(404)
            db.session.delete(the_list)
            db.session.commit()
            return redirect(url_for('list.list_lists'))

    flash('Are you sure you want to delete this list? '
          'There is no turning back.')
    return render_template('lists/confirm.html', shortname=shortname)


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
