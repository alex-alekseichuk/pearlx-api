from flask_restx import fields

from ..services import for_admin, for_authenticated
from ..services.user_ders import UserDersService, DersService
from ..utils.flask_restx_extensions import PearlxResource, PearlxNamespace

userDersService = UserDersService()
dersService = DersService()

ders_api = PearlxNamespace("ders", description="Ders and user access")


UpdateUserDerRequest = ders_api.schema_model(
    "UpdateUserDer",
    {
        "type": "object",
        "required": ["read_enabled", "write_enabled"],
        "properties": {
            "read_enabled": {"description": "Allow user to read", "type": "boolean"},
            "write_enabled": {"description": "Allow user to write", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)

DerModel = ders_api.model(
    "Der",
    {
        "id": fields.String(readonly=True, description="The der unique identifier"),
        "enabled": fields.Boolean(required=True, description="The der state"),
        "der_type": fields.String(required=True, description="The der type"),
        "site_id": fields.String(required=True, description="The site identifier"),
    },
)

DerEnableModel = ders_api.schema_model(
    "DerEnable",
    {
        "type": "object",
        "required": ["enabled"],
        "properties": {
            "enabled": {"description": "Required state of der", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)


@ders_api.route("/<string:der_id>/users/<string:user_id>")
@ders_api.response(404, "User not found")
@ders_api.param("user_id", "The user identifier")
@ders_api.param("der_id", "The der identifier")
class DerUser(PearlxResource):
    """Manage user's access to the der"""

    @for_authenticated
    @for_admin
    @ders_api.expect(UpdateUserDerRequest, validate=True)
    def patch(self, user_id, der_id):
        """Update a user's access on der"""
        userDersService.update_user_der_access(user_id, der_id, ders_api.payload)
        return "", 200


@ders_api.route("/refresh")
class DerRefresh(PearlxResource):
    """Load and populate ders from timestream db"""

    @for_authenticated
    @for_admin
    @ders_api.doc("refresh_ders")
    @ders_api.marshal_list_with(DerModel)
    def post(self):
        """Start refreshing of ders"""
        return dersService.refresh_ders()
