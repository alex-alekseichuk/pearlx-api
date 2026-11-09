from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Boolean, DateTime, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import object_mapper, ColumnProperty, declarative_base


class ModelBase(object):
    def to_dict(self, exclude_keys=()):
        """TODO: Remove after services are converted to using
        Marshmallow/Schema
        """
        mapper = object_mapper(self)
        return {
            col.key: getattr(self, col.key)
            for col in mapper.iterate_properties
            if isinstance(col, ColumnProperty) and col.key not in exclude_keys
        }

    created_at = Column(DateTime, server_default=text("now()"), nullable=False)
    updated_at = Column(DateTime, server_default=text("now()"), nullable=False)

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if hasattr(self, "updated_at"):
            setattr(self, "updated_at", text("now()"))


Base = declarative_base(cls=ModelBase)
db = SQLAlchemy(model_class=Base)


def init_db(app):
    db.init_app(app)

    @app.teardown_request
    def rollback_and_warn(exception):
        if db.session is not None and db.session.dirty:
            current_app.logger.warning(
                "Request to {} completed with dirty session: {!r}".format(app.request.url, db.session.dirty)
            )
            db.session.rollback()

    Migrate(app, db)


def create_all():
    db.create_all()
    db.session.commit()


def reset_tables(session):
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
        session.commit()


def commit():
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as ex:
        current_app.logger.error(f"{ex.__class__.__name__}: {ex}")
        db.session.rollback()
        return False


class EnabledMixin(ModelBase):
    enabled = Column(Boolean, default=True, nullable=False)

    def enable(self):
        if self.enabled:
            return
        self.update({"enabled": True})

    def disable(self):
        if not self.enabled:
            return
        self.update({"enabled": False})


class CreatedAtMixin:
    created_at = Column(DateTime, server_default=text("now()"), nullable=False)


# load all models to allow alembic migrations for them
from .models import *
