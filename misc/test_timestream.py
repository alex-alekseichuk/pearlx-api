import sys
import os
from pathlib import Path

path = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(path.parent.absolute()))

import datetime
import awswrangler as wr
import numpy as np

from src.pearlx_api_flex.utils.bot3_session import get_bot3_session


class Config:
    def __init__(self, suffix="staging"):
        self.suffix = suffix

    def get(self, key):
        if key == "TSTREAM_DB":
            return "VPPTimestream" + self.suffix
        if key == "TSTREAM_PROPS_TBL":
            return "VPPSiteProperties" + self.suffix
        if key == "TSTREAM_MEASURES_TBL":
            return "VPPSiteMeasurements" + self.suffix


class Logger:
    def error(self, message):
        print(message)


class App:
    config = Config()
    logger = Logger()


app = App()


def get_site_inverter_data_from_timestream(site_id, start_time, end_time, derid_inverter):
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
        print(query)
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


def inverter_query():
    query = """
        SELECT
            site_id, serial_number,
            CAST(timestamp AS timestamp) AS timestamp,
            der_controller_id,
            inverter_id as derid_inverter,
            inverter_operating_mode,
            inverter_fault, amb_temp_f, from_grid_watts, load_watts, inverter_feedin_meter,
            inverter_production_meter, inverter_purchased_meter, inverter_consumption_meter
        FROM
            VPPTimestreamstaging.VPPSiteMeasurementsstaging
        WHERE
            site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
            AND inverter_id IS NOT NULL
            AND inverter_id = '83273c90-c0a8-44ec-8b15-87d10d31b5ac'
            AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
            AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
        ORDER BY
            timestamp
    """

    df_measurements = wr.timestream.query(sql=query, boto3_session=get_bot3_session())
    df_measurements = df_measurements.replace({np.nan: None})
    measurements = df_measurements.to_dict(orient="records")

    print(measurements)


def storage_query():
    query = """
    SELECT
                t1.*, t2.storage_status, t2.storage_id
            FROM
            (
                SELECT
                    site_id, der_controller_id, batt_id AS derid_battery, serial_number,
                    timestamp, batt_system_status,batt_operating_mode,batt_active_power,batt_current_ac,batt_frequency_ac,batt_reactive_power,batt_soc,batt_fullpackenergyavailable,batt_soh,batt_temp_f,batt_voltage_ac,batt_voltage_dc,battery_fault
                FROM
                    VPPTimestreamstaging.VPPSiteMeasurementsstaging
                WHERE
                    site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
                    AND batt_id = 'f0a42cec-fb1c-406f-a173-0ce4a66980b3'
                    AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
                    AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
            ) t1,
            (
                SELECT
                    storage_status, timestamp, site_id, storage_id
                FROM
                    VPPTimestreamstaging.VPPSiteMeasurementsstaging
                WHERE
                    site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
                    AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
                    AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
            ) t2
            WHERE
                t1.timestamp = t2.timestamp AND t1.site_id = t2.site_id AND t1.der_controller_id = t2.storage_id
            ORDER BY
                t1.timestamp
    """

    query = """
                SELECT
                    site_id, der_controller_id, batt_id AS derid_battery, serial_number,
                    timestamp, batt_system_status,batt_operating_mode,batt_active_power,batt_current_ac,
                    batt_frequency_ac,batt_reactive_power,batt_soc,batt_fullpackenergyavailable,batt_soh,
                    batt_temp_f,batt_voltage_ac,batt_voltage_dc,battery_fault
                FROM
                    VPPTimestreamstaging.VPPSiteMeasurementsstaging
                WHERE
                    site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
                    AND batt_id = 'f0a42cec-fb1c-406f-a173-0ce4a66980b3'
                    AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
                    AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
            
    """

    query = """
            SELECT
                t1.*, t2.storage_status, t2.storage_id
            FROM
            (
                SELECT
                    site_id, der_controller_id, batt_id AS derid_battery, serial_number,
                    timestamp, batt_system_status,batt_operating_mode,batt_active_power,batt_current_ac,batt_frequency_ac,batt_reactive_power,batt_soc,batt_fullpackenergyavailable,batt_soh,batt_temp_f,batt_voltage_ac,batt_voltage_dc,battery_fault
                FROM
                    VPPTimestreamstaging.VPPSiteMeasurementsstaging
                WHERE
                    site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
                    AND batt_id = '3f61ef97-665a-4f27-9d59-70a083a36ffd'
                    AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
                    AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
            ) t1,
            (
                SELECT
                    storage_status, timestamp, site_id, storage_id
                FROM
                    VPPTimestreamstaging.VPPSiteMeasurementsstaging
                WHERE
                    site_id = '72304cb5-7891-467e-b6c3-8a5a84e0a6a4'
                    AND CAST(timestamp AS timestamp) >= TIMESTAMP '2022-09-06 00:00:00'
                    AND CAST(timestamp AS timestamp) <= TIMESTAMP '2022-09-07 13:00:00'
            ) t2
            WHERE
                t1.timestamp = t2.timestamp AND t1.site_id = t2.site_id AND t1.der_controller_id = t2.storage_id
            ORDER BY
                t1.timestamp
        """

    df_measurements = wr.timestream.query(sql=query, boto3_session=get_bot3_session())
    df_measurements = df_measurements.replace({np.nan: None})
    measurements = df_measurements.to_dict(orient="records")

    print(measurements)


if __name__ == "__main__":
    # measurements = get_site_inverter_data_from_timestream(
    #     "72304cb5-7891-467e-b6c3-8a5a84e0a6a4",
    #     "2022-09-06T00:00:00.000Z",
    #     "2022-09-07T13:00:00.000Z",
    #     "83273c90-c0a8-44ec-8b15-87d10d31b5ac",
    # )
    # print(measurements)

    storage_query()
