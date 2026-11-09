from . import on_error, NotFoundException, IncorrectInputException
from ..db.dao import transaction
from ..db.dao.organizations import OrganizationsDao


class OrganizationsService:
    def __init__(self):
        self.organizationsDao = OrganizationsDao()

    @on_error("Can't get all organizations")
    def get_all_organizations(self):
        return self.organizationsDao.get_all()

    @on_error("Can't get organization by ID")
    def get_organization_by_id(self, organization_id):
        organization = self.check_organization_exists(organization_id)
        return organization

    @on_error("Can't create organization")
    @transaction
    def create_organization(self, data):
        organization = self.organizationsDao.get_by_name(data["name"])
        if organization is not None:
            raise IncorrectInputException(
                f"Can't create organization, duplicate record with name `{data['name']}` " f"already exists."
            )
        return self.organizationsDao.create(data)

    @on_error("Can't delete organization")
    @transaction
    def delete_organization(self, organization_id):
        self.check_organization_exists(organization_id)
        self.organizationsDao.delete(organization_id)

    @on_error("Can't update organization")
    @transaction
    def update_organization(self, organization_id, data):
        self.check_organization_exists(organization_id)
        organization = self.organizationsDao.get_by_name(data["name"])
        if organization and organization.id != organization_id:
            raise IncorrectInputException(
                f"Can't set name `{data['name']}`, duplicate record with such a name already " f"exists."
            )
        return self.organizationsDao.update(organization_id, data)

    def check_organization_exists(self, organization_id):
        organization = self.organizationsDao.get_by_id(organization_id)
        if organization is None:
            raise NotFoundException(f"Can't get organization by ID: {organization_id}")
        return organization
