from datetime import datetime
from flask import request
from flask_restx import Resource, fields, Namespace

ping_api = Namespace("ping", description="PING operations")

PingResponse = ping_api.model(
    "PingResponse",
    {
        "datetime": fields.DateTime(readonly=True, description="The date-time of the response"),
        "method": fields.String(required=True, description="The HTTP method"),
        "url": fields.String(required=True, description="The HTTP url"),
    },
)


@ping_api.route("")
class Ping(Resource):
    """Simple reply with current datetime"""

    @ping_api.doc("get_ping")
    @ping_api.marshal_with(PingResponse)
    def get(self):
        response = {
            "datetime": datetime.utcnow().isoformat()[:-3] + "Z",
            "method": request.method,
            "url": request.url,
        }
        return response
