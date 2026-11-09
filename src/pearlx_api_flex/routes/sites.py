from flask import request
from flask_restx import fields, reqparse

from ..services import for_admin, for_authenticated, for_site_owner, for_der_owner
from ..services.user_sites import UserSitesService
from ..services.sites import SitesService
from ..utils.flask_restx_extensions import PearlxResource, PearlxNamespace

userSitesService = UserSitesService()
sitesService = SitesService()

sites_api = PearlxNamespace("sites", description="Sites and user access")

UpdateUserSiteRequest = sites_api.schema_model(
    "UpdateUserSite",
    {
        "type": "object",
        "required": ["read_enabled", "write_enabled"],
        "properties": {
            "read_enabled": {"description": "Allow user to read", "type": "boolean"},
            "write_enabled": {"description": "Allow user to write", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)

SiteModel = sites_api.model(
    "Site",
    {
        "id": fields.String(readonly=True, description="The site unique identifier"),
        "enabled": fields.Boolean(required=True, description="The site state"),
        "site_name": fields.String(required=True, description="The site name"),
        "site_address": fields.String(required=True, description="The site address"),
        "system_id": fields.String(required=True, description="The site system identifier"),
    },
)

SitePropertiesModel = sites_api.model(
    "SiteProperties",
    {
        "system_timezone": fields.String(readonly=True, description="The site system_timezone"),
        "site_name": fields.String(readonly=True, description="The site name"),
        "derid_system": fields.String(readonly=True, description="The site system id"),
        "location_latitude": fields.String(readonly=True, description="The site location_latitude"),
        "location_longitude": fields.String(readonly=True, description="The site location_longitude"),
        "site_address": fields.String(required=True, description="The site address"),
        "iou_utility": fields.String(required=True, description="The site iou_utility"),
        "iou_circuit_name": fields.String(required=True, description="The site iou_circuit_name"),
    },
)

SiteStoragePropertiesModel = sites_api.model(
    "SiteStorageProperties",
    {
        "site_id": fields.String(readonly=True, description="The site site_id"),
        "serial_number": fields.String(readonly=True, description="The site battery serial_number"),
        "derid_battery": fields.String(readonly=True, description="The site battery derid_battery"),
        "derid_storage": fields.String(readonly=True, description="The site battery derid_storage"),
        "derid_inverter": fields.String(readonly=True, description="The site battery derid_inverter"),
        "batt_model": fields.String(readonly=True, description="The site battery batt_model"),
        "batt_manufacture": fields.String(readonly=True, description="The site battery batt_manufacture"),
        "batt_rated_power": fields.String(required=True, description="The site battery batt_rated_power"),
        "batt_rated_capacity": fields.String(required=True, description="The site battery batt_rated_capacity"),
        "min_operating_temperature": fields.String(
            required=True, description="The site battery min_operating_temperature"
        ),
        "max_operating_temperature": fields.String(
            required=True, description="The site battery max_operating_temperature"
        ),
        "batt_rte": fields.String(required=True, description="The site battery batt_rte"),
    },
)

SiteEnableModel = sites_api.schema_model(
    "SiteEnable",
    {
        "type": "object",
        "required": ["enabled"],
        "properties": {
            "enabled": {"description": "Required state of site", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)


@sites_api.route("/<string:site_id>/users/<string:user_id>")
@sites_api.response(404, "User not found")
@sites_api.param("user_id", "The user identifier")
@sites_api.param("site_id", "The site identifier")
class SiteUser(PearlxResource):
    """Manage user's access to the site"""

    @for_authenticated
    @for_admin
    @sites_api.doc("add_site_to_user")
    @sites_api.response(201, "User site access added")
    def post(self, user_id, site_id):
        """Add a user's site access"""
        userSitesService.add_site_to_user(user_id, site_id)
        return "", 201

    @for_authenticated
    @for_admin
    @sites_api.doc("remove_site_from_user")
    @sites_api.response(204, "User site access deleted")
    def delete(self, user_id, site_id):
        """Delete a user's site access"""
        userSitesService.remove_site_from_user(user_id, site_id)
        return "", 204

    @for_authenticated
    @for_admin
    @sites_api.expect(UpdateUserSiteRequest, validate=True)
    def patch(self, user_id, site_id):
        """Update a user's access on site"""
        userSitesService.update_user_site_access(user_id, site_id, sites_api.payload)
        return "", 200


@sites_api.route("/refresh")
class SiteRefresh(PearlxResource):
    """Load and populate sites from timestream db"""

    @for_authenticated
    @for_admin
    @sites_api.doc("refresh_sites")
    @sites_api.marshal_list_with(SiteModel)
    def post(self):
        """Start refreshing of sites"""
        return sitesService.refresh_sites()


@sites_api.route("")
class SitesList(PearlxResource):
    """Shows a list of all Sites"""

    @for_authenticated
    @sites_api.doc("list_sites")
    @sites_api.marshal_list_with(SiteModel)
    def get(self):
        """List all sites"""
        return sitesService.get_all_sites()


@sites_api.route("/<string:site_id>")
@sites_api.response(404, "Site not found")
@sites_api.param("site_id", "The site identifier")
class Site(PearlxResource):
    """Show a single site item"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @sites_api.doc("get_site")
    @sites_api.marshal_list_with(SiteModel)
    def get(self, site_id):
        """Load a site by its ID"""
        return sitesService.get_site_by_id(site_id)


@sites_api.route("/<string:site_id>/site-properties")
@sites_api.response(404, "Site not found")
@sites_api.param("site_id", "The site identifier")
class SiteProperties(PearlxResource):
    """Show a single site item properties"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @sites_api.doc("get_site_properties")
    @sites_api.marshal_list_with(SitePropertiesModel)
    def get(self, site_id):
        """Load a site properties by its ID"""
        return sitesService.get_site_properties_by_id(site_id)


@sites_api.route("/<string:site_id>/storage-properties")
@sites_api.response(404, "Site not found")
@sites_api.param("site_id", "The site identifier")
class SiteStorageProperties(PearlxResource):
    """Show a single site item storage properties"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @sites_api.doc("get_site_storage_properties")
    @sites_api.param("serials", "The list of serials. Coma separated.")
    @sites_api.marshal_list_with(SiteStoragePropertiesModel)
    def get(self, site_id):
        """Load a site storage properties by its ID"""
        serials = request.args.get("serials")
        if serials:
            serials = serials.split(",")
        return sitesService.get_site_storage_properties(site_id, serials)


@sites_api.route("/<string:site_id>/enable")
@sites_api.response(404, "Site not found")
@sites_api.param("site_id", "The site identifier")
class SiteEnable(PearlxResource):
    """Control of sites' state"""

    @for_authenticated
    @for_admin
    @sites_api.doc("enable_site")
    @sites_api.expect(SiteEnableModel, validate=True)
    @sites_api.marshal_with(SiteModel)
    def patch(self, site_id):
        """Activate or deactivate site"""
        return sitesService.update_site(site_id, sites_api.payload)


storageDataRequestParser = reqparse.RequestParser()
storageDataRequestParser.add_argument("start_time", location="args", type=str, required=True)
storageDataRequestParser.add_argument("end_time", location="args", type=str, required=True)

SiteStorageDataModel = sites_api.model(
    "SiteStorageData",
    {
        "site_id": fields.String(readonly=True, description="The site site_id"),
        "der_controller_id": fields.String(readonly=True, description="The site storage der_controller_id"),
        "derid_battery": fields.String(readonly=True, description="The site storage derid_battery"),
        "serial_number": fields.String(readonly=True, description="The site storage serial_number"),
        "timestamp": fields.String(readonly=True, description="The site storage measure timestamp"),
        "batt_system_status": fields.String(readonly=True, description="The site storage batt_system_status"),
        "batt_operating_mode": fields.String(readonly=True, description="The site storage batt_operating_mode"),
        "batt_active_power": fields.String(readonly=True, description="The site storage batt_active_power"),
        "batt_current_ac": fields.String(readonly=True, description="The site storage batt_current_ac"),
        "batt_frequency_ac": fields.String(readonly=True, description="The site storage batt_frequency_ac"),
        "batt_reactive_power": fields.String(readonly=True, description="The site storage batt_reactive_power"),
        "batt_soc": fields.String(readonly=True, description="The site storage batt_soc"),
        "batt_fullpackenergyavailable": fields.String(
            readonly=True, description="The site storage batt_fullpackenergyavailable"
        ),
        "batt_soh": fields.String(readonly=True, description="The site storage batt_soh"),
        "batt_temp_f": fields.String(readonly=True, description="The site storage batt_temp_f"),
        "batt_voltage_ac": fields.String(readonly=True, description="The site storage batt_voltage_ac"),
        "batt_voltage_dc": fields.String(readonly=True, description="The site storage batt_voltage_dc"),
        "battery_fault": fields.String(readonly=True, description="The site storage battery_fault"),
        "storage_status": fields.String(readonly=True, description="The site storage status"),
        "storage_id": fields.String(readonly=True, description="The site storage id"),
    },
)


@sites_api.route("/<string:site_id>/ders/<string:der_id>/storage-data")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteStorageData(PearlxResource):
    """Show a single site item storage data"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @for_der_owner(write_required=False)
    @sites_api.doc("get_site_storage_data")
    @sites_api.expect(storageDataRequestParser)
    @sites_api.marshal_list_with(SiteStorageDataModel)
    def get(self, site_id, der_id):
        """Load a site storage data by its ID"""
        query_params = storageDataRequestParser.parse_args()
        return sitesService.get_site_storage_data(
            site_id,
            query_params["start_time"],
            query_params["end_time"],
            der_id,
        )


inverterDataRequestParser = reqparse.RequestParser()
inverterDataRequestParser.add_argument("start_time", location="args", type=str, required=True)
inverterDataRequestParser.add_argument("end_time", location="args", type=str, required=True)

SiteInverterDataModel = sites_api.model(
    "SiteInverterData",
    {
        "site_id": fields.String(readonly=True, description="The site site_id"),
        "der_controller_id": fields.String(readonly=True, description="The site storage der_controller_id"),
        "derid_inverter": fields.String(readonly=True, description="The site inverter der_id"),
        "serial_number": fields.String(readonly=True, description="The site inverter serial_number"),
        "timestamp": fields.String(readonly=True, description="The site inverter measure timestamp"),
        "inverter_operating_mode": fields.String(
            readonly=True, description="The site inverter inverter_operating_mode"
        ),
        "inverter_fault": fields.String(readonly=True, description="The site inverter inverter_fault"),
        "amb_temp_f": fields.String(readonly=True, description="The site inverter amb_temp_f"),
        "from_grid_watts": fields.String(readonly=True, description="The site inverter from_grid_watts"),
        "load_watts": fields.String(readonly=True, description="The site inverter load_watts"),
        "inverter_feedin_meter": fields.String(readonly=True, description="The site inverter inverter_feedin_meter"),
        "inverter_production_meter": fields.String(
            readonly=True, description="The site inverter inverter_production_meter"
        ),
        "inverter_purchased_meter": fields.String(
            readonly=True, description="The site inverter inverter_purchased_meter"
        ),
        "inverter_consumption_meter": fields.String(
            readonly=True, description="The site inverter inverter_consumption_meter"
        ),
    },
)


@sites_api.route("/<string:site_id>/ders/<string:der_id>/inverter-data")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteInverterData(PearlxResource):
    """Show a single site item inverter data"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @for_der_owner(write_required=False)
    @sites_api.doc("get_site_inverter_data")
    @sites_api.expect(inverterDataRequestParser)
    @sites_api.marshal_list_with(SiteInverterDataModel)
    def get(self, site_id, der_id):
        """Load a site inverter data by its ID"""
        query_params = inverterDataRequestParser.parse_args()
        return sitesService.get_site_inverter_data(
            site_id, query_params["start_time"], query_params["end_time"], der_id
        )


DerModel = sites_api.model(
    "Der",
    {
        "id": fields.String(readonly=True, description="The der unique identifier"),
        "enabled": fields.Boolean(required=True, description="The der state"),
        "der_type": fields.String(required=True, description="The der type"),
        "site_id": fields.String(required=True, description="The site identifier"),
    },
)


@sites_api.route("/<string:site_id>/ders")
@sites_api.response(404, "Site not found")
@sites_api.param("site_id", "The site identifier")
class SiteDersList(PearlxResource):
    """Shows a list of all Ders"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @sites_api.doc("list_ders")
    @sites_api.marshal_list_with(DerModel)
    def get(self, site_id):
        return sitesService.get_ders_by_site_id(site_id)


@sites_api.route("/<string:site_id>/ders/<string:der_id>")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteDer(PearlxResource):
    """Show a single der item"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @for_der_owner(write_required=False)
    @sites_api.doc("get_der")
    @sites_api.marshal_list_with(DerModel)
    def get(self, site_id, der_id):
        return sitesService.get_der(site_id, der_id)


DerEnableModel = sites_api.schema_model(
    "DerEnable",
    {
        "type": "object",
        "required": ["enabled"],
        "properties": {
            "enabled": {"description": "Required state of der", "type": "boolean"},
        },
        "additionalProperties": False,
    },
)


@sites_api.route("/<string:site_id>/ders/<string:der_id>/enable")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteDerEnable(PearlxResource):
    """Control of ders' state"""

    @for_authenticated
    @for_admin
    @sites_api.doc("enable_der")
    @sites_api.expect(DerEnableModel, validate=True)
    @sites_api.marshal_with(DerModel)
    def patch(self, site_id, der_id):
        """Activate or deactivate der"""
        return sitesService.update_der(site_id, der_id, sites_api.payload)


ScheduleDerSettingsUpdateRequest = sites_api.schema_model(
    "ScheduleDerSettingsUpdate",
    {
        "type": "object",
        "required": [
            "startTime",
            "endTime",
            "priority",
            "eventOrigin",
            "eventOrigin",
            "parameters",
        ],
        "properties": {
            "startTime": {
                "description": "Start Time of when the settings should apply",
                "type": "string",
                "format": "date-time",
            },
            "endTime": {
                "description": "End Time of when the settings should apply",
                "type": "string",
                "format": "date-time",
            },
            "priority": {
                "description": "Event Priority that must be greater than 1 (incl.) and less than 100000 (incl.)",
                "type": "string",
            },
            "eventOrigin": {
                "description": '"GRID_SERVICES_API" needs to be passed as part of the request body as shown above',
                "type": "string",
                "enum": ["GRID_SERVICES_API"],
            },
            "parameters": {
                "description": "The set of settings/commands that are being modified",
                "type": "object",
                "properties": {
                    "allowGridExport": {
                        "description": "Allow/Forbid export energy to grid (Boolean - True/False)",
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["bool"]},
                            "enabled": {"type": "boolean"},
                            "value": {"type": "boolean"},
                        },
                        "required": ["type", "enabled", "value"],
                        "additionalProperties": False,
                    },
                    "chargeStorageUsingPvOnly": {
                        "description": "Eliminate Charging Storage from the grid",
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["bool"]},
                            "enabled": {"type": "boolean"},
                            "value": {"type": "boolean"},
                        },
                        "required": ["type", "enabled", "value"],
                        "additionalProperties": False,
                    },
                    "activePowerLimit": {
                        "description": "Max Active Power in %",
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["integer"]},
                            "enabled": {"type": "boolean"},
                            "value": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                            },
                        },
                        "required": ["type", "enabled", "value"],
                        "additionalProperties": False,
                    },
                    "reservedStorage": {
                        "description": "Sets percent of reserved storage out of total capacity",
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["decimal"]},
                            "enabled": {"type": "boolean"},
                            "value": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                            },
                        },
                        "required": ["type", "enabled", "value"],
                        "additionalProperties": False,
                    },
                    "storageControlMode": {
                        "description": "Sets the system into one of the following control models",
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["string"]},
                            "enabled": {"type": "boolean"},
                            "value": {
                                "type": "string",
                                "enum": [
                                    "maximizeSelfConsumption",
                                    "backupOnly",
                                    "userDefinedStorageProfile",
                                    "disable",
                                ],
                            },
                        },
                        "required": ["type", "enabled", "value"],
                        "additionalProperties": False,
                    },
                },
                "anyOf": [
                    {"required": ["allowGridExport"]},
                    {"required": ["chargeStorageUsingPvOnly"]},
                    {"required": ["activePowerLimit"]},
                    {"required": ["reservedStorage"]},
                    {"required": ["storageControlMode"]},
                ],
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    },
)


