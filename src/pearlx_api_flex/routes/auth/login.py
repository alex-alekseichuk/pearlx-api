from flask_restx import fields

from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api

LoginRequest = auth_api.schema_model(
    "LoginRequest",
    {
        "type": "object",
        "properties": {
            "email": {"description": "Email", "type": "string"},
            "password": {"description": "Password", "type": "string"},
        },
        "required": ["email", "password"],
        "additionalProperties": False,
    },
)


LoginResponse = auth_api.model(
    "LoginResponse",
    {
        "token": fields.String(required=True, description="JWT token"),
    },
)


@auth_api.route("/login")
class AuthLogin(PearlxResource):
    @auth_api.doc("login")
    @auth_api.expect(LoginRequest, validate=True)
    @auth_api.marshal_with(LoginResponse, code=200)
    def post(self):
        """Login"""
        return {"token": authService.login(auth_api.payload)}, 200
