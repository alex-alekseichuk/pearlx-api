from .services import (
    AuthenticationException,
    ServiceException,
    AuthorizationException,
    NotFoundException,
    IncorrectInputException,
)


def init_error_handlers(app):
    @app.errorhandler(AuthenticationException)
    def handle_authentication_exception(error):
        """When the login is incorrect or token is expired/incorrect."""
        return {"status": 401, "message": str(error)}, 401

    @app.errorhandler(AuthorizationException)
    def handle_authorization_exception(error):
        """When the request is not authorized on service layer."""
        return {"status": 403, "message": str(error)}, 403

    @app.errorhandler(NotFoundException)
    def handle_not_found_exception(error):
        """When service layer can't find some object."""
        return {"status": 404, "message": str(error)}, 404

    @app.errorhandler(IncorrectInputException)
    def handle_input_exception(error):
        """When input is incorrect."""
        return {"status": 409, "message": str(error)}, 409

    @app.errorhandler(ServiceException)
    def handle_service_exception(error):
        """When some service error occurs."""
        return {"status": 500, "message": str(error)}, 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """When some service error occurs."""
        return {"status": 500, "message": str(error)}, 500
