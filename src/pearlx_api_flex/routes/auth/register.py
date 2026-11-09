from flask_restx import fields
from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api


RegisterRequest = auth_api.schema_model(
    "RegisterRequest",
    {
        "type": "object",
        "properties": {
            "firstname": {"description": "First name", "type": "string"},
            "lastname": {"description": "Last name", "type": "string"},
            "email": {"description": "Email", "type": "string"},
            "organization_id": {"description": "Organization ID", "type": "string"},
            "password": {"description": "Password", "type": "string"},
        },
        "required": ["firstname", "lastname", "email", "organization_id", "password"],
        "additionalProperties": False,
    },
)


RegisterResponse = auth_api.model(
    "RegisterResponse",
    {
        "id": fields.String(required=True, description="User ID"),
        "firstname": fields.String(required=True, description="First name"),
        "lastname": fields.String(required=True, description="Last name"),
        "email": fields.String(required=True, description="Email"),
        "organization_id": fields.String(required=True, description="Organization ID"),
    },
)


@auth_api.route("/register")
class AuthRegister(PearlxResource):
    @auth_api.doc("register user")
    @auth_api.expect(RegisterRequest, validate=True)
    @auth_api.marshal_with(RegisterResponse, code=201)
    def post(self):
        """Create a new user"""
        return authService.register(auth_api.payload), 201
