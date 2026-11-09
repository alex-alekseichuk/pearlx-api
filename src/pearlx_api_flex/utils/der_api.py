from flask import current_app as app
from requests.auth import HTTPBasicAuth
import requests
import requests_pkcs12


def get_der(url):
    if "DER_CERT_BYTES" in app.config:
        return requests_pkcs12.get(
            f"{app.config.get('DER_URI')}{url}",
            pkcs12_data=app.config["DER_CERT_BYTES"],
            pkcs12_password=app.config["DER_CERT_PASSWORD"],
            auth=(app.config.get("DER_AUTH_USER"), app.config.get("DER_AUTH_PASSWORD")),
        )
    else:
        return requests.get(
            f"{app.config.get('DER_URI')}{url}",
            auth=HTTPBasicAuth(app.config.get("DER_AUTH_USER"), app.config.get("DER_AUTH_PASSWORD")),
        )


def post_der(url, data):
    app.logger.debug(f"post_der {url}")
    if "DER_CERT_BYTES" in app.config:
        app.logger.debug("has DER_CERT_BYTES")
        return requests_pkcs12.post(
            f"{app.config.get('DER_URI')}{url}",
            json=data,
            pkcs12_data=app.config["DER_CERT_BYTES"],
            pkcs12_password=app.config["DER_CERT_PASSWORD"],
            auth=(app.config.get("DER_AUTH_USER"), app.config.get("DER_AUTH_PASSWORD")),
        )
    else:
        app.logger.debug("has no DER_CERT_BYTES")
        return requests.post(
            f"{app.config.get('DER_URI')}{url}",
            json=data,
            auth=HTTPBasicAuth(app.config.get("DER_AUTH_USER"), app.config.get("DER_AUTH_PASSWORD")),
        )
