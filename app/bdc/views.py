# coding=utf-8
from flask import render_template, redirect, url_for, flash, jsonify
from flask.ext.login import login_required, current_user
from . import bdc
from .forms import BDCSettingsForm, BDCReviewForm, NoteForm, NextForm
from .. import db
from ..models import Note


@bdc.route('/review', methods=['GET', 'POST'])
@login_required
def bdc_review():
    if current_user.is_new():
        today_words = current_user.init_words()
        new_words = today_words
    elif not current_user.is_have_today_words():
        current_user.insert_new_words()
        today_words, new_words = current_user.generate_today_words()
    elif current_user.is_checkin():
        flash(u'您已完成今日打卡任务')
        return render_template('bdc/success.html')
    else:
        today_words = current_user.get_today_words()
        new_words = current_user.get_today_new_words()
    today_words_totals = len(today_words)
    new_words_totals = len(new_words)
    return render_template('bdc/review.html', today_words_totals=today_words_totals,
                           new_words_totals=new_words_totals)


# @bdc.route('/ajax_labsID')
# def addID():
#     courseID = request.args.get('CourseID', '0', type=str)
#     course_ajax = Courses.query.filter_by(CourseID=courseID).first()
#     print course_ajax.labs
#     x = []
#     for i in course_ajax.labs:
#         x.append(i.LabID)
#     LabName_ajax = Labs.query.filter(Labs.LabID == x[0]).first().LabName
#     return jsonify(LabsID=x, LabName=LabName_ajax)
#
# @bdc.route('/review/<int:word_id>', methods=['GET', 'POST'])
# @login_required
# def bdc_review_id(word_id):
#     # 如果的今日单词列表已经全部认识了一遍，那么就跳转到完成打卡界面
#     word = current_user.get_today_words()
#     form = NoteForm()
#     next_form = NextForm()
#     if form.validate_on_submit():
#         note = Note(body=form.body.data,
#                     word=word,
#                     author=current_user._get_current_object()
#                     )
#         db.session.add(note)
#         flash(u'您的笔记添加成功')
#         return redirect(url_for('.bdc_review_id', word_id=word_id))
#     if next_form.validate_on_submit():
#         return redirect(url_for('.bdc_review_id', word_id=word_id + 1))
#     return render_template('bdc/study.html', word=word, form=form, nextForm=next_form)


@bdc.route('/bdc/settings', methods=['GET', 'POST'])
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
