# coding=utf-8
from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, BDCSettingsForm, BDCReviewForm
from .. import db
from ..models import Role, User, Word
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
    words = Word.query.filter_by(id=1).first_or_404()
    # userNow = request.user  # 获取username，这个是个实例
    # userName = userNow.username
    # settingUser_instance = Setting.objects.get(user=userNow.id)
    # settingRank = int(settingUser_instance.settingRank)
    # settingNumber = int(settingUser_instance.settingNumber)
    #
    # # 数据提取：
    # # word_str_=Word.objects.order_by('?')[:num]#此语句在百万级数据面前是最快速简单的随机选取num个数据的方法
    # wordStandard = Word.objects.filter(wordRank__lte=settingRank)  # 获取等级小于等于lv的所有数据
    # wordStandard_number = random.sample(list(wordStandard), settingNumber)  # 随机获取num个数据 在list中
    # wordToWeb = []
    #
    # for wordBeUse in wordStandard_number:
    #     tmpWord = []
    #     tmpAll = []
    #     # 单词具体内容添加
    #     tmpWord.append(wordBeUse.wordName)
    #     tmpWord.append(wordBeUse.wordTranslation)
    #     tmpWord.append(wordBeUse.wordExample)
    #     tmpWord.append(wordBeUse.wordSynonyms)
    #     # 下面这段是笔记添加
    #     try:
    #         wordNowNote_instance = Note.objects.filter(word=wordBeUse.id)  # 这个是此单词的所有笔记的实例的集合
    #         wordNowNote_all = []  # 这个单词的所有笔记
    #         wordNowNote_userNow = "暂无个人笔记"  # 这个单词的个人笔记
    #         for noteBeUse in wordNowNote_instance:
    #             wordNowNote_all.append(noteBeUse.noteContent)  # 把这个单词的所有笔记内容
    #             if noteBeUse.noteAuthor == userName:
    #                 wordNowNote_userNow = noteBeUse.noteContent  # 此用户这个单词的笔记
    #         wordNowNote_all.insert(0, wordNowNote_userNow)  # 把此用户的笔记加入到笔记开头
    #     # 没笔记就创建一个默认的笔记
    #     except Note.DoesNotExist:
    #         Note.objects.create(word=wordBeUse, noteAuthor=userNow, noteContent="暂无笔记")
    #         wordNowNote_all = ["暂无个人笔记", "暂无任何笔记"]
    #
    #     # 每个单词的临时列表 tmpALL = [tmpWord,wordNowNote_all]
    #     tmpAll.append(tmpWord)
    #     tmpAll.append(wordNowNote_all)
    #     # 传递给前端的列表wordToWord = [tmpALL(word1),tmpALL(word2),tmpALL(word3),……]
    #     wordToWeb.append(tmpAll)
    #
    # return render(request, 'word.html',
    #               {'wordToWeb': wordToWeb, 'rank': settingRank,
    #                # 'noteTest':wordToWeb,
    #                'number': settingNumber, 'user': userName})
    # if form.validate_on_submit():
    #     current_user.name = form.name.data
    #     current_user.location = form.location.data
    #     current_user.about_me = form.about_me.data
    #     db.session.add(current_user)
    #     flash('Your profile has been updated.')
    #     return redirect(url_for('.user', username=current_user.username))

    # form.name.data = current_user.name
    # form.location.data = current_user.location
    # form.about_me.data = current_user.about_me
    return render_template('bdc/review.html', words=words)


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
        flash('Your profile has been updated.')
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