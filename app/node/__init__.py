
from flask import Blueprint

node = Blueprint('node', __name__)

from . import views
