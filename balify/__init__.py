import logging

from datetime import date, datetime  # Entity field type

import humps  # noqa
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from .resource import RouterGenerator
from .utils import pluralize

from .decorators import action

from sqlmodel import Field, SQLModel, create_engine


class _OMeta(type):
    """Metaclass for `O` object

    Bind FastAPI instance to `O`

    TODO: Compare `Metaclass` and `__init_subclass__`, then choose one in for `_OMeta`
    """

    _app = FastAPI()

    def __new__(cls, *args, **kwargs):
        meta = super().__new__(cls, *args, **kwargs)

        meta._app = FastAPI()
        meta._app = add_pagination(cls._app)

        return meta

    @property
    def _endpoint(self):
        if self._o_endpoint:  # noqa
            endpoint = self._o_endpoint  # noqa
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
        print("--> Generate routers in App(%s)" % id(self._app))
        return RouterGenerator(self)()


GREETERS = [{"name": "Josh"}]


class O(metaclass=_OMeta):
    """O is a proxy for model, schema, resource

    model is SQLAlchemy/SQLModel model
    schema is Pydantic model
    resource is Restful resource
    """

    schema = None

    @classmethod
    def serve(cls, *entities) -> None:

        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/")
        def hello():
            return {"Hello": "World", "Powered by": "balify router"}

        cls._app.include_router(router, prefix="/router1")

        for entity in entities:
            print("--> Serve entity `%s` in App(%s)" % (str(entity), id(cls._app)))
            cls._app.include_router(entity.as_router(), prefix="/users")

    @action()
    def create(self, schema_in):
        return {"id": schema_in.id, "content": schema_in.content}

    # def list(self):
    #     return {
    #         "items": [],
    #         "total": 0,
    #         "limit": 10,
    #         "offset": 1,
    #     }

    # @action()
    # def list(self, schema_in):
    #     return GREETERS[: schema_in.limit]


# I found that `O, o` in `from balify import O, o` look like an cute emontion.
# May be I can split the metaclass to uppercase `O` and lowercase `o`.
# Uppercase `O` for define entity, could be translate to model, schema and resource.
# Lowercase `o` for FastAPI instance, provide `serve` functionality.
#
# On the other hand, using both the uppercase O and the lowercase o helps developers
# form good coding style habits.
o = O
