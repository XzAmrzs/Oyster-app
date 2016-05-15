# coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Required


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


class NextForm(Form):
    submit = SubmitField(u'下一个')


class CheckinForm(Form):
    submit = SubmitField(u'完成任务')
