from functools import wraps

from flask import g, request
from werkzeug.exceptions import NotFound, Forbidden, Unauthorized, BadRequest

from core import log
from model import Object, File, Config, TextBlob

logger = log.getLogger()


def requires_capabilities(*required_caps):
    """
    Decorator for endpoints which require specific permission.
    Available capabilities are declared in capabilities.Capabilities
    """

    def decorator(f):
        @wraps(f)
        def endpoint(*args, **kwargs):
            for required_cap in required_caps:
                if not g.auth_user.has_rights(required_cap):
                    raise Forbidden("You are not permitted to perform this action")
            return f(*args, **kwargs)

        return endpoint

    return decorator


def requires_authorization(f):
    """
    Decorator for endpoints which require authorization.
    """
    @wraps(f)
    def endpoint(*args, **kwargs):
        if not g.auth_user:
            raise Unauthorized('Not authenticated.')
        return f(*args, **kwargs)
    return endpoint


def deprecated(f):
    """
    Decorator for deprecated methods
    """
    @wraps(f)
    def endpoint(*args, **kwargs):
        logger.warning("Used deprecated endpoint: %s", request.path)
        return f(*args, **kwargs)
    return endpoint


def access_object(object_type, identifier):
    """
    Get object by provided string type and identifier
    :param object_type: String type [file, config, blob, object]
    :param identifier: Object identifier
    :return: Returns specified object or None when object doesn't exist, has different type or user doesn't have
             access to this object.
    """
    object_types = {
        "object": Object,
        "file": File,
        "config": Config,
        "blob": TextBlob
    }
    if object_type not in object_types:
        # Should never happen, routes should be restricted on route definition level
        raise ValueError(f"Incorrect object type '{object_type}'")
    return object_types[object_type].access(identifier)
