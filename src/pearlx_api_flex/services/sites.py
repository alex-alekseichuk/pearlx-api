import numpy as np

from flask import g, current_app as app

from . import (
    on_error,
    NotFoundException,
    IncorrectInputException,
    is_admin,
)
from ..db.dao import transaction
from ..db.dao.sites import SitesDao
from ..db.dao.ders import DersDao
from ..utils.der_api import get_der, post_der


class SitesService:
    def __init__(self):
        self.sitesDao = SitesDao()
        self.dersDao = DersDao()

    @on_error("Can't get all sites")
    def get_all_sites(self):
        if is_admin():
            return self.sitesDao.get_all()
        else:
            user_id = g.context["user_id"]
            return self.sitesDao.get_sites_by_user_id(user_id)

    @on_error("Can't get site by ID")
    def get_site_by_id(self, site_id):
        return self.check_site_exists(site_id)

    @on_error("Can't populate sites from timestream db")
    @transaction
    def refresh_sites(self):
        df = self.dersDao.get_sites_ders_datframe_from_timestream()
        df_sites = df.drop_duplicates(subset=["site_id"]).drop(columns=["der_id", "der_type"]).replace({np.nan: None})
        sites = {site["site_id"]: site for site in df_sites.to_dict(orient="records")}

        for site in self.sitesDao.get_sites_by_site_id_list(sites.keys()):
            site.update(sites.pop(site.site_id))

        if sites:
            self.sitesDao.create_sites(sites.values())
            return self.sitesDao.get_sites_by_site_id_list(sites.keys())

        return []

    @on_error("Can't get site properties by ID")
    def get_site_properties_by_id(self, site_id):
        site = self.check_site_exists(site_id)
        properties = self.sitesDao.get_site_properties_from_timestream(site.site_id)
        if properties is None:
            raise NotFoundException(f"Can't get site properties by ID: {site_id}")
        return properties

    @on_error("Can't get site storage properties by ID and serials")
    def get_site_storage_properties(self, site_id, serials):
        site = self.check_site_exists(site_id)
        properties = self.sitesDao.get_site_storage_properties_from_timestream(site.site_id, serials)
        if properties is None:
            raise NotFoundException(f"Can't get site storage properties by ID: {site_id} and serials: {serials}")
        return properties

    @on_error("Can't update site")
    @transaction
    def update_site(self, site_id, data):
        self.check_site_exists(site_id)
        return self.sitesDao.update(site_id, data)

    @on_error("Can't update der")
    @transaction
    def update_der(self, site_id, der_id, data):
        self.check_site_exists(site_id)
        self.check_der_exists(site_id, der_id)
        return self.dersDao.update(der_id, data)

    def check_site_exists(self, site_id):
        site = self.sitesDao.get_site_by_id(site_id)
        if site is None:
            app.logger.warning(f"Can't get site by ID: {site_id}")
            raise NotFoundException(f"Can't get site by ID: {site_id}")
        return site

    def check_der_exists(self, site_id, der_id):
        der = self.dersDao.get_der_by_id(der_id)
        if der is None:
            app.logger.warning(f"Can't get der by ID: {der_id}")
            raise NotFoundException(f"Can't get der by ID: {der_id}")
        if str(der.site_id) != site_id:
            app.logger.warning("Der doesn't belong to site")
            raise IncorrectInputException("Der doesn't belong to site")
        return der

    @on_error("Can't get site storage data by ID and storages der_id")
    def get_site_storage_data(self, site_id, start_time, end_time, battery_id):
        site = self.check_site_exists(site_id)
        der = self.check_der_exists(site_id, battery_id)
        measurements = self.sitesDao.get_site_storage_data_from_timestream(
            site.site_id, start_time, end_time, der.der_id
        )
        return measurements

    @on_error("Can't get site inverter data by site_id and inverter_id")
    def get_site_inverter_data(self, site_id, start_time, end_time, inverter_id):
        site = self.check_site_exists(site_id)
        der = self.check_der_exists(site_id, inverter_id)
        measurements = self.sitesDao.get_site_inverter_data_from_timestream(
            site.site_id, start_time, end_time, der.der_id
        )
        return measurements

    @on_error("Can't get ders by site ID")
    def get_ders_by_site_id(self, site_id):
        self.check_site_exists(site_id)
        if is_admin():
            return self.dersDao.get_ders_by_site_id(site_id)
        else:
            user_id = g.context["user_id"]
            return self.dersDao.get_ders_by_site_id(site_id, user_id)

    @on_error("Can't get der by site ID and der ID")
    def get_der(self, site_id, der_id):
        self.check_site_exists(site_id)
        return self.check_der_exists(site_id, der_id)

    @on_error("Can't schedule der command")
    def schedule_der_command(self, command, site_id, der_id, data):
        self.check_site_exists(site_id)
        der = self.check_der_exists(site_id, der_id)
        data["derId"] = der.der_id
        res = post_der(f"/commands/{command}", data)
        return res.json()

    @on_error("Can't cancel der command")
    def cancel_der_command(self, site_id, data):
        self.check_site_exists(site_id)
        post_der("/commands/cancel-der-event", data)
        return

    @on_error("Can't get event")
    def get_event(self, site_id, event_id):
        self.check_site_exists(site_id)
        res = get_der(f"/der-events/{event_id}")
        return res.json()
