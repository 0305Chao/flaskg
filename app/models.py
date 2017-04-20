# coding=utf-8
import hashlib
from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request


class Permissions(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permissions.FOLLOW |
                     Permissions.COMMENT |
                     Permissions.WRITE_ARTICLES, True),
            'Moderator': (Permissions.FOLLOW |
                          Permissions.COMMENT |
                          Permissions.WRITE_ARTICLES |
                          Permissions.MODERATE_COMMENTS, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if not role:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwds):
        super().__init__(**kwds)
        if not self.role:
            if self.email == current_app.config['FLASKG_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if not self.role:
                self.role = Role.query.filter_by(default=True).first()
        if self.email and self.avator_hash:
            self.avator_hash = hashlib.md5(
                self.email.encode('utf-8').hexdigest())

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravator.com/avator'
        else:
            url = 'http://www.gravator.com/avator'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    @property
    def password(self):
        raise AttributeError('看个这个密码知道自己是文盲了吧！')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=60 * 60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=60 * 60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_change_email_token(self, new_email, expiration=60 * 60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if not new_email:
            return False
        if not self.query.filter_by(email=new_email).first():
            return False
        self.email = new_email
        self.avator_hash = hashlib.md5(self.email.encode('utf-8').hexdigest())
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permissions.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
