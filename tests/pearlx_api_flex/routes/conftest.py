"""Global pytest fixtures."""
import os
import pytest
from src.pearlx_api_flex import create_app


@pytest.fixture()
def app(smtpd):
    app = create_app(os.getenv("FLASK_ENV", "development"))
    app.config["EMAIL_LOCAL_HOST"] = smtpd.hostname
    app.config["EMAIL_LOCAL_PORT"] = smtpd.port
    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
