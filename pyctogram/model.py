import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from pyctogram import db

accounts2lists = db.Table(
    'acccounts2lists',
    db.Column('list_id',
              db.Integer,
              db.ForeignKey('lists.id'), primary_key=True),
    db.Column('account_id',
              db.Integer,
              db.ForeignKey('accounts.id'), primary_key=True),
    db.Column('date_added', db.DateTime, default=datetime.datetime.utcnow())
)

accounts2users = db.Table(
    'acccounts2users',
    db.Column('user_id',
              db.Integer,
              db.ForeignKey('users.id'), primary_key=True),
    db.Column('account_id',
              db.Integer,
              db.ForeignKey('accounts.id'), primary_key=True),
    db.Column('date_added', db.DateTime, default=datetime.datetime.utcnow())
)

user_faves = db.Table(
    'faves',
    db.Column('user_id',
              db.Integer,
              db.ForeignKey('users.id'), primary_key=True),
    db.Column('media_id',
              db.Integer,
              db.ForeignKey('media.id'), primary_key=True),
    db.Column('filename', db.Text),
    db.Column('date_added', db.DateTime, default=datetime.datetime.utcnow())
)


class User(UserMixin, db.Model):
    """
    Pyctogram users
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    accounts = db.relationship('Account',
                               secondary=accounts2users,
                               lazy='subquery',
                               backref=db.backref('users', lazy=True))
    faves = db.relationship('Media',
                            secondary=user_faves,
                            lazy='subquery',
                            backref=db.backref('users', lazy=True))
    lists = db.relationship('List',
                            lazy=True,
                            backref=db.backref('users', lazy='joined'))

    def __init__(self, username, email, password,
                 created_at=datetime.datetime.utcnow()):
        self.username = username
        self.email = email
        self.created_at = created_at
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_media_paginate(self, page=1, per_page=10):
        return Media.query.filter(
            Media.fav_users.any(User.id == self.id)).order_by(
            Media.timestamp.desc()).paginate(
            page, per_page, False)


class Account(db.Model):
    """
    Instragram accounts
    """
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)  # instagram id
    account_name = db.Column(db.Text, unique=True, nullable=False)
    full_name = db.Column(db.Text)
    biography = db.Column(db.Text)
    profile_pic_url = db.Column(db.Text)
    profile_pic_url_hd = db.Column(db.Text)
    external_url = db.Column(db.Text)
    external_url_linkshimmed = db.Column(db.Text)
    followed_by = db.Column(db.Integer)
    follow = db.Column(db.Integer)
    last_updated = db.Column(db.Integer)
    is_private = db.Column(db.Boolean)
    media = db.relationship('Media',
                            lazy=True,
                            backref=db.backref('accounts', lazy='joined'))
    account_lists = db.relationship('List',
                                    secondary=accounts2lists,
                                    lazy='subquery',
                                    backref=db.backref('account', lazy=True))

    def __init__(self, id, account_name):
        self.id = id
        self.account_name = account_name

    def get_media_paginate(self, page=1, per_page=10):
        return Media.query.join(Account).filter(Account.id == self.id).order_by(
            Media.timestamp.desc()).paginate(
            page, per_page, False)


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', name='fk_user_list'),
        nullable=True
    )
    shortname = db.Column(db.Text)
    longname = db.Column(db.Text)
    description = db.Column(db.Text)
    last_updated = db.Column(db.Integer)
    date_added = db.Column(db.DateTime)
    is_hidden = db.Column(db.Boolean)
    is_default = db.Column(db.Boolean, default=False)
    user = db.relationship(User, backref='user')
    accounts = db.relationship('Account',
                               secondary=accounts2lists,
                               lazy='subquery',
                               backref=db.backref('lists', lazy=True))

    def __init__(self, user_id, shortname, longname, description="",
                 date_added=datetime.datetime.utcnow()):
        self.user_id = user_id
        self.shortname = shortname
        self.longname = longname
        self.description = description
        self.date_added = date_added

    def get_media_paginate(self, page=1, per_page=10):
        return Media.query.join(Account).filter(
            Account.account_lists.any(List.id == self.id)).order_by(
            Media.timestamp.desc()).paginate(
            page, per_page, False)


class Media(db.Model):
    """
    Accounts media
    """
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)  # instagram id
    owner = db.Column(
        db.Integer,
        db.ForeignKey('accounts.id', name='fk_media_account'),
        nullable=True
    )
    media_type = db.Column(db.Text)
    is_video = db.Column(db.Boolean)
    display_url = db.Column(db.Text)
    caption = db.Column(db.Text)
    shortcode = db.Column(db.Text)
    timestamp = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    thumbnails = db.Column(db.Text)
    sidecar = db.Column(db.Text)
    account = db.relationship(Account, backref='account')
    fav_users = db.relationship('User',
                                secondary=user_faves,
                                lazy='subquery',
                                backref=db.backref('media', lazy=True))

    def is_saved(self, user_id):
        return User.query.filter(
            User.id == user_id, User.faves.any(Media.id == self.id)).first()
