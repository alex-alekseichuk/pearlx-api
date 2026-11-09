from .. import db
from ..models.user import User, UserDer


class UserDersDao(object):
    def get_user_der(self, user_id, der_id):
        return db.session.query(UserDer).filter_by(user_id=user_id, der_id=der_id).first()

    def get_user_ders(self, user_id):
        return db.session.query(User).get(user_id).ders

    def create_user_der(self, user_id, der_id):
        user = db.session.query(User).get(user_id)
        if user is None:
            return
        user_der = UserDer(user_id=user_id, der_id=der_id)
        db.session.add(user_der)
        return user_der

    def update_user_der(self, user_id, der_id, data):
        user_der = self.get_user_der(user_id, der_id)
        if user_der is None:
            return
        user_der.update(data)
        return user_der

    def delete_user_der(self, user_id, der_id):
        user_der = self.get_user_der(user_id, der_id)
        if user_der is None:
            return
        db.session.delete(user_der)

    def delete_all_user_ders(self, user_id):
        user_ders = self.get_user_ders(user_id)
        for user_der in user_ders:
            db.session.delete(user_der)
