from flask_restx import fields

from src.pearlx_api_flex.services import for_authenticated
from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api


MeResponse = auth_api.model(
    "MeResponse",
    {
        "id": fields.String(readonly=True, description="The user unique identifier"),
        "firstname": fields.String(required=True, description="The user first name"),
        "lastname": fields.String(required=True, description="The user last name"),
        "email": fields.String(required=True, description="The user email"),
        "phone": fields.String(required=False, description="The user phone"),
        "enabled": fields.Boolean(required=False, description="The user state"),
        "organization_id": fields.String(required=True, description="The user organization unique identifier"),
    },
)


@auth_api.route("/me")
class AuthMe(PearlxResource):
    @for_authenticated
    @auth_api.doc("me", security="Bearer Auth")
    @auth_api.marshal_with(MeResponse, code=200)
    def get(self):
        """Info about currently logged-in user."""
        return authService.get_info_about_me()
