"""
Config settings for development, testing and production environments.
Values can be loaded from ENV or SecretsManager secret.

ENV params:
    FLASK_*
    AWS_*
    LOG_LEVEL
    COLORED_LOGS
    ADMIN_* for migrations and test
    SCHEDULER_*
    PROMETHEUS_*
Secret params:
    DATABASE_*
    JWT_*
    DER_*
    TSTREAM_*
    SMTP_*
"""
import io
import os

import awswrangler as wr
import boto3
from dotenv import load_dotenv

from .utils.bot3_session import get_bot3_session


def get_config(app, config_name):
    load_dotenv()

    config = {
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-2"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "info"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_EXPIRY_SECONDS": os.getenv("JWT_EXPIRY_SECONDS"),
        "JWT_KEY": os.getenv("JWT_KEY"),
        "SCHEDULER_ENABLED": bool(int(os.getenv("SCHEDULER_ENABLED"))),
        "SCHEDULER_REFRESH_FROM_TIMESTREAM": os.getenv("SCHEDULER_REFRESH_FROM_TIMESTREAM"),
        "PROMETHEUS_ENABLED": bool(int(os.getenv("PROMETHEUS_ENABLED", 0))),
        "PROPAGATE_EXCEPTIONS": True,
        "EMAIL_FROM": os.getenv("EMAIL_FROM", "no-reply@pearlxinfra.com"),
        "DATABASE_USERNAME": os.getenv("DATABASE_USERNAME", "pearlx_api"),
        "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD", "pearlx_api"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME", "pearlx_api"),
        "DATABASE_HOST": os.getenv("DATABASE_HOST", "localhost"),
        "TSTREAM_DB": os.getenv("TSTREAM_DB", "VPPTimestreamdev"),
        "TSTREAM_PROPS_TBL": os.getenv("TSTREAM_PROPS_TBL", "VPPSitePropertiesdev"),
        "TSTREAM_MEASURES_TBL": os.getenv("TSTREAM_MEASURES_TBL", "VPPSiteMeasurementsdev"),
    }

    if "DATABASE_HOST" in config and "DATABASE_URL" not in config:
        config["DATABASE_URL"] = (
            f"postgresql+psycopg2://{config['DATABASE_USERNAME']}:{config['DATABASE_PASSWORD']}"
            f"@{config['DATABASE_HOST']}:5432/{config['DATABASE_NAME']}"
        )

    if config_name == "development":
        config |= {
            "ENV": "development",
            "DEBUG": bool(int(os.getenv("FLASK_DEBUG", 1))),
            "SQLALCHEMY_ECHO": True,
            "EMAIL_LOCAL_HOST": os.getenv("EMAIL_LOCAL_HOST"),
            "EMAIL_LOCAL_PORT": os.getenv("EMAIL_LOCAL_PORT"),
        }
    else:  # production
        config |= {
            "ENV": "production",
            "DEBUG": bool(int(os.getenv("FLASK_DEBUG", 0))),
            "SQLALCHEMY_ECHO": False,
        }

    if os.getenv("AWS_ACCESS_KEY_ID"):
        config["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
    if os.getenv("AWS_SECRET_ACCESS_KEY"):
        config["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")

    if os.getenv("AWS_SECRETS_NANE"):
        secrets = wr.secretsmanager.get_secret_json(os.getenv("AWS_SECRETS_NANE"), get_bot3_session())
        if secrets:
            config |= secrets

    if "DATABASE_URL" in config:
        config["SQLALCHEMY_DATABASE_URI"] = config["DATABASE_URL"]

    if "DER_CERT_PASSWORD" in config:
        config["DER_CERT_BYTES"] = load_der_cert(config)

    app.logger.debug("Config:\n" + "\n".join([f"  {key}: {value}" for key, value in config.items()]))

    return config


def load_der_cert(config):
    s3_resource = boto3.resource("s3", region_name=config["AWS_REGION"])
    s3_bucket = s3_resource.Bucket(config["DER_CERT_S3_BUCKET"])
    buf = io.BytesIO()
    s3_bucket.download_fileobj(config["DER_CERT_S3_FILENAME"], buf)
    return buf.getvalue()
