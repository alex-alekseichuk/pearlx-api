import uuid

from datetime import datetime
from flask import current_app, g, render_template

from . import (
    on_error,
    AuthenticationException,
    NotFoundException,
    IncorrectInputException,
)
from ..db.dao import transaction
from ..db.dao.users import UsersDao
from ..utils import generate_jwt_token, verify_jwt_token, send_email, is_password_secured


class AuthService:
    def __init__(self):
        self.usersDao = UsersDao()

    @on_error("Can't register a user")
    @transaction
    def register(self, data):
        # TODO: check duplicates for firstname, lastname, email
        if not is_password_secured(data["password"]):
            raise IncorrectInputException(
                "Password is not strong. Use 8-16 lowercase and uppercase, digit and special symbols."
            )
        user = self.usersDao.createUser(data)
        self.usersDao.createUsagePlan(user)
        token = str(uuid.uuid4())
        now = datetime.utcnow()
        _user = self.usersDao.get_user_by_email(user.email)
        self.usersDao.update(_user.id, {"verify_email_token": token, "verify_email_token_send_at": now})
        send_email(
            user.email,
            "Pearlx - Verify email request",
            render_template(
                "verify-email.html", name=f"{user.firstname} {user.lastname}", email=user.email, token=token
            ),
        )
        return user

    @on_error("Can't login")
    @transaction
    def login(self, data):
        email = data["email"]
        user = self.usersDao.get_user_by_email(email)
        if user is None:
            current_app.logger.warning(f"Unknown email: {email}")
            raise AuthenticationException("Incorrect login.")
        if not user.enabled:
            current_app.logger.warning(f"User disabled: {email}")
            raise AuthenticationException("User disabled.")
        if not user.email_verified:
            current_app.logger.warning(f"User email unverified: {email}")
            raise AuthenticationException("User email unverified.")
        if not user.verify_password(data["password"]):
            current_app.logger.warning(f"Incorrect password for email: {email}")
            raise AuthenticationException("Incorrect login.")
        token = AuthService.generate_token(user)
        self.usersDao.createApiKey(user.usage_plan, token)
        return token

    @on_error("Can't logout")
    @transaction
    def logout(self):
        user_id = g.context["user_id"]
        user = self.usersDao.get_user_by_id(user_id)
        if user is None:
            current_app.logger.error(f"Unknown user_id: {user_id}")
            return
        self.usersDao.deleteApiKey(user.usage_plan)

    @on_error("Can't get info about me")
    def get_info_about_me(self):
        return self.usersDao.get_user_by_id(g.context["user_id"])

    @on_error("Can't change password")
    @transaction
    def change_password(self, data):
        user_id = g.context["user_id"]
        user = self.usersDao.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(f"Can't get user by ID: {user_id}")
        password = data["new-password"]
        if not is_password_secured(password):
            raise IncorrectInputException(
                "Password is not strong. Use 8-16 lowercase and uppercase, digit and special symbols."
            )
        if user.is_password_used(password):
            raise IncorrectInputException("Password was already used")
        data = user.create_password_fields(password)
        self.usersDao.update(user_id, data)

    @on_error("Can't perform forgot password")
    @transaction
    def forgot_password(self, data):
        email = data["email"]
        user = self.usersDao.get_user_by_email(email)
        if user is None:
            current_app.logger.warning(f"Unknown email: {email}")
            raise AuthenticationException("Unknown email.")
        token = str(uuid.uuid4())
        now = datetime.utcnow()
        self.usersDao.update(user.id, {"reset_token": token, "reset_token_sent_at": now})
        send_email(
            user.email,
            "Pearlx - Forgot password request",
            render_template("forgot-password.html", name=f"{user.firstname} {user.lastname}", email=email, token=token),
        )

    @on_error("Can't reset password")
    @transaction
    def reset_password(self, data):
        token = data["token"]
        password = data["password"]
        user = self.usersDao.get_user_by_reset_token(token)
        if user is None:
            current_app.logger.warning(f"Unknown token: {token}")
            raise AuthenticationException("Unknown token.")
        now = datetime.utcnow()
        time_diff_in_mins = (now - user.reset_token_sent_at).total_seconds() / 60
        if time_diff_in_mins > 10:
            current_app.logger.warning(f"token: {token} expired")
            raise AuthenticationException("Expired token.")
        if not is_password_secured(password):
            raise IncorrectInputException(
                "Password is not strong. Use 8-16 lowercase and uppercase, digit and special symbols."
            )
        if user.is_password_used(password):
            raise IncorrectInputException("Password was already used")
        data = user.create_password_fields(password)
        data["reset_token"] = None
        data["reset_token_sent_at"] = None
        self.usersDao.update(user.id, data)

    @on_error("Can't send verify email token")
    @transaction
    def reverify_email(self, data):
        email = data["email"]
        user = self.usersDao.get_user_by_email(email)
        if user is None:
            return ""
        token = str(uuid.uuid4())
        now = datetime.utcnow()
        self.usersDao.update(user.id, {"verify_email_token": token, "verify_email_token_send_at": now})
        send_email(
            user.email,
            "Pearlx - Verify email request",
            render_template(
                "reverify-email.html", name=f"{user.firstname} {user.lastname}", email=user.email, token=token
            ),
        )
        return ""

    @on_error("Can't verify email token")
    @transaction
    def verify_email_token(self, data):
        email = data["email"]
        token = data["token"]
        user = self.usersDao.get_user_by_email(email)
        if token != user.verify_email_token:
            current_app.logger.warning(f"Unknown verify_email_token for email: {email}")
            raise AuthenticationException("Unknown verify_email_token for email.")
        data["email_verified"] = True
        data["verify_email_token"] = None
        data["verify_email_token_send_at"] = None
        self.usersDao.update(user.id, data)

    @staticmethod
    def generate_token(user):
        return generate_jwt_token(
            current_app.config["JWT_KEY"],
            int(current_app.config.get("JWT_EXPIRY_SECONDS")),
            {
                "user_id": str(user.id),
                "is_admin": user.is_admin,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
            },
        )

    def verify_token(self, token):
        payload = verify_jwt_token(token, current_app.config["JWT_KEY"])
        if payload is None:
            return
        user_id = payload["user_id"]
        user = self.usersDao.get_user_by_id(user_id)
        if user is None:
            current_app.logger.error(f"Unknown user_id: {user_id}")
            return
        if user.usage_plan and user.usage_plan.api_key and user.usage_plan.api_key.token == token:
            return payload
        current_app.logger.error(f"Unknown token for user_id: {user_id}")
