from src.pearlx_api_flex.services.auth import AuthService
from src.pearlx_api_flex.utils.flask_restx_extensions import PearlxNamespace

authService = AuthService()
auth_api = PearlxNamespace("auth", description="Authentication operations")
