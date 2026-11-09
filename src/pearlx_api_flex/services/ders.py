import numpy as np

from . import on_error, NotFoundException
from ..db.dao import transaction
from ..db.dao.ders import DersDao
from ..db.dao.sites import SitesDao


class DersService:
    def __init__(self):
        self.dersDao = DersDao()
        self.sitesDao = SitesDao()

    @on_error("Can't get der by ID")
    def get_der_by_id(self, der_id):
        der = self.dersDao.get_der_by_id(der_id)
        if der is None:
            raise NotFoundException(f"Can't get der by ID: {der_id}")
        return der

    @on_error("Can't populate ders from timestream db")
    @transaction
    def refresh_ders(self):
        df = self.dersDao.get_sites_ders_datframe_from_timestream()
        df_ders = df.drop(columns=["system_id", "site_name", "site_address"]).replace({np.nan: None})
        ders = {der["der_id"]: der for der in df_ders.to_dict(orient="records")}

        for der in self.dersDao.get_ders_by_der_id_list(ders.keys()):
            site = self.sitesDao.get_site_by_site_id(ders[der.der_id]["site_id"])

            if site is not None:
                ders[der.der_id]["site_id"] = site.id
                der.update(ders.pop(der.der_id))

        for der in ders.values():
            site = self.sitesDao.get_site_by_site_id(der["site_id"])

            if site is not None:
                ders[der["der_id"]]["site_id"] = site.id
            else:
                ders.pop(der["der_id"])

        if ders:
            self.dersDao.create_ders(ders.values())
            return self.dersDao.get_ders_by_der_id_list(ders.keys())

        return []
