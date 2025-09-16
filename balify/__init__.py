from __future__ import annotations

import humps  # noqa
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .resource import RouterGenerator
from .utils import pluralize


class _VAMeta(type):
    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(*args, **kwargs)
        self._application = FastAPI()
        self._application = add_pagination(self._application)

    @property
    def _endpoint(self):
        if self._va_endpoint:  # noqa
            endpoint = self._va_endpoint  # noqa
        else:
            # Generate endpoint from resource name
            name = self.__name__.replace("Resource", "")
            words = humps.decamelize(name).split("_")
            words[-1] = pluralize(words[-1])
            endpoint = "-".join(words)

        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return endpoint

    def as_router(self):
        return RouterGenerator(self)()

    def list(self):
        return []


class _VA(metaclass=_VAMeta):
    """VA is a proxy for model, schema, resource

    model is SQLAlchemy model
    schema is Pydantic model
    resource is Restful resource
    """

    @classmethod
    def serve(cls, *entity_classes) -> None:
        for entity_class in entity_classes:
            cls._application.include_router(entity_class.as_router(), prefix="/users")

    def list(self):
        return {
            "items": [],
            "total": 0,
            "limit": 10,
            "offset": 1,
        }


va = _VA
