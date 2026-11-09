from dotenv import load_dotenv
from greenlet import greenlet
from locust import HttpUser, constant


load_dotenv()


def get_id():
    return greenlet.getcurrent().minimal_ident


class BaseUser(HttpUser):
    wait_time = constant(0.01)
