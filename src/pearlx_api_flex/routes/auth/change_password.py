from src.pearlx_api_flex.services import for_authenticated
from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api


ChangePasswordRequest = auth_api.schema_model(
    "ChangePasswordRequest",
    {
        "type": "object",
        "properties": {
            "new-password": {"description": "Password", "type": "string"},
        },
        "required": ["new-password"],
        "additionalProperties": False,
    },
)


@auth_api.route("/change-password")
class AuthChangePassword(PearlxResource):
    @for_authenticated
    @auth_api.doc("change-password", security="Bearer Auth")
    @auth_api.expect(ChangePasswordRequest, validate=True)
    @auth_api.response(204, "Password changed")
    def post(self):
        """Change password for currently logged-in user."""
        authService.change_password(auth_api.payload)
        return "", 204
