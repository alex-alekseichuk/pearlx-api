from src.pearlx_api_flex.services import for_authenticated
from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxResource

from .auth_api import authService, auth_api


@auth_api.route("/logout")
class AuthLogout(PearlxResource):
    @for_authenticated
    @auth_api.doc("logout", security="Bearer Auth")
    @auth_api.response(204, "User logged out")
    def post(self):
        """Logout"""
        authService.logout()
        return "", 204
