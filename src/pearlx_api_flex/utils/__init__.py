import os
import hashlib
import jwt
import boto3
import smtplib
import hmac
import re

from datetime import datetime, timedelta
from flask import current_app
from botocore.exceptions import ClientError
from email.mime.text import MIMEText


def generate_salt():
    return os.urandom(32)


def hash_password_with_salt(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)


def verify_password_hash(password, password_hash, password_salt):
    return hmac.compare_digest(
        password_hash,
        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), password_salt, 100000),
    )


def is_password_secured(password):
    length = (password_length := len(password)) > 7 and password_length < 17
    digit = re.search(r"\d", password) is not None
    uppercase = re.search(r"[A-Z]", password) is not None
    lowercase = re.search(r"[a-z]", password) is not None
    symbol = bool(set(" !@#$%^&*() -=[]\\;',./ _+{}|:\"<>?").intersection(password))
    return all([length, digit, uppercase, lowercase, symbol])


def generate_jwt_token(key, expiration, payload):
    now = datetime.utcnow()
    payload["exp"] = now + timedelta(seconds=expiration)
    return jwt.encode(payload, key, algorithm="HS256")


def verify_jwt_token(token, key):
    try:
        payload = jwt.decode(token, key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        current_app.logger.warning("Access token expired.")
        return
    except jwt.InvalidTokenError as err:
        current_app.logger.error("Invalid token.")
        current_app.logger.error(err)
        return
    return payload


def send_email(to, subject, body):
    if current_app.config.get("ENV") == "development" and current_app.config.get("EMAIL_LOCAL_HOST"):
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = current_app.config.get("EMAIL_FROM")
        msg["To"] = to

        with smtplib.SMTP(
            current_app.config.get("EMAIL_LOCAL_HOST"), current_app.config.get("EMAIL_LOCAL_PORT")
        ) as server:
            server.sendmail(current_app.config.get("EMAIL_FROM"), [to], msg.as_string())

        return True

    client = boto3.client("ses", region_name=current_app.config.get("AWS_REGION"))

    try:
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    to,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": body,
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject,
                },
            },
            Source=current_app.config.get("EMAIL_FROM"),
        )
    except ClientError as err:
        current_app.logger.error(f"Can't send email {subject} to {to}, err {err.response['Error']['Message']}")
        current_app.logger.error(err)
        return False
    current_app.logger.info(f"Email sent! Message ID: {response['MessageId']}")
    return True
