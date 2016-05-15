# coding=utf-8
from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Note, UserWord


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:user_id>/words/<int:word_id>/notes/')
def get_user_word_notes(user_id, word_id):
    notes = Note.query.filter_by(user_id=user_id, word_id=word_id).all()
    return jsonify({
        'notes': [note.to_json() for note in notes]
    })


@api.route('/users/<int:id>/today-words/')
def get_user_words(id):
    user = User.query.get_or_404(id)
    words = user.get_today_words()
    return jsonify({
        'words': [word.to_json() for word in words],
    })


@api.route('/users/<int:id>/notes/')
def get_user_notes(id):
    user = User.query.get_or_404(id)
    notes = user.notes
    return jsonify({
        'notes': [note.to_json() for note in notes],
    })


# @api.route('/users/<int:id>', methods=['PUT'])
# # 这个路由需要加入什么权限管理?
# @permission_required(这个参数应该是客户端传过来一个)
# def edit_user(id):
#     user = User.query.get_or_404(id)
#     if g.current_user != user and \
#             not g.current_user.can(Permission.ADMINISTER):
#         return forbidden('Insufficient permissions')
#     post.body = request.json.get('body', post.body)
#     db.session.add(post)
#     return jsonify(post.to_json())
