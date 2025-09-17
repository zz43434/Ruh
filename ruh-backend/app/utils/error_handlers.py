def handle_not_found_error(error):
    response = {
        "status": "error",
        "message": "Resource not found."
    }
    return response, 404

def handle_internal_server_error(error):
    response = {
        "status": "error",
        "message": "An internal server error occurred."
    }
    return response, 500

def handle_validation_error(error):
    response = {
        "status": "error",
        "message": "Validation error.",
        "details": error.messages
    }
    return response, 400

def register_error_handlers(app):
    app.register_error_handler(404, handle_not_found_error)
    app.register_error_handler(500, handle_internal_server_error)
    app.register_error_handler(400, handle_validation_error)