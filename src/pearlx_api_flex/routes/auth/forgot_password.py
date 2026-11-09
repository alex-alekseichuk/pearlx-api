from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api

ForgotPasswordRequest = auth_api.schema_model(
    "ForgotPasswordRequest",
    {
        "type": "object",
        "properties": {
            "email": {"description": "Email", "type": "string"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
)


@auth_api.route("/forgot-password")
class AuthForgotPassword(PearlxResource):
    @auth_api.expect(ForgotPasswordRequest, validate=True)
    def post(self):
        """Forgot password."""
        authService.forgot_password(auth_api.payload)
        return "", 200


ResetPasswordRequest = auth_api.schema_model(
    "ResetPasswordRequest",
    {
        "type": "object",
        "properties": {
            "token": {"description": "Token", "type": "string"},
            "password": {"description": "New password", "type": "string"},
        },
        "required": ["token", "password"],
        "additionalProperties": False,
    },
)


@auth_api.route("/reset-password")
class AuthResetPassword(PearlxResource):
    @auth_api.expect(ResetPasswordRequest, validate=True)
    def post(self):
        """Reset password."""
        authService.reset_password(auth_api.payload)
        return "", 200
