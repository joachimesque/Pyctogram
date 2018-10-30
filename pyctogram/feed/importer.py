import json
import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from pyctogram import db
from pyctogram.helpers.importer import get_account_data
from pyctogram.model import Account, List

import_blueprint = Blueprint('importer', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config[
               'ALLOWED_EXTENSIONS']


@import_blueprint.route("/import/json", methods=['POST', 'GET'])
@login_required
def import_from_json():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'r') as f:
                contacts_to_import = json.loads(f.read().splitlines()[0])
                contacts_to_import = list(
                    contacts_to_import['following'].keys())

                if not contacts_to_import:
                    flash('No contact to import')
                    return redirect(request.url)

                total = 0
                default_list_info = current_app.config['DEFAULT_LIST_INFO']
                headers = current_app.config['DEFAULT_HEADERS']
                contacts_not_ok = []

                for contact in contacts_to_import:
                    account = Account.query.filter_by(
                        account_name=contact).first()
                    if not account:
                        account_data = get_account_data(contact, headers)

                        if not account_data:
                            contacts_not_ok.append(account)
                            continue

                        account = Account(id=account_data["id"],
                                          account_name=account_data["username"])  # noqa
                        account.full_name = account_data["full_name"]
                        account.biography = account_data["biography"]
                        account.profile_pic_url = account_data[
                            "profile_pic_url"]
                        account.profile_pic_url_hd = account_data[
                            "profile_pic_url_hd"]
                        account.external_url = account_data["external_url"]
                        account.external_url_linkshimmed = account_data[
                            "external_url_linkshimmed"]
                        account.followed_by = account_data["edge_followed_by"][
                            "count"]
                        account.follow = account_data["edge_follow"]["count"]
                        account.last_updated = 0
                        account.is_private = int(account_data["is_private"])
                        db.session.add(account)

                    default_list = List.query.filter_by(
                        user_id=current_user.id,
                        shortname=default_list_info['shortname']
                    ).first()

                    if not default_list:
                        default_list = List(
                            user_id=current_user.id,
                            shortname=default_list_info['shortname'],
                            longname=default_list_info['longname'],
                            description=default_list_info['description'],
                        )
                        db.session.add(default_list)

                    if account not in current_user.accounts:
                        current_user.accounts.append(account)
                        total += 1

                    if account not in default_list.accounts:
                        default_list.accounts.append(account)

                db.session.commit()

            return redirect(
                url_for('importer.import_success', import_count=total,
                        contacts_not_ok=contacts_not_ok))

    return render_template('import/json.html')


@import_blueprint.route("/import/success")
@login_required
def import_success():
    import_count = request.args['import_count']
    return render_template('import/success.html', import_count=import_count)
