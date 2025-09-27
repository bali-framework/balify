import inspect
from collections import OrderedDict
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi_pagination import LimitOffsetPage
from pydantic import BaseModel
from starlette import status

from .decorators import action
from .utils import transform_to_sqlmodel


from .generic_routes import pick_route, list_, create_, get_, update_, delete_
from .schemas import ResultResponse


GENERIC_ACTIONS = [
    "list",
    "get",
    "create",
    "update",
    "delete",
]


class Generator:
    @property
    def resource_name(self):
        return self.cls.__name__.replace("Resource", "")  # type: ignore

    @property
    def primary_key(self):
        return "id"


class RouterGenerator(Generator):
    """
    Generator FastAPI router from Resource class
    """

    def __init__(self, cls):
        self.cls = cls  # `cls` is Entity

        self.router = APIRouter()
        # self._ordered_filters = self._get_ordered_filters()
        self._ordered_filters = {}

        # Provide class var `schema` to Entity
        self.cls.schema = transform_to_sqlmodel(cls)

        # # Bind Generic actions to Entity
        # self.cls.create = create

    def __call__(self):
        actions = GENERIC_ACTIONS
        actions = ["list", "get", "create", "update"]
        for action in actions:
            print("--> Add router %s" % str(action))
            self.add_route(action)
        return self.router

    def check_permissions(self, resource):
        pass
        # for permission_class in self.cls.permission_classes:
        #     permission = permission_class(resource)
        #     if not permission.check():
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail="Permission Denied",
        #         )

    def _get_ordered_filters(self):
        filters = OrderedDict()
        for item in self.cls.filters:
            k = item.keys().__iter__().__next__()
            v = item.values().__iter__().__next__()
            filters[k] = v
        return filters

    def get_endpoint(
        self, action, detail=False, methods=list, schema_in_annotation=None
    ):
        """Convert Resource instance method to FastAPI endpoint"""
        resource = self.cls()
        action_func = getattr(resource, action)

        def endpoint(request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return action_func()

        async def async_endpoint(request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return await action_func()

        def endpoint_detail(pk: int, request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return action_func(pk)

        async def async_endpoint_detail(pk: int, request: Request = None):
            resource._request = request
            self.check_permissions(resource)
            return await action_func(pk)

        def endpoint_schema(
            schema_in: BaseModel = None, request: Request = None, **kwargs
        ):
            resource._request = request
            self.check_permissions(resource)
            if "get" in methods and schema_in_annotation:
                schema_in = schema_in_annotation(**kwargs)
            return action_func(schema_in)

        async def async_endpoint_schema(
            schema_in: BaseModel = None, request: Request = None, **kwargs
        ):
            resource._request = request
            self.check_permissions(resource)
            if "get" in methods and schema_in_annotation:
                schema_in = schema_in_annotation(**kwargs)
            return await action_func(schema_in)

        sig = inspect.signature(getattr(self.cls, action))

        route = pick_route(action_func, async_endpoint, endpoint)
        if detail:
            route = pick_route(action_func, async_endpoint_detail, endpoint_detail)
        elif "schema_in" in sig.parameters:
            route = pick_route(action_func, async_endpoint_schema, endpoint_schema)
            params = list(sig.parameters.values())[1:]
            if "get" in methods and schema_in_annotation:
                # Destructor the `schema_in` to Query
                for field, annotation in schema_in_annotation.__fields__.items():
                    params = params[1:]
                    params.append(
                        inspect.Parameter(
                            name=field,
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=annotation.default,
                            annotation=annotation.type_,
                        )
                    )
                route.__signature__ = sig.replace(parameters=params)
            else:
                params = list(sig.parameters.values())[1:]

            params.append(
                inspect.Parameter(
                    name="request",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=Request,
                )
            )
            route.__signature__ = sig.replace(parameters=params)

        return route

    def add_route(self, action):
        if action == "list":
            self.router.add_api_route(
                "",
                list_(self),
                methods=["GET"],
                # response_model=LimitOffsetPage[self.cls],
                response_model=list[self.cls.schema],
                summary=f"List {self.resource_name}",
            )
        elif action == "create":
            self.router.add_api_route(
                "",
                create_(self),
                methods=["POST"],
                response_model=self.cls.schema and Optional[self.cls.schema],
                summary=f"Create {self.resource_name}",
                status_code=status.HTTP_201_CREATED,
            )
        elif action == "get":
            self.router.add_api_route(
                "/{%s}" % self.primary_key,
                get_(self),
                methods=["GET"],
                response_model=self.cls.schema,
                summary=f"Get {self.resource_name}",
            )
        elif action == "update":
            self.router.add_api_route(
                "/{%s}" % self.primary_key,
                update_(self),
                methods=["PATCH"],
                response_model=self.cls.schema,
                summary=f"Update {self.resource_name}",
            )
        elif action == "delete":
            self.router.add_api_route(
                "/{%s}" % self.primary_key,
                delete_(self),
                methods=["DELETE"],
                response_model=ResultResponse,
                summary=f"Delete {self.resource_name}",
            )
