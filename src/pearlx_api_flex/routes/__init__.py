from flask_restx import Api

from .ders import ders_api
from .organizations import organizations_api
from .ping import ping_api
from .sites import sites_api
from .users import users_api
from .auth import auth_api


def init_routes():
    authorizations = {
        "Bearer Auth": {"type": "apiKey", "in": "header", "name": "Authorization"},
    }
    api = Api(
        prefix="/api/v1",
        version="0.1",
        title="PearlX Flex API",
        description="",
        doc="/ui",
        security="Bearer Auth",
        authorizations=authorizations,
    )

    api.add_namespace(ping_api)
    api.add_namespace(auth_api)
    api.add_namespace(organizations_api)
    api.add_namespace(users_api)
    api.add_namespace(sites_api)
    api.add_namespace(ders_api)

    return api
