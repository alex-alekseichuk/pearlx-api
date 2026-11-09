"""Unit tests for environment config settings."""
import os

from src.pearlx_api_flex import create_app


def test_config_development():
    app = create_app("development")
    assert app.config["ENV"] == "development"
    assert app.config["DEBUG"] == {"0": False, "1": True}[os.getenv("FLASK_DEBUG")]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == os.getenv("DATABASE_URL")


def test_config_production():
    app = create_app("production")
    assert app.config["ENV"] == "production"
    assert app.config["DEBUG"] == {"0": False, "1": True}[os.getenv("FLASK_DEBUG")]
    assert app.config["SQLALCHEMY_DATABASE_URI"] == os.getenv("DATABASE_URL")
