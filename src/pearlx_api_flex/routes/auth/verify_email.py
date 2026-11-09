from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api

ReVerifyEmailRequest = auth_api.schema_model(
    "ReVerifyEmailRequest",
    {
        "type": "object",
        "properties": {
            "email": {"description": "Email", "type": "string"},
        },
        "required": ["email"],
        "additionalProperties": False,
    },
)


@auth_api.route("/reverify-email")
class AuthReVerifyEmail(PearlxResource):
    @auth_api.expect(ReVerifyEmailRequest, validate=True)
    def post(self):
        """ReVerify Email."""
        authService.reverify_email(auth_api.payload)
        return "", 200


VerifyEmailTokenRequest = auth_api.schema_model(
    "VerifyEmailTokenRequest",
    {
        "type": "object",
        "properties": {
            "email": {"description": "Email", "type": "string"},
            "token": {"description": "Token", "type": "string"},
        },
        "required": ["email", "token"],
        "additionalProperties": False,
    },
)


@auth_api.route("/verify-email-token")
class AuthVerifyEmailToken(PearlxResource):
    @auth_api.expect(VerifyEmailTokenRequest, validate=True)
    def post(self):
        """Verify Email using token."""
        authService.verify_email_token(auth_api.payload)
        return "", 200
