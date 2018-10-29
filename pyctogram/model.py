from pyctogram import db

accounts2lists = db.Table(
    'acccounts2lists',
    db.Column('list_id',
              db.Integer,
              db.ForeignKey('lists.id'), primary_key=True),
    db.Column('account_id',
              db.Integer,
              db.ForeignKey('accounts.id'), primary_key=True),
    db.Column('date_added', db.DateTime)
)

accounts2users = db.Table(
    'acccounts2users',
    db.Column('user_id',
              db.Integer,
              db.ForeignKey('users.id'), primary_key=True),
    db.Column('account_id',
              db.Integer,
              db.ForeignKey('accounts.id'), primary_key=True),
    db.Column('date_added', db.DateTime)
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
    db.Column('date_added', db.DateTime)
)


# init user, with only an id for now
class User(db.Model):
    """
    Pyctogram users
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    accounts = db.relationship('Account',
                               secondary=accounts2users,
                               lazy='subquery',
                               backref=db.backref('users', lazy=True))
    faves = db.relationship('Media',
                            secondary=user_faves,
                            lazy='subquery',
                            backref=db.backref('users', lazy=True))


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
    last_updated = db.Column(db.DateTime)
    date_added = db.Column(db.DateTime)
    is_hidden = db.Column(db.Boolean)
    user = db.relationship(User, backref='user')
    accounts = db.relationship('Account',
                               secondary=accounts2lists,
                               lazy='subquery',
                               backref=db.backref('lists', lazy=True))


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
