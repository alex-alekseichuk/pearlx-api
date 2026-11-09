import awswrangler as wr
from flask import current_app as app
from src.pearlx_api_flex.utils.bot3_session import get_bot3_session

from .. import db
from ..models.site import Der
from ..models.user import User


class DersDao(object):
    def get_der_by_id(self, der_id):
        return db.session.query(Der).get(der_id)

    def get_ders_by_site_id(self, site_id, user_id=None):
        if user_id is not None:
            user = db.session.query(User).get(user_id)
            return [
                user_der.der
                for user_der in user.ders
                if str(user_der.der.site_id) == site_id and user_der.read_enabled and user_der.der.enabled
            ]
        return db.session.query(Der).filter_by(site_id=site_id).all()

    def get_ders_by_der_id_list(self, der_id_list):
        return db.session.query(Der).filter(Der.der_id.in_(der_id_list)).all()

    def create_ders(self, ders):
        db.session.add_all([Der(**der) for der in ders])

    def get_sites_ders_datframe_from_timestream(self):
        field_batt = "batt_id"
        field_inverter = "inverter_id"
        field_storage = "storage_id"

        query_1 = f"""
            SELECT
                site_id, system_id, site_name, site_address, time
            FROM
            (
                SELECT
                    site_id, site_name, time, system_id, site_address,
                    ROW_NUMBER() OVER (PARTITION BY site_id ORDER BY time desc) AS RowNumber
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}
                WHERE
                    site_id<>'none'
            ) AS a
            WHERE
                a.RowNumber = 1 ORDER BY time desc"""

        query_2 = (
            """
            SELECT
                site_id, {0}, time, system_id
            FROM
            (
                SELECT
                    site_id, {0}, time, system_id, ROW_NUMBER() OVER (PARTITION BY {0} ORDER BY time desc) AS RowNumber
                FROM
                    """
            + f"{app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}"
            + """
                WHERE
                    site_id<>'none' AND {0} is not NULL
            ) a
            WHERE
                a.RowNumber = 1 ORDER BY {0}"""
        )

        query_3 = f"""
            SELECT
                t1.site_id, t1.system_id, t2.site_name, t2.site_address, {field_batt} AS der_id, 'battery' AS der_type
            FROM
                ({query_2.format(field_batt)}) AS t1, ({query_1}) AS t2
            WHERE
                t1.system_id = t2.system_id AND t1.site_id = t2.site_id
            UNION ALL
            SELECT
                t1.site_id, t1.system_id, t2.site_name, t2.site_address, {field_inverter} AS der_id, 'inverter' AS der_type
            FROM
                ({query_2.format(field_inverter)}) AS t1, ({query_1}) AS t2
            WHERE
                t1.system_id = t2.system_id AND t1.site_id = t2.site_id
            UNION ALL
            SELECT
                t1.site_id, t1.system_id, t2.site_name, t2.site_address, {field_storage} AS der_id, 'storage' AS der_type
            FROM
                ({query_2.format(field_storage)}) AS t1, ({query_1}) AS t2
            WHERE
                t1.system_id = t2.system_id AND t1.site_id = t2.site_id"""

        return wr.timestream.query(
            sql=query_3.format(
                field_batt,
                query_2.format(field_batt),
                query_1,
                field_inverter,
                query_2.format(field_inverter),
                field_storage,
                query_2.format(field_storage),
            ),
            boto3_session=get_bot3_session(),
        )

    def update(self, der_id, data):
        der = self.get_der_by_id(der_id)
        der.update(data)
        return der
