from flask_restx import Resource
from flask_restx.namespace import Namespace
from flask_restx.model import SchemaModel
from jsonschema import Draft4Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from ..services import IncorrectInputException


class PearlxSchemaModel(SchemaModel):
    """Custom schema model based on default one of flask_restx. Overrides validate method."""

    def validate(self, data, resolver=None, format_checker=None):
        validator = Draft4Validator(self.__schema__, resolver=resolver, format_checker=FormatChecker())
        try:
            validator.validate(data)
        except ValidationError:
            errors = dict(self.format_error(e) for e in validator.iter_errors(data))
            result = ", ".join([f"{k}: {v}" if k else f"common: {v}" for k, v in errors.items()])
            raise IncorrectInputException(result)


class PearlxNamespace(Namespace):
    """Custom namespace based on default one of flask_restx. Overrides schema_model method."""

    def schema_model(self, name=None, schema=None):
        model = PearlxSchemaModel(name, schema)
        return self.add_model(name, model)


class PearlxResource(Resource):
    """Custom resource based on default one of flask_restx. Wraps auth checking mechanism."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_decorators.append(self.check_auth)

    def check_auth(self, f):
        if hasattr(f, "_auth_checks"):
            for auth_check in reversed(f._auth_checks):
                auth_check()
        return f
