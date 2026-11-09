from functools import wraps

from .. import commit


class DaoException(Exception):
    """Raised when SQL commit failed."""


def commit_or_abort():
    """Commit TX by hand in DAO methods."""
    if not commit():
        raise DaoException()


def transaction(f):
    """Decorator to run some DAO method in transaction and commit automatically."""

    @wraps(f)
    def wrapper(*args, **kwds):
        result = f(*args, **kwds)
        commit_or_abort()
        return result

    return wrapper
