from flask_restx import fields, marshal
from ..services import for_admin, for_authenticated, is_admin
from ..services.user_sites import UserSitesService
from ..services.users import UsersService
from ..utils.flask_restx_extensions import PearlxNamespace, PearlxResource


usersService = UsersService()
userSitesService = UserSitesService()

users_api = PearlxNamespace("users", description="USER operations")

UserModel = users_api.model(
    "User",
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

UserForAdminModel = users_api.model(
    "UserForAdmin",
    {
        "id": fields.String(readonly=True, description="The user unique identifier"),
        "firstname": fields.String(required=True, description="The user first name"),
        "lastname": fields.String(required=True, description="The user last name"),
        "email": fields.String(required=True, description="The user email"),
        "phone": fields.String(required=False, description="The user phone"),
        "enabled": fields.Boolean(required=False, description="The user state"),
        "organization_id": fields.String(required=True, description="The user organization unique identifier"),
        "is_admin": fields.Boolean(required=False, description="The user admin or not"),
    },
)

UserPatchModel = users_api.schema_model(
    "UserPatch",
    {
        "type": "object",
        "properties": {
            "firstname": {"description": "The user first name", "type": "string"},
            "lastname": {"description": "The user last name", "type": "string"},
        },
        "anyOf": [{"required": ["firstname"]}, {"required": ["lastname"]}],
        "additionalProperties": False,
    },
)

UserEnableModel = users_api.schema_model(
    "UserEnable",
    {
        "type": "object",
        "required": ["enabled"],
        "properties": {
            "enabled": {"description": "Required state of user", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)

UserAdminModel = users_api.schema_model(
    "UserAdmin",
    {
        "type": "object",
        "required": ["is_admin"],
        "properties": {
            "is_admin": {
                "description": "Required admin role of user",
                "type": "boolean",
            },
        },
        "additionalProperties": False,
    },
)


@users_api.route("")
class UsersList(PearlxResource):
    """Shows a list of all Users, and lets you POST to add new users"""

    @for_authenticated
    @for_admin
    @users_api.doc("list_users")
    @users_api.marshal_list_with(UserForAdminModel)
    def get(self):
        """List all users"""
        return usersService.get_all_users()


@users_api.route("/<string:user_id>")
@users_api.response(404, "User not found")
@users_api.param("user_id", "The user identifier")
class User(PearlxResource):
    """Show a single user item and lets you delete them"""

    @for_authenticated
    @users_api.doc("get_user")
    def get(self, user_id):
        """Load an user by its ID"""
        if is_admin():
            model = UserForAdminModel
        else:
            model = UserModel
        return marshal(usersService.get_user_by_id(user_id), model), 200

    @for_authenticated
    @for_admin
    @users_api.doc("delete_user")
    @users_api.response(204, "User deleted")
    def delete(self, user_id):
        """Delete a user given its identifier"""
        usersService.delete_user(user_id)
        return "", 204

    @for_authenticated
    @users_api.expect(UserPatchModel, validate=True)
    @users_api.marshal_with(UserModel)
    def patch(self, user_id):
        """Update an user given its identifier"""
        return usersService.update_user(user_id, users_api.payload)


@users_api.route("/<string:user_id>/enable")
@users_api.response(404, "User not found")
@users_api.param("user_id", "The user identifier")
class UserEnable(PearlxResource):
    """Control of users' state"""

    @for_authenticated
    @for_admin
    @users_api.doc("enable_user")
    @users_api.expect(UserEnableModel, validate=True)
    @users_api.marshal_with(UserModel)
    def post(self, user_id):
        """Activate or deactivate user"""
        return usersService.update_user(user_id, users_api.payload)


@users_api.route("/<string:user_id>/admin")
@users_api.response(404, "User not found")
@users_api.param("user_id", "The user identifier")
class UserAdmin(PearlxResource):
    """Control of users' role"""

    @for_authenticated
    @for_admin
    @users_api.doc("admin_user")
    @users_api.expect(UserAdminModel, validate=True)
    @users_api.marshal_with(UserModel)
    def post(self, user_id):
        """Activate or deactivate user admin role"""
        return usersService.update_user(user_id, users_api.payload)


@users_api.route("/<string:user_id>/sites")
@users_api.response(404, "User not found")
@users_api.param("user_id", "The user identifier")
class UserSites(PearlxResource):
    @for_authenticated
    @for_admin
    @users_api.doc("remove_all_sites_from_user")
    @users_api.response(204, "All user sites access deleted")
    def delete(self, user_id):
        """Delete user access to all sites"""
        userSitesService.remove_all_sites_from_user(user_id)
        return "", 204
