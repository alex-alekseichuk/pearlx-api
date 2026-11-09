"""Flask app initialization via factory pattern."""
import logging

from flask import Flask, g, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from prometheus_flask_exporter import PrometheusMetrics

from src.pearlx_api_flex.services.auth import AuthService

from .config import get_config
from .db import init_db
from .error_handlers import init_error_handlers
from .logs import init_loggers
from .routes import init_routes

cors = CORS()
bcrypt = Bcrypt()
authService = AuthService()


def create_app(flask_env):
    init_loggers()

    app = Flask("pearlx-api-flex")

    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config.update(**get_config(app, flask_env))

    if app.config["PROMETHEUS_ENABLED"]:
        PrometheusMetrics(app)

    init_db(app)

    cors.init_app(app)
    bcrypt.init_app(app)

    @app.before_request
    def init_context():
        g.context = None
        if "Authorization" not in request.headers:
            return
        token = request.headers["Authorization"].split()[1]
        if token is not None:
            g.context = authService.verify_token(token)

    init_error_handlers(app)

    @app.after_request
    def after_request(response):
        """Logging after every request."""
        logging.getLogger("app.access").info(
            "%s %s %s %s %s %s",
            request.remote_addr,
            request.method,
            request.path,
            request.scheme,
            response.status,
            response.content_length,
        )
        return response

    api = init_routes()
    api.init_app(app)

    return app
