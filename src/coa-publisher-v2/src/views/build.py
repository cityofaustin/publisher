from flask import request

from app import app

from helpers.res_handlers import handle_error, handle_missing_arg, handle_success

@app.route('/build', methods=('POST',), strict_slashes=False)
def build():
    data = request.get_json(force=True)
