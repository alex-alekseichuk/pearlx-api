from functools import wraps
from flask import g, current_app

from ..db.dao.user_sites import UserSitesDao
from ..db.dao.user_ders import UserDersDao
from ..db.dao.users import UsersDao

userSitesDao = UserSitesDao()
userDersDao = UserDersDao()
usersDao = UsersDao()


class ServiceException(Exception):
    """Raised when some pure internal error occurs in a service."""


class AuthenticationException(ServiceException):
    """Raised when the login is incorrect or token is expired/incorrect."""


class AuthorizationException(ServiceException):
    """Raised when the call is forbidden based on current context/user."""


class NotFoundException(ServiceException):
    """Raised when some object/entity is absent or disabled."""


class IncorrectInputException(ServiceException):
    """Raised when some object/entity is absent or disabled."""


def is_admin():
    if g.context is None or "is_admin" not in g.context or not g.context["is_admin"]:
        return False
    return True


def on_error(message):
    """Catch any non-service error of backend layer, log and raise service error."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            try:
                result = f(*args, **kwds)
            except Exception as ex:
                if isinstance(ex, ServiceException):
                    raise ex
                current_app.logger.error(ex)
                current_app.logger.error(f"{message} {args} {kwds}")
                raise ServiceException(message)
            return result

        return wrapper

    return decorator


def for_admin(f):
    """Check the current context has admin role."""

    def check():
        if not is_admin():
            current_app.logger.error(f"Forbidden for non-admin: {f.__name__}")
            raise AuthorizationException("Forbidden")

    if not hasattr(f, "_auth_checks"):
        f._auth_checks = []

    f._auth_checks.append(check)

    return f


def for_authenticated(f):
    """Check the current context is authenticated."""

    def check():
        if not g.context:
            current_app.logger.error(f"Unauthenticated for anonymous: {f.__name__}")
            raise AuthenticationException("Unauthenticated")

    if not hasattr(f, "_auth_checks"):
        f._auth_checks = []

    f._auth_checks.append(check)

    return f


def for_site_owner(read_required=True, write_required=True):
    """Check the current context is site owner."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if is_admin():
                return f(*args, **kwds)

            if "site_id" in kwds:
                user_site = userSitesDao.get_user_site(g.context["user_id"], kwds["site_id"])

                if user_site:
                    if not user_site.site.enabled:
                        raise AuthorizationException("Forbidden: this site is disabled")

                    permit = True
                    if read_required and not user_site.read_enabled:
                        permit = False
                    if write_required and not user_site.write_enabled:
                        permit = False
                    if permit:
                        return f(*args, **kwds)

            raise AuthorizationException("Forbidden: you have not right to this site")

        return wrapper

    return decorator


def for_der_owner(read_required=True, write_required=True):
    """Check the current context is der owner."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if is_admin():
                return f(*args, **kwds)

            if "der_id" in kwds:
                user_der = userDersDao.get_user_der(g.context["user_id"], kwds["der_id"])

                if user_der:
                    if not user_der.der.enabled:
                        raise AuthorizationException("Forbidden: this der is disabled")

                    permit = True
                    if read_required and not user_der.read_enabled:
                        permit = False
                    if write_required and not user_der.write_enabled:
                        permit = False
                    if permit:
                        return f(*args, **kwds)

            raise AuthorizationException("Forbidden: you have not right to this der")

        return wrapper

    return decorator


def for_organization_member(f):
    """Check the current context is organization member."""

    @wraps(f)
    def wrapper(*args, **kwds):
        if is_admin():
            return f(*args, **kwds)

        if "organization_id" in kwds:
            user = usersDao.get_user_by_id(g.context["user_id"])
            if user and str(user.organization_id) == kwds["organization_id"]:
                return f(*args, **kwds)

        raise AuthorizationException("Forbidden: you have not right to this organization")

    return wrapper
