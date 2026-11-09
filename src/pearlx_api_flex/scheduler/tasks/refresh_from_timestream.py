from src.pearlx_api_flex.services.sites import SitesService
from src.pearlx_api_flex.services.ders import DersService


def refresh_from_timestream(app):
    """Populate sites and ders from timestream db"""
    with app.app_context():
        SitesService().refresh_sites()
        DersService().refresh_ders()
