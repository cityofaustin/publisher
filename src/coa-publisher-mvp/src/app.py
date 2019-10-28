from flask import Flask
from flask_cors import CORS

from helpers.res_handlers import handle_internal_server_error

# Initialize App
app = Flask(__name__)
app.config['DEBUG'] = False
CORS(app) # TODO: implement a more strict domain acceptance policy (e.g.: limit requests to just Joplin sites)
app.register_error_handler(500, handle_internal_server_error)

# Import Routes
import views.hello
import views.build
import views.publish
