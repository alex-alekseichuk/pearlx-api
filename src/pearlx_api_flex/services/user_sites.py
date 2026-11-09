from . import (
    on_error,
    IncorrectInputException,
)
from .sites import SitesService
from .user_ders import UserDersService
from .users import UsersService
from ..db.dao import transaction
from ..db.dao.user_sites import UserSitesDao


class UserSitesService:
    def __init__(self):
        self.userSitesDao = UserSitesDao()
        self.userDersService = UserDersService()
        self.usersService = UsersService()
        self.sitesService = SitesService()

    @on_error("Can't add site to user")
    @transaction
    def add_site_to_user(self, user_id, site_id):
        self.usersService.get_user_by_id(user_id)
        site = self.sitesService.get_site_by_id(site_id)
        user_site = self.userSitesDao.get_user_site(user_id, site_id)
        if user_site is not None:
            raise IncorrectInputException(
                f"Can't add site `{site_id}` to user `{user_id}`, duplicate record already exists."
            )
        user_site = self.userSitesDao.create_user_site(user_id, site_id)
        for der in site.ders:
            self.userDersService.add_der_to_user(user_id, der.id)
        return user_site

    @on_error("Can't update user's site access")
    @transaction
    def update_user_site_access(self, user_id, site_id, data):
        self.usersService.get_user_by_id(user_id)
        self.sitesService.get_site_by_id(site_id)
        return self.userSitesDao.update_user_site(user_id, site_id, data)

    @on_error("Can't remove site from user")
    @transaction
    def remove_site_from_user(self, user_id, site_id):
        self.usersService.get_user_by_id(user_id)
        site = self.sitesService.get_site_by_id(site_id)
        for der in site.ders:
            self.userDersService.remove_der_from_user(user_id, der.id)
        self.userSitesDao.delete_user_site(user_id, site_id)

    @on_error("Can't remove all sites from user")
    @transaction
    def remove_all_sites_from_user(self, user_id):
        self.usersService.get_user_by_id(user_id)
        self.userDersService.remove_all_ders_from_user(user_id)
        self.userSitesDao.delete_all_user_sites(user_id)
