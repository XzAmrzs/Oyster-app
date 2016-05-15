from flask import jsonify, request, current_app, url_for
from flask.ext.login import current_user

from app.api_1_0.users import get_user_word_notes
from . import api
from ..models import Word


@api.route('/words/<int:id>')
def get_word(id):
    word = Word.query.get_or_404(id)
    return jsonify(word.to_json())


@api.route('/words/<int:id>/notes/')
def get_word_notes(id):
    word = Word.query.get_or_404(id)
    notes = word.notes
    return jsonify({
        'notes': [note.to_json() for note in notes]
    })

#
# @api.route('/users/<int:id>/timeline/')
# def get_user_followed_words(id):
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     pagination = user.followed_words.order_by(Word.timestamp.desc()).paginate(
#             page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#             error_out=False)
#     words = pagination.items
#     prev = None
#     if pagination.has_prev:
#         prev = url_for('api.get_words', page=page - 1, _external=True)
#     next = None
#     if pagination.has_next:
#         next = url_for('api.get_words', page=page + 1, _external=True)
#     return jsonify({
#         'words': [word.to_json() for word in words],
#         'prev': prev,
#         'next': next,
#         'count': pagination.total
#     })
