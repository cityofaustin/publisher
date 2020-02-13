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
    return handle_error(f"Missing required arg: [{arg}]", 400)

def handle_error(msg, code):
    print(f"{code} Error: {msg}")
    return msg, code

def handle_success(msg):
    print(msg)
    return msg, 200