from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_user, logout_user

from pyctogram import db
from pyctogram.model import List, User
from pyctogram.users.forms import LoginForm, RegisterForm

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed.index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Connected as \'{user.username}\'', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('feed.index'))
        else:
            flash(
                'Incorrect login and/or password, please try again.'), 'error'

    return render_template('user/login.html', form=form)


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.flush()

        # feed creation (= default list)
        list_info = current_app.config['DEFAULT_LIST_INFO']
        feed = List(
            user_id=user.id,
            shortname=list_info['shortname'],
            longname=list_info['longname'],
            description=list_info['description'],
        )
        feed.is_default = True
        db.session.add(feed)
        db.session.commit()
        flash(
            'Successfull registration, you can now log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('user/register.html', title='Register', form=form)


@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))
