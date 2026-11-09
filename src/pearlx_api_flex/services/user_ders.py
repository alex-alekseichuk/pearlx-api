from . import (
    on_error,
    IncorrectInputException,
)
from .ders import DersService
from .users import UsersService
from ..db.dao import transaction
from ..db.dao.user_ders import UserDersDao


class UserDersService:
    def __init__(self):
        self.userDersDao = UserDersDao()
        self.usersService = UsersService()
        self.dersService = DersService()

    @on_error("Can't add der to user")
    @transaction
    def add_der_to_user(self, user_id, der_id):
        self.usersService.get_user_by_id(user_id)
        self.dersService.get_der_by_id(der_id)
        user_der = self.userDersDao.get_user_der(user_id, der_id)
        if user_der is not None:
            raise IncorrectInputException(
                f"Can't add der `{der_id}` to user `{user_id}`, duplicate record already exists."
            )
        return self.userDersDao.create_user_der(user_id, der_id)

    @on_error("Can't update user's der access")
    @transaction
    def update_user_der_access(self, user_id, der_id, data):
        self.usersService.check_user_exists(user_id)
        self.dersService.get_der_by_id(der_id)
        return self.userDersDao.update_user_der(user_id, der_id, data)

    @on_error("Can't remove der from user")
    @transaction
    def remove_der_from_user(self, user_id, der_id):
        self.usersService.get_user_by_id(user_id)
        self.dersService.get_der_by_id(der_id)
        self.userDersDao.delete_user_der(user_id, der_id)

    @on_error("Can't remove all ders from user")
    @transaction
    def remove_all_ders_from_user(self, user_id):
        self.usersService.get_user_by_id(user_id)
        self.userDersDao.delete_all_user_ders(user_id)
