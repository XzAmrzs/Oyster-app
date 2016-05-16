# coding=utf-8
from flask import jsonify, request, g, abort, url_for, current_app
from flask.ext.login import current_user

from .. import db
from ..models import Note, Permission, Word
from . import api
from .decorators import permission_required
from .errors import forbidden


# @api.route('/notes/')
# def get_notes():
#     page = request.args.get('page', 1, type=int)
#     pagination = Note.query.paginate(
#             page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#             error_out=False)
#     notes = pagination.items
#     prev = None
#     if pagination.has_prev:
#         prev = url_for('api.get_notes', page=page - 1, _external=True)
#     next = None
#     if pagination.has_next:
#         next = url_for('api.get_notes', page=page + 1, _external=True)
#     return jsonify({
#         'notes': [note.to_json() for note in notes],
#         'prev': prev,
#         'next': next,
#         'count': pagination.total
#     })


@api.route('/notes/<int:id>')
def get_note(id):
    note = Note.query.get_or_404(id)
    return jsonify(note.to_json())


@api.route('/notes/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_note():
    note = Note.from_json(request.json)
    note.author = g.current_user
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_json()), 201, \
           {'Location': url_for('api.get_note', id=note.id, _external=True)}


@api.route('/notes/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_note(id):
    note = Note.query.get_or_404(id)
    if g.current_user != note.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    note.body = request.json.get('body', note.body)
    db.session.add(note)
    return jsonify(note.to_json())


@api.route('/words/<int:id>/notes/', methods=['POST'])
# @permission_required(Permission.NOTE)
def new_word_note(id):
    word = Word.query.get_or_404(id)
    note = Note.from_json(request.json)
    # 直接用g有点小问题，除非整个全是前后端分离才可
    # note.author = g.current_user
    note.author = current_user
    note.word = word
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_json()), 201, \
           {'Location': url_for('api.get_note', id=note.id,
                                _external=True)}
