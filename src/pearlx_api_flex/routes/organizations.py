from flask_restx import fields

from ..services import for_admin, for_authenticated, for_organization_member
from ..services.organizations import OrganizationsService
from ..utils.flask_restx_extensions import PearlxNamespace, PearlxResource

organizationsService = OrganizationsService()

organizations_api = PearlxNamespace("organizations", description="ORGANIZATION operations")

OrganizationModel = organizations_api.model(
    "OrganizationModel",
    {
        "id": fields.String(readonly=True, description="The organization unique identifier"),
        "name": fields.String(required=True, description="The organization name"),
        "address": fields.String(required=True, description="The organization address"),
        "phone": fields.String(required=False, description="The organization phone"),
    },
)

OrganizationValidationModel = organizations_api.schema_model(
    "OrganizationValidationModel",
    {
        "type": "object",
        "properties": {
            "name": {"description": "The organization name", "type": "string"},
            "address": {"description": "The organization address", "type": "string"},
            "phone": {"description": "The organization phone"},
        },
        "required": ["name"],
        "additionalProperties": False,
    },
)


@organizations_api.route("")
class OrganizationsList(PearlxResource):
    """Shows a list of all Organizations, and lets you POST to add new organizations"""

    @for_authenticated
    @for_admin
    @organizations_api.doc("list_organizations")
    @organizations_api.marshal_list_with(OrganizationModel)
    def get(self):
        """List all organizations"""
        return organizationsService.get_all_organizations()

    @for_authenticated
    @for_admin
    @organizations_api.doc("create_organization", security="Bearer Auth")
    @organizations_api.expect(OrganizationValidationModel, validate=True)
    @organizations_api.marshal_with(OrganizationModel, code=201)
    def post(self):
        """Create a new organization"""
        return organizationsService.create_organization(organizations_api.payload), 201


@organizations_api.route("/<string:organization_id>")
@organizations_api.response(404, "Organization not found")
@organizations_api.param("organization_id", "The organization identifier")
class Organization(PearlxResource):
    """Show a single organization item and lets you delete them"""

    @for_authenticated
    @for_organization_member
    @organizations_api.doc("get_organization")
    @organizations_api.marshal_with(OrganizationModel)
    def get(self, organization_id):
        """Load an organization by its ID"""
        return organizationsService.get_organization_by_id(organization_id)

    @for_authenticated
    @for_admin
    @organizations_api.doc("delete_organization", security="Bearer Auth")
    @organizations_api.response(204, "Organization deleted")
    def delete(self, organization_id):
        """Delete a organization given its identifier"""
        organizationsService.delete_organization(organization_id)
        return "", 204

    @for_authenticated
    @for_admin
    @organizations_api.doc("update_organization", security="Bearer Auth")
    @organizations_api.expect(OrganizationValidationModel, validate=True)
    @organizations_api.marshal_with(OrganizationModel)
    def put(self, organization_id):
        """Update an organization given its identifier"""
        return organizationsService.update_organization(organization_id, organizations_api.payload)
