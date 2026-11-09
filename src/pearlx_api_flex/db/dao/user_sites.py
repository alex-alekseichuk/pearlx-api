from .. import db
from ..models.user import User, UserSite


class UserSitesDao(object):
    def get_user_site(self, user_id, site_id):
        return db.session.query(UserSite).filter_by(user_id=user_id, site_id=site_id).first()

    def get_user_sites(self, user_id):
        return db.session.query(User).get(user_id).sites

    def create_user_site(self, user_id, site_id):
        user = db.session.query(User).get(user_id)
        if user is None:
            return
        user_site = UserSite(user_id=user_id, site_id=site_id)
        db.session.add(user_site)
        return user_site

    def update_user_site(self, user_id, site_id, data):
        user_site = self.get_user_site(user_id, site_id)
        if user_site is None:
            return
        user_site.update(data)
        return user_site

    def delete_user_site(self, user_id, site_id):
        user_site = self.get_user_site(user_id, site_id)
        if user_site is None:
            return
        db.session.delete(user_site)

    def delete_all_user_sites(self, user_id):
        user_sites = self.get_user_sites(user_id)
        for user_site in user_sites:
            db.session.delete(user_site)
