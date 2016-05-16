# coding=utf-8
from flask import render_template, redirect, url_for, flash
from flask.ext.login import login_required, current_user
from . import bdc
from .forms import BDCSettingsForm
from .. import db


@bdc.route('/review', methods=['GET', 'POST'])
@login_required
def bdc_review():
    if current_user.is_new():
        flash(u'您是新用户')
        today_words = current_user.init_words()
        new_words = today_words
    elif not current_user.is_have_today_words():
        flash(u'为您发放今日的新单词')
        current_user.insert_new_words()
        today_words, new_words = current_user.generate_today_words()
    elif current_user.is_checkin():
        flash(u'您已完成今日打卡任务')
        return render_template('bdc/success.html')
    else:
        flash(u'欢迎回来')
        today_words = current_user.get_today_words()
        new_words = current_user.get_today_new_words()
    today_words_totals = len(today_words)
    new_words_totals = len(new_words)
    return render_template('bdc/review.html', today_words_totals=today_words_totals,
                           new_words_totals=new_words_totals)


@bdc.route('/settings', methods=['GET', 'POST'])
@login_required
def bdc_settings():
    form = BDCSettingsForm()
    if form.validate_on_submit():
        print current_user
        current_user.word_totals = form.word_totals.data
        current_user.rank = form.rank.data
        current_user.level = form.level.data
        current_user.auto_voice = form.auto_voice.data
        db.session.add(current_user)
        flash('Your vocabulary settings has been updated.')
        return redirect(url_for('bdc.bdc_settings'))
    form.word_totals.data = current_user.word_totals
    form.rank.data = current_user.rank
    form.level.data = current_user.level
    form.auto_voice.data = current_user.auto_voice
    return render_template('bdc/bdc_settings.html', form=form)

