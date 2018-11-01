import os
from datetime import datetime

import requests
from flask import (Blueprint, abort, current_app, redirect, render_template,
                   request)
from flask_login import current_user, login_required

from pyctogram import appLog, db
from pyctogram.helpers.redirection import get_redirection
from pyctogram.model import Media

media_blueprint = Blueprint('media', __name__)


@media_blueprint.route("/p/<media_shortcode>")
@login_required
def media(media_shortcode):
    post = Media.query.filter_by(shortcode=media_shortcode).first()
    if not media:
        abort(404)
    return render_template('media/index.html', post=post)


@media_blueprint.route("/memory/", defaults={'page': 1})
@media_blueprint.route("/memory/page/<int:page>")
@login_required
def memory(page):
    per_page = current_app.config['PER_PAGE']
    pagination = current_user.get_media_paginate(page=page,
                                                 per_page=per_page)
    posts = pagination.items
    return render_template('feed/memory.html', posts=posts,
                           pagination=pagination)


@media_blueprint.route("/save/<media_shortcode>")
@login_required
def save(media_shortcode):
    origin = request.args.get('origin', default='')
    media = Media.query.filter_by(shortcode=media_shortcode).first()
    if not media:
        abort(404)

    # Create the filename and download the image
    date = datetime.fromtimestamp(media.timestamp).strftime('%Y-%m-%d_%H-%M')
    filename = f'{date}_{media_shortcode}_{media.account.id}.jpg'
    dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                            str(current_user.id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    destination = os.path.join(dir_path, filename)

    with open(destination, 'wb') as handle:
        response = requests.get(media.display_url, stream=True)
        if not response.ok:
            appLog.error(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

    if media not in current_user.faves:
        current_user.faves.append(media)
        db.session.commit()

    redirection = get_redirection(origin=origin,
                                  media_shortcode=media_shortcode,
                                  media_owner=media.account.account_name)

    return redirect(redirection)


@media_blueprint.route("/forget/<media_shortcode>")
@login_required
def forget(media_shortcode):
    origin = request.args.get('origin', default='')
    media = Media.query.filter_by(shortcode=media_shortcode).first()
    if not media:
        abort(404)

    if media in current_user.faves:
        dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                str(current_user.id))
        date = datetime.fromtimestamp(media.timestamp).strftime(
            '%Y-%m-%d_%H-%M')
        filename = (f'{date}_{media_shortcode}_{media.account.id}'
                    '.jpg')
        target = os.path.join(dir_path, filename)
        if os.path.isfile(target):
            os.remove(target)

        current_user.faves.remove(media)
        db.session.commit()

    redirection = get_redirection(origin=origin,
                                  media_shortcode=media_shortcode,
                                  media_owner=media.account.account_name)

    return redirect(redirection)
