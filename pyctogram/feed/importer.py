import json
import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from pyctogram.helpers.import_accounts import create_accounts

import_blueprint = Blueprint('importer', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config[
               'ALLOWED_EXTENSIONS']


def import_contacts_from_file(request, type):
    total = 0
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                str(current_user.id))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, filename)
        file.save(file_path)

        with open(file_path, 'r') as f:
            if type == 'json':
                contacts_to_import = json.loads(f.read().splitlines()[0])
                contacts_to_import = list(
                    contacts_to_import['following'].keys())
            else:
                contacts_to_import = f.read().splitlines()

            if not contacts_to_import:
                flash('No contact to import')
                return redirect(request.url)

            default_list_info = current_app.config['DEFAULT_LIST_INFO']
            total = create_accounts(contacts_to_import, current_user,
                                    default_list_info)
    return total


@import_blueprint.route("/import/json", methods=['POST', 'GET'])
@login_required
def import_from_json():
    if request.method == 'POST':
        total, not_imported = import_contacts_from_file(request, 'json')
        if not_imported:
            accounts_list = ', '.join(not_imported)
            flash('Errors were encountered for the following accounts:'
                  f' {accounts_list}', 'error')
        return redirect(
            url_for('importer.import_done', import_count=total))
    return render_template('import/json.html')


@import_blueprint.route("/import/text", methods=['POST', 'GET'])
@login_required
def import_from_text():
    if request.method == 'POST':
        total, not_imported = import_contacts_from_file(request, 'text')
        if not_imported:
            accounts_list = ', '.join(not_imported)
            flash('Errors were encountered for the following accounts:'
                  f' {accounts_list}', 'error')
        return redirect(
            url_for('importer.import_done', import_count=total))
    return render_template('import/text.html')


@import_blueprint.route("/import", methods=['POST', 'GET'])
@login_required
def import_from_form():
    if request.method == 'POST':

        if request.form['contacts'] == '':
            flash('Please fill in the text area before clicking the button.')
            return render_template('import/form.html',
                                   errors='The text area should not be empty.')

        contacts_to_import = request.form['contacts'].splitlines()

        default_list_info = current_app.config['DEFAULT_LIST_INFO']
        total, not_imported = create_accounts(contacts_to_import, current_user,
                                              default_list_info)
        if not_imported:
            accounts_list = ', '.join(not_imported)
            flash('Errors were encountered for the following accounts:'
                  f' {accounts_list}', 'error')
        return redirect(url_for('importer.import_done', import_count=total))

    return render_template('import/form.html')


@import_blueprint.route("/import/done")
@login_required
def import_done():
    import_count = request.args['import_count']
    return render_template('import/done.html', import_count=import_count)
