import functools
import inspect
import json
import logging
import traceback

from fastapi.dependencies.utils import get_typed_signature
from fastapi_pagination import LimitOffsetParams, set_page, Page
from pydantic import BaseModel

from .exceptions import ReturnTypeError
from .paginate import paginate
from .schemas import get_schema_in

logger = logging.getLogger("bali")


def compatible_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)

    @functools.wraps(func)
    async def wrapper_async(self, *args, **kwargs):
        return await func(self, *args, **kwargs)

    return wrapper_async if inspect.iscoroutinefunction(func) else wrapper


def action(methods=None, detail=None, **kwargs):
    """
    Mark a Resource method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.

    :param methods:
    :param detail:
    :param kwargs:
    """
    methods = ["get"] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    class Action:
        def __init__(self, func):
            self.func = func

        def __set_name__(self, owner, name):
            # replace ourself with the original method
            setattr(owner, name, compatible_method(self.func))

            # Append actions to Resource._actions
            try:
                schema_in_annotation = get_schema_in(self.func)
            except ValueError:
                schema_in_annotation = None

            _actions = getattr(owner, "_actions", dict())
            _actions[self.func.__name__] = {
                "detail": detail,
                "methods": methods,
                "schema_in_annotation": schema_in_annotation,
            }
            setattr(owner, "_actions", _actions)

    return Action
