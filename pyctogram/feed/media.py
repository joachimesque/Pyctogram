from flask import Blueprint, abort, render_template
from flask_login import login_required

from pyctogram.model import Media

media_blueprint = Blueprint('media', __name__)


@media_blueprint.route("/p/<media_shortcode>")
@login_required
def media(media_shortcode):
    post = Media.query.filter_by(shortcode=media_shortcode).first()
    if not media:
        abort(404)
    return render_template('media/index.html', post=post)
