from flask import jsonify
import traceback

# Handle uncaught 500 Internal Server Errors
def handle_internal_server_error(e):
    print(str(e))
    traceback.print_tb(e.__traceback__)

    status = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(status), 500

def handle_missing_arg(arg):
    return handle_400_error(f"Missing required arg: [{arg}]")

def handle_400_error(msg):
    print(msg)
    return msg, 400

def handle_success(msg):
    print(msg)
    return msg, 200
