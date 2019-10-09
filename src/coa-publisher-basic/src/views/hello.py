from flask import Blueprint

bp = Blueprint('common', __name__)

@bp.route('/', methods=('GET',))
def index():
    return "Hello, world!!", 200
