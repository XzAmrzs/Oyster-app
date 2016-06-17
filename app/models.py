# coding=utf-8
from datetime import datetime, date
import hashlib
from sqlalchemy import func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user

# from app.api_1_0.users import get_user_word_notes
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    NOTE = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Rank:
    # 0 四级 1 六级 2 托福 3 雅思
    pass


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
                     Permission.NOTE |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.NOTE |
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
    # 上次完成任务
    last_checkin = db.Column(db.Date(), default=date(2013, 1, 1))
    avatar_hash = db.Column(db.String(32))
    # oyster修改
    timezone = db.Column(db.String(32))
    # 难度
    rank = db.Column(db.Integer, default=0)
    word_totals = db.Column(db.Integer, default=50)
    study_times = db.Column(db.Integer, default=5)
    # 对单词的目标掌握程度
    level = db.Column(db.Integer, default=0)
    auto_voice = db.Column(db.Integer, default=0)
    # 用户和笔记的一对多关系
    notes = db.relationship('Note', backref='author', lazy='dynamic')
    # 用户和单词的多对多关系
    # words = db.relationship('Word', secondary=user_word, backref=db.backref('users', lazy='dynamic'))

    # association proxy of "user_word" collection to "word" attribute
    words = association_proxy('user_words', 'word')

    @staticmethod
    def generate_fake(count=1):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email='test@oyster.com',
                     username=forgery_py.internet.user_name(True),
                     password='test',
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

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

    def is_new(self):
        return False if self.words else True

    def is_checkin(self):
        return (date.today() - self.last_checkin).days == 0

    def is_have_today_words(self):
        return True if UserWord.query.filter_by(user_id=self.id, last_time=date.today()).first() else False

    def init_words(self):
        first_words = Word.query.filter_by(rank=self.rank).order_by(func.random()).limit(self.word_totals).all()
        self.words += first_words
        db.session.add(self)
        db.session.commit()
        return self.words

    # 根据用户的难度和用户的单词量取新单词
    # 每日单词量的新词比为0.17
    def generate_new_words(self, proportion=0.17):
        today_new_words = []
        cu_new_word_totals = int(self.word_totals * proportion)
        words = Word.query.filter_by(rank=self.rank).order_by(func.random()).all()
        i = 0
        for new_word in words:
            if new_word not in self.words:
                today_new_words.append(new_word)
                i += 1
            if i == cu_new_word_totals:
                break
        return today_new_words

    def insert_new_words(self):
        self.words += self.generate_new_words()
        db.session.add(self)
        db.session.commit()

    def generate_today_words(self, proportion=0.17):
        today_old_words = []
        today_new_words = []
        cu_new_word_totals = int(self.word_totals * proportion)
        cu_old_word_totals = self.word_totals - cu_new_word_totals
        old_totals = 0
        new_totals = 0
        for user_word in self.user_words:
            if user_word.level in range(1, self.study_times):
                if old_totals != cu_old_word_totals:
                    today_old_words.append(user_word.word)
                    user_word.last_time = date.today()
                    old_totals += 1
            if user_word.level == 0:
                if new_totals != cu_new_word_totals:
                    today_new_words.append(user_word.word)
                    user_word.last_time = date.today()
                    new_totals += 1
        db.session.add(self)
        db.session.commit()
        today_words = today_new_words + today_old_words
        return today_words, today_new_words

    def get_today_words(self):
        today_words = [x.word for x in self.user_words if x.last_time == date.today()]
        return today_words

    def get_today_new_words(self):
        today_new_words = [x.word for x in self.user_words if x.last_time == date.today() and x.level == 0]
        return today_new_words

    def checkin(self):
        self.last_checkin = date.today()
        today_words = UserWord.get_user_today_words(self.id)
        for today_word in today_words:
            if today_word.last_time == date.today():
                today_word.update_level()
                db.session.add(today_word)

    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username,
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class UserWord(db.Model):
    __tablename__ = 'user_word'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), primary_key=True)
    level = db.Column(db.Integer, default=0, index=True)
    last_time = db.Column(db.Date(), default=date.today())
    # bidirectional attribute/collection of "user"/"user_words"
    user = db.relationship(User, backref=orm.backref("user_words", cascade="all, delete-orphan"))
    # reference to the "Word" object
    word = db.relationship("Word")

    def __init__(self, word=None, user=None, level=None):
        # 史上巨吭，参数的word和user位置互换就运行不了了
        self.user = user
        self.word = word
        self.level = level
    #
    # def __init__(self, **kwargs):
    #     super(UserWord, self).__init__(**kwargs)

    def update_level(self):
        self.level += 1

    @staticmethod
    def get_user_today_words(user_id):
        return UserWord.query.filter_by(user_id=user_id, last_time=date.today()).all()


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(64), unique=True, index=True)
    rank = db.Column(db.Integer, index=True, default=0)
    USA_voice = db.Column(db.TEXT())
    UK_voice = db.Column(db.TEXT())
    eg = db.Column(db.Text())
    translations = db.Column(db.Text())
    phonetic_symbol = db.Column(db.String(128))
    # words表和notes表的一对多关系
    notes = db.relationship('Note', backref='word', lazy='dynamic')

    # words表和users表的多对多关系在user中定义

    # 同义词功能还没有想好要怎么实现
    # synonym = db.Column(db.Text())

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            w = Word(content=forgery_py.lorem_ipsum.word(),
                     eg=forgery_py.lorem_ipsum.sentence(),
                     rank=randint(0, 3),
                     USA_voice=forgery_py.basic.text(spaces=False),
                     UK_voice=forgery_py.basic.text(spaces=False),
                     translations=forgery_py.lorem_ipsum.sentence(),
                     phonetic_symbol='[' + forgery_py.lorem_ipsum.word() + ']'
                     )
            if not w.query.filter_by(content=w.content).first():
                db.session.add(w)
                db.session.commit()

    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)

    def __repr__(self):
        return '<words %r>' % self.content

    def to_json(self):
        json_word = {
            'id': self.id,
            'content': self.content,
            'USA_voice': self.USA_voice,
            'UK_voice': self.UK_voice,
            'eg': self.eg,
            'translations': self.translations,
            'phonetic_symbol': self.phonetic_symbol,
            'user_notes': [note.to_json() for note in self.notes if note.id == current_user.id]
        }
        return json_word


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

    def to_json(self):
        json_note = {
            'id': self.id,
            'body': self.body,
            'author': self.author.to_json(),
        }
        return json_note

    @staticmethod
    def from_json(json_note):
        body = json_note.get('body')
        if body is None or body == '':
            raise ValidationError('note does not have a body')
        return Note(body=body)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
