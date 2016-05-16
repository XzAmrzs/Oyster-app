# coding=utf-8
import json

from flask import jsonify, request, current_app, url_for, g

from .. import db
from .errors import bad_request
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


@api.route('/users/<int:id>/checkin/', methods=['POST'])
def edit_user_checkin(id):
    user = User.query.get_or_404(id)
    words = request.json.get('words')
    flag = True
    for word in words:
        if not word['processed']:
            flag = False
    if flag:
        user.checkin()
        db.session.add(user)
        db.session.commit()
    else:
        return bad_request('not all processed')
    return jsonify(user.to_json()), 201, \
           {'Location': url_for('api.get_user', id=user.id,
                                _external=True)}
