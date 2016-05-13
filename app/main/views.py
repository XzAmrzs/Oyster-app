# coding=utf-8
from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, BDCSettingsForm, BDCReviewForm, NoteForm
from .. import db
from ..models import Role, User, Word, Note
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/bdc/review/', methods=['GET', 'POST'])
@login_required
def bdc():
    form = BDCReviewForm()
    if current_user.is_new_day():
        print '距离上次打卡超过1天，插入新单词'
        current_user.insert_new_words()
    if form.validate_on_submit():
        flash(u'开始学习')
        # 此处应该有一个User的今日单词函数，返回的是旧的加新的单词列表
        # first_id = current_user.today_words()
        return redirect(url_for('.bdc_review_id', word_id=1))
    return render_template('bdc/review.html', form=form)


@main.route('/bdc/review/<int:word_id>', methods=['GET', 'POST'])
@login_required
def bdc_review_id(word_id):
    word = Word.query.filter_by(id=word_id).first()
    form = NoteForm()
    if form.validate_on_submit():
        # 每个笔记要添/加到对应的这个单词和用户中
        note = Note(body=form.body.data,
                    word=word,
                    author=current_user._get_current_object()
                    )
        db.session.add(note)
        flash(u'您的笔记添加成功')
        return redirect(url_for('.bdc_review_id', word_id=word_id))
    return render_template('bdc/study.html', word=word, form=form)


# @main.route('/ajax_labsID')
# def addID():
#     courseID = request.args.get('CourseID', '0', type=str)
#     course_ajax = Courses.query.filter_by(CourseID=courseID).first()
#     print course_ajax.labs
#     x = []
#     for i in course_ajax.labs:
#         x.append(i.LabID)
#     LabName_ajax = Labs.query.filter(Labs.LabID == x[0]).first().LabName
#     return jsonify(LabsID=x, LabName=LabName_ajax)


@main.route('/bdc/settings', methods=['GET', 'POST'])
@login_required
def bdc_settings():
    form = BDCSettingsForm()
    if form.validate_on_submit():
        current_user.word_totals = form.word_totals.data
        current_user.rank = form.rank.data
        current_user.level = form.level.data
        current_user.auto_voice = form.auto_voice
        db.session.add(current_user)
        flash('Your vocabulary settings has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.word_totals.data = current_user.word_totals
    form.rank.data = current_user.rank
    form.level.data = current_user.level
    form.auto_voice.data = current_user.auto_voice
    return render_template('bdc/bdc_settings.html', form=form)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
