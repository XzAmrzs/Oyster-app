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


@main.route('/bdc/review', methods=['GET', 'POST'])
@login_required
def bdc():
    # form = BDCReviewForm()
    words = current_user.words
    # if current_user.is_new_day():
    #     words = Word.new_words()
    form = NoteForm()
    if form.validate_on_submit():
        # 没个笔记要添加到对应的这个单词和用户中
        # note = Note(body=form.body.data,
        #             word=current_word,
        #             author=current_user._get_current_object()
        #             )
        # db.session.add(note)
        flash(u'您的笔记添加失败')
        return redirect(url_for('.bdc'))
    return render_template('bdc/review.html', words=words, form=form)


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
