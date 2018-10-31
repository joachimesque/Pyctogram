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
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename)
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
            headers = current_app.config['DEFAULT_HEADERS']

            total = create_accounts(contacts_to_import, current_user,
                                    headers, default_list_info)
    return total


@import_blueprint.route("/import/json", methods=['POST', 'GET'])
@login_required
def import_from_json():
    if request.method == 'POST':
        total = import_contacts_from_file(request, 'json')
        return redirect(
            url_for('importer.import_success', import_count=total))
    return render_template('import/json.html')


@import_blueprint.route("/import/text", methods=['POST', 'GET'])
@login_required
def import_from_text():
    if request.method == 'POST':
        total = import_contacts_from_file(request, 'text')
        return redirect(
            url_for('importer.import_success', import_count=total))
    return render_template('import/text.html')


@import_blueprint.route("/import/success")
@login_required
def import_success():
    import_count = request.args['import_count']
    return render_template('import/success.html', import_count=import_count)
