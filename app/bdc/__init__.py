from flask import Blueprint

bdc = Blueprint('bdc', __name__)

from . import views
