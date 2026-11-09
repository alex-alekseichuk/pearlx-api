import datetime
import awswrangler as wr
import numpy as np
from flask import current_app as app

from src.pearlx_api_flex.utils.bot3_session import get_bot3_session

from .. import db
from ..models.site import Site
from ..models.user import User


class SitesDao(object):
    def get_all(self):
        return db.session.query(Site).all()

    def get_site_by_id(self, site_id):
        return db.session.query(Site).get(site_id)

    def get_site_by_site_id(self, site_id):
        return db.session.query(Site).filter_by(site_id=site_id).first()

    def get_sites_by_user_id(self, user_id):
        user = db.session.query(User).get(user_id)
        return [user_site.site for user_site in user.sites if user_site.read_enabled and user_site.site.enabled]

    def get_sites_by_site_id_list(self, site_id_list):
        return db.session.query(Site).filter(Site.site_id.in_(site_id_list)).all()

    def create_sites(self, sites):
        db.session.add_all([Site(**site) for site in sites])

    def get_site_properties_from_timestream(self, site_id):
        query = f"""
            SELECT
                system_timezone, site_name, system_id as derid_system, location_latitude, location_longitude,
                site_address, iou_utility, iou_circuit_name
            FROM
            (
                SELECT
                    system_timezone, site_name, system_id, location_latitude, location_longitude,
                    site_address, iou_utility, iou_circuit_name, time,
                    ROW_NUMBER() OVER (PARTITION BY site_id ORDER BY time desc) AS RowNumber
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}
                WHERE
                    site_id = '{site_id}') AS a
            WHERE
                a.RowNumber = 1 ORDER BY time desc"""
        df_properties = wr.timestream.query(sql=query, boto3_session=get_bot3_session())
        df_properties = df_properties.replace({np.nan: None})
        return df_properties.to_dict(orient="records")

    def get_site_storage_properties_from_timestream(self, site_id, serials):
        if serials:
            serials = ", ".join([f"'{s}'" for s in serials])
        query = f"""
            SELECT
                t1.site_id, t1.serial_number, t1.derid_battery, t2.derid_storage, t3.derid_inverter, t1.batt_model,
                t1.batt_manufacture, t1.batt_rated_power, t1.batt_rated_capacity, t1.min_operating_temperature,
                t1.max_operating_temperature, t1.batt_rte
            FROM
            (
                SELECT DISTINCT
                    measure_value::varchar as serial_number, batt_id as derid_battery, batt_model,
                    manufacture as batt_manufacture, batt_rated_power, batt_rated_capacity, der_controller_id,
                    min_operating_temperature, max_operating_temperature, batt_rte, site_id
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}
                WHERE
                    site_id = '{site_id}'{f" AND measure_value::varchar IN ({serials})" if serials else ""}
            ) t1,
            (
                SELECT DISTINCT
                    storage_id as derid_storage, der_controller_id
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}
                WHERE
                    site_id = '{site_id}' AND storage_id is NOT NULL
            ) t2,
            (
                SELECT DISTINCT
                    inverter_id as derid_inverter, der_controller_id
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_PROPS_TBL')}
                WHERE
                    site_id = '{site_id}' AND inverter_id is NOT NULL
            ) t3
            WHERE
                t1.der_controller_id = t2.derid_storage AND t2.der_controller_id = t3.der_controller_id"""
        try:
            df_properties = wr.timestream.query(sql=query, boto3_session=get_bot3_session())
            properties = df_properties.to_dict(orient="records")
        except Exception:
            properties = None
        return properties

    def update(self, site_id, data):
        site = self.get_site_by_id(site_id)
        site.update(data)
        return site

    def get_site_storage_data_from_timestream(self, site_id, start_time, end_time, derid_battery=None):
        session = get_bot3_session()

        storage_field_list = [
            "batt_system_status",
            "batt_operating_mode",
            "batt_active_power",
            "batt_current_ac",
            "batt_frequency_ac",
            "batt_reactive_power",
            "batt_soc",
            "batt_fullpackenergyavailable",
            "batt_soh",
            "batt_temp_f",
            "batt_voltage_ac",
            "batt_voltage_dc",
            "battery_fault",
        ]

        # Get All Field Names from the table
        df_all_field_name = wr.timestream.query(
            sql=f"""DESCRIBE {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_MEASURES_TBL')}""",
            boto3_session=session,
        )
        # Convert returned fields into a list
        all_field_list = df_all_field_name["Column"].tolist()

        # Get field list intersection with fields from table
        storage_field_shortlist = [field for field in storage_field_list if field in all_field_list]

        storage_fields = "{}".format(",".join(storage_field_shortlist))

        start_time = datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

        query = f"""
            SELECT
                t1.*, t2.storage_status, t2.storage_id
            FROM
            (
                SELECT
                    site_id, der_controller_id, batt_id AS derid_battery, serial_number,
                    timestamp, {storage_fields}
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_MEASURES_TBL')}
                WHERE
                    site_id = '{site_id}'
                    {f"AND batt_id = '{derid_battery}'" if derid_battery else ""}
                    {f"AND CAST(timestamp AS timestamp) >= TIMESTAMP '{start_time}'" if start_time else ""}
                    {f"AND CAST(timestamp AS timestamp) <= TIMESTAMP '{end_time}'" if end_time else ""}
            ) t1,
            (
                SELECT
                    storage_status, timestamp, site_id, storage_id
                FROM
                    {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_MEASURES_TBL')}
                WHERE
                    site_id = '{site_id}'
                    {f"AND CAST(timestamp AS timestamp) >= TIMESTAMP '{start_time}'" if start_time else ""}
                    {f"AND CAST(timestamp AS timestamp) <= TIMESTAMP '{end_time}'" if end_time else ""}
            ) t2
            WHERE
                t1.timestamp = t2.timestamp AND t1.site_id = t2.site_id AND t1.der_controller_id = t2.storage_id
            ORDER BY
                t1.timestamp"""
        try:
            app.logger.debug(query)
            df_measurements = wr.timestream.query(sql=query, boto3_session=session)
            df_measurements = df_measurements.replace({np.nan: None})
            measurements = df_measurements.to_dict(orient="records")
        except Exception as err:
            app.logger.error(
                f"get_site_storage_data_from_timestream site ID: {site_id}, der ID: {derid_battery}, from: {start_time}, to: {end_time}"
            )
            app.logger.error(err)
            measurements = []
        return measurements

    def get_site_inverter_data_from_timestream(self, site_id, start_time, end_time, derid_inverter):
        session = get_bot3_session()

        inverter_data_list = [
            "inverter_operating_mode",
            "inverter_fault",
            "amb_temp_f",
            "from_grid_watts",
            "load_watts",
            "inverter_feedin_meter",
            "inverter_production_meter",
            "inverter_purchased_meter",
            "inverter_consumption_meter",
        ]

        # Get All Field Names from the table
        df_all_field_name = wr.timestream.query(
            sql=f"""DESCRIBE {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_MEASURES_TBL')}""",
            boto3_session=session,
        )
        # Convert returned fields into a list
        all_field_list = df_all_field_name["Column"].tolist()

        # Get field list intersection with fields from table
        inverter_data_shortlist = [field for field in inverter_data_list if field in all_field_list]
        inverter_fields = ",".join(inverter_data_shortlist)

        start_time = datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")

        query = f"""
            SELECT
                site_id, serial_number,
                CAST(timestamp AS timestamp) AS timestamp,
                der_controller_id,
                inverter_id as derid_inverter,
                {inverter_fields}
            FROM
                {app.config.get('TSTREAM_DB')}.{app.config.get('TSTREAM_MEASURES_TBL')}
            WHERE
                site_id = '{site_id}'
                AND inverter_id IS NOT NULL
                {f"AND inverter_id = '{derid_inverter}'" if derid_inverter else ""}
                {f"AND CAST(timestamp AS timestamp) >= TIMESTAMP '{start_time}'"}
                {f"AND CAST(timestamp AS timestamp) <= TIMESTAMP '{end_time}'"}
            ORDER BY
                timestamp"""
        try:
            app.logger.debug(query)
            df_measurements = wr.timestream.query(sql=query, boto3_session=session)
            df_measurements = df_measurements.replace({np.nan: None})
            measurements = df_measurements.to_dict(orient="records")
        except Exception as err:
            app.logger.error(
                f"get_site_inverter_data_from_timestream site ID: {site_id}, der ID: {derid_inverter}, from: {start_time}, to: {end_time}"
            )
            app.logger.error(err)
            measurements = []
        return measurements
