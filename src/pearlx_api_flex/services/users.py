from . import (
    on_error,
    NotFoundException,
)
from ..db.dao import transaction
from ..db.dao.users import UsersDao


class UsersService:
    def __init__(self):
        self.usersDao = UsersDao()

    @on_error("Can't get all users")
    def get_all_users(self):
        return self.usersDao.get_all()

    @on_error("Can't get user by ID")
    def get_user_by_id(self, user_id):
        user = self.check_user_exists(user_id)
        return user

    @on_error("Can't delete user")
    @transaction
    def delete_user(self, user_id):
        self.check_user_exists(user_id)
        self.usersDao.delete(user_id)

    @on_error("Can't update user")
    @transaction
    def update_user(self, user_id, data):
        self.check_user_exists(user_id)
        return self.usersDao.update(user_id, data)

    def check_user_exists(self, user_id):
        user = self.usersDao.get_user_by_id(user_id)
        if user is None:
            raise NotFoundException(f"Can't get user by ID: {user_id}")
        return user
