import os
import requests
from locust import events
from . import BaseUser

token = None


def get_token(host):
    r = requests.post(
        host + "/auth/login",
        json={
            "email": os.getenv("ADMIN_EMAIL", "admin@some.com"),
            "password": os.getenv("ADMIN_PASSWORD", "add_pass"),

        },
    )
    return r.json()["token"]


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global token
    token = get_token(environment.host)


class AuthUser(BaseUser):
    def http_get(self, uri):
        global token
        return self.client.get(uri, headers={"Authorization": f"Bearer {token}"})

    def http_post(self, uri, data):
        global token
        return self.client.post(uri, data, headers={"Authorization": f"Bearer {token}"})
