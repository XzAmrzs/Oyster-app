# coding=utf-8
from datetime import datetime, date
import hashlib

from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


user_word = db.Table('user_word',
                     db.Column('user_id', db.Integer, db.ForeignKey('words.id')),
                     db.Column('word_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('level', db.Integer, default=0, index=True)
                     )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    last_checkin = db.Column(db.DateTime(), default=date(2013, 1, 1))
    avatar_hash = db.Column(db.String(32))
    # shanbay修改
    # timezone = db.Column(db.String(32))
    rank = db.Column(db.Integer, default=0)
    word_totals = db.Column(db.Integer, default=50)
    # study_times = db.Column(db.Integer, default=5)
    level = db.Column(db.Integer, default=0)
    auto_voice = db.Column(db.Integer, default=0)
    # 用户和笔记的一对多关系
    notes = db.relationship('Note', backref='author', lazy='dynamic')
    # 用户和单词的多对多关系
    words = db.relationship('Word', secondary=user_word, backref=db.backref('users', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SHANBAY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                    self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
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

    def generate_reset_token(self, expiration=3600):
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

    def generate_email_change_token(self, new_email, expiration=3600):
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
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url, hash=hash, size=size, default=default, rating=rating)

    # 用当前日期和用户上次打完卡的时间做比较(只比较天数)
    # 如果天数相差大于等于1那么说明是新的一天,返回True
    def is_new_day(self):
        return (date.today() - self.last_checkin).days >= 1

    # 根据用户的难度和用户的单词量取新单词
    # 0 四级 1 六级 2 托福 3 雅思
    # 每日单词量的新词比为0.17
    def new_words(self, proportion=0.17):
        # return a new words list
        cu_word_totals = int(self.word_totals * proportion)
        return Word.query.filter_by(rank=self.rank).order_by(func.random()).limit(cu_word_totals).all()

    def insert_new_words(self):
        # 将新单词插入到user_word表中
        for new_word in self.new_words():
            self.words.append(new_word)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64), unique=True, index=True)
    rank = db.Column(db.Integer, index=True)
    USA_voice = db.Column(db.TEXT(), unique=True)
    UK_voice = db.Column(db.TEXT(), unique=True)
    eg = db.Column(db.Text())
    translations = db.Column(db.Text())
    phonetic_symbol = db.Column(db.String(128))
    # words表和notes表的一对多关系
    notes = db.relationship('Note', backref='word', lazy='dynamic')

    # words表和users表的多对多关系在user中定义

    # 同义词功能还没有想好要怎么实现
    # synonym = db.Column(db.Text())

    def __repr__(self):
        return '<words %r>' % self.content


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.TEXT(), index=True)
    like_counts = db.Column(db.Integer, default=0)
    dislike_counts = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime(64), index=True, default=datetime.utcnow)
    # 协管员通过这个查禁不当评论
    disabled = db.Column(db.BOOLEAN)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))

    def __repr__(self):
        return '<notes %r>' % self.body


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
