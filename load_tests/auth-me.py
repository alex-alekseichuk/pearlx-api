from locust import task
from common.auth import AuthUser


class MeUser(AuthUser):
    @task
    def me(self):
        self.http_get("/auth/me")
