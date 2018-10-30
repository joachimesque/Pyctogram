from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user

from pyctogram import db
from pyctogram.model import User
from pyctogram.users.forms import LoginForm, RegisterForm

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Connecté en tant que \'{}\''.format(user.username))
            next = request.args.get('next')
            return redirect(next or url_for('index'))
        else:
            flash(
                'Login ou mot de passe incorrect, veuillez réessayer.'
            ), 'error'

    return render_template('user/login.html', form=form)


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Vous êtes enregistré.')
        return redirect(url_for('index'))

    return render_template('user/register.html', title='Register', form=form)
