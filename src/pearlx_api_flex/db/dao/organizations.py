from .. import db
from ..models.organization import Organization


class OrganizationsDao(object):
    def get_all(self):
        return db.session.query(Organization).all()

    def get_by_id(self, organization_id):
        try:
            return db.session.query(Organization).get(organization_id)
        except:
            return None

    def get_by_name(self, name):
        return db.session.query(Organization).filter_by(name=name).first()

    def create(self, data):
        organization = Organization(**data)
        db.session.add(organization)
        return organization

    def update(self, organization_id, data):
        organization = self.get_by_id(organization_id)
        organization.update(data)
        return organization

    def delete(self, organization_id):
        organization = self.get_by_id(organization_id)
        if organization:
            # for user in organization.users:
            #     user.disable()
            db.session.delete(organization)
