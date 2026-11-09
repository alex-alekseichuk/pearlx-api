from .. import db
from ..models.user import User, UsagePlan, ApiKey


class UsersDao(object):
    def get_all(self):
        return db.session.query(User).all()

    def get_user_by_id(self, user_id):
        return db.session.query(User).get(user_id)

    def get_user_by_email(self, email):
        return db.session.query(User).filter_by(email=email).first()

    def get_user_by_reset_token(self, reset_token):
        return db.session.query(User).filter_by(reset_token=reset_token).first()

    def createUser(self, user_data):
        user = User(**user_data)
        db.session.add(user)
        return user

    def update(self, user_id, data):
        user = self.get_user_by_id(user_id)
        user.update(data)
        return user

    def delete(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)

    def createUsagePlan(self, user):
        user.usage_plan = UsagePlan(user=user, name=user.email)
        return user.usage_plan

    def createApiKey(self, usage_plan, token):
        usage_plan.api_key = ApiKey(usage_plan=usage_plan, token=token)

    def deleteApiKey(self, usage_plan):
        if usage_plan and usage_plan.api_key:
            db.session.delete(usage_plan.api_key)
