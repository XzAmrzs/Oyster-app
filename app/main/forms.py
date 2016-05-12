# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class BDCSettingsForm(Form):
    word_totals = SelectField(u'每日学习量', coerce=int)
    rank = SelectField(u'单词难度', coerce=int)
    # study_times = db.Column(db.Integer, default=5)
    level = SelectField(u'单词的目标掌握程度', coerce=int)
    auto_voice = SelectField(u'自动发音模式', coerce=int)
    submit = SubmitField(u'确定')

    def __init__(self, *args, **kwargs):
        super(BDCSettingsForm, self).__init__(*args, **kwargs)
        self.word_totals.choices = [(total, total) for total in xrange(50, 701, 50)]
        self.rank.choices = [(0, u'四级'), (1, u'六级'), (2, u'托福'), (3, u'雅思')]
        self.auto_voice.choices = [(0, u'美音'), (1, u'英音')]
        self.level.choices = [(0, u'再认'), (1, u'拼写')]


class BDCReviewForm(Form):
    submit = SubmitField(u'开始学习')


class NoteForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField(u'提交笔记')