@sites_api.route("/<string:site_id>/ders/<string:der_id>/schedule-der-settings-update")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteScheduleDerSettingsUpdate(PearlxResource):
    """Modifying DER Settings for a Time Window"""

    @for_authenticated
    @for_site_owner(read_required=False)
    @for_der_owner(read_required=False)
    @sites_api.doc("site_schedule_der_settings_update")
    @sites_api.expect(ScheduleDerSettingsUpdateRequest, validate=True)
    def post(self, site_id, der_id):
        return sitesService.schedule_der_command("schedule-der-settings-update", site_id, der_id, sites_api.payload)


ScheduleDerEventRequest = sites_api.schema_model(
    "ScheduleDerEvent",
    {
        "type": "object",
        "required": [
            "commandUri",
            "startTime",
            "endTime",
            "priority",
            "eventOrigin",
            "parameters",
        ],
        "properties": {
            "commandUri": {
                "description": "Uri of the command that is being modified",
                "type": "string",
                "enum": ["chargeStorage", "dischargeStorage"],
            },
            "startTime": {
                "description": "Start Time of when the settings should apply",
                "type": "string",
                "format": "date-time",
            },
            "endTime": {
                "description": "End Time of when the settings should apply",
                "type": "string",
                "format": "date-time",
            },
            "priority": {
                "description": "Event Priority that must be greater than 1 (incl.) and less than 100000 (incl.)",
                "type": "string",
            },
            "eventOrigin": {
                "description": '"GRID_SERVICES_API" needs to be passed as part of the request body as shown above',
                "type": "string",
                "enum": ["GRID_SERVICES_API"],
            },
            "parameters": {
                "description": "The set of settings/commands that are being modified",
                "type": "object",
                "properties": {
                    "chargePowerPercent": {
                        "description": "Charge storage at constant power",
                        "type": "string",
                    },
                    "dischargePowerPercent": {
                        "description": "Discharge storage at constant power",
                        "type": "string",
                    },
                },
                "oneOf": [
                    {"required": ["chargePowerPercent"]},
                    {"required": ["dischargePowerPercent"]},
                ],
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    },
)


@sites_api.route("/<string:site_id>/ders/<string:der_id>/schedule-der-event")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("der_id", "The der identifier")
class SiteScheduleDerEvent(PearlxResource):
    """Schedule an event"""

    @for_authenticated
    @for_site_owner(read_required=False)
    @for_der_owner(read_required=False)
    @sites_api.doc("site_schedule_der_event")
    @sites_api.expect(ScheduleDerEventRequest, validate=True)
    def post(self, site_id, der_id):
        return sitesService.schedule_der_command("schedule-der-event", site_id, der_id, sites_api.payload)


CancelDerEventRequest = sites_api.schema_model(
    "CancelDerEvent",
    {
        "type": "object",
        "required": ["derEventId"],
        "properties": {
            "derEventId": {"description": "Event ID", "type": "string"},
        },
        "additionalProperties": False,
    },
)


@sites_api.route("/<string:site_id>/cancel-der-event")
@sites_api.param("site_id", "The site identifier")
class SiteCancelDerEvent(PearlxResource):
    """Canceling Events - For cancelling an ongoing or future event"""

    @for_authenticated
    @for_site_owner(read_required=False)
    @sites_api.doc("site_cancel_der_event")
    @sites_api.expect(CancelDerEventRequest, validate=True)
    def post(self, site_id):
        return sitesService.cancel_der_command(site_id, sites_api.payload)


@sites_api.route("/<string:site_id>/der-events/<string:event_id>")
@sites_api.param("site_id", "The site identifier")
@sites_api.param("event_id", "The event identifier")
class SiteDerEvent(PearlxResource):
    """Tracking Events/Settings"""

    @for_authenticated
    @for_site_owner(write_required=False)
    @sites_api.doc("site_der_event")
    def get(self, site_id, event_id):
        return sitesService.get_event(site_id, event_id)
