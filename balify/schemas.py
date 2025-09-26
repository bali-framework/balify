"""Generic request/response schemas"""

from typing import List, Dict, Any

from fastapi.dependencies.utils import get_typed_signature
from pydantic import BaseModel, Field

# TODO: Rename to `XXXIn` or `XXXOut` style
__all__ = [
    "GetRequest",
    "ListRequest",
    "CreateRequest",
    "UpdateRequest",
    "DeleteRequest",
    "ItemResponse",
    "ListResponse",
    "ResultResponse",
]


class GetRequest(BaseModel):
    id: int = Field(default_factory=int)


class ListRequest(BaseModel):
    filters: Dict[str, Any] = Field(default_factory=dict)
    offset: int = Field(default_factory=int)
    limit: int = Field(default_factory=int)
    ordering: List[str] = Field(default_factory=list)


class CreateRequest(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)


class UpdateRequest(BaseModel):
    id: int = Field(default_factory=int)
    data: Dict[str, Any] = Field(default_factory=dict)


class DeleteRequest(BaseModel):
    id: int = Field(default_factory=int)


class ItemResponse(BaseModel):
    data: List[Dict[str, Any]] = Field(default_factory=list)


class ListResponse(BaseModel):
    data: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = Field(default_factory=int)


class ResultResponse(BaseModel):
    result: bool = Field(default_factory=bool)


def get_schema_in(func, default_by_action=False):
    """
    Inspects action function to get the schema

    if `default_by_action` is provided, It is generally to obtain a schema
    that can be used in a `generic action` method.
    (like: list/create/get/update/delete)
    """

    # Generic schemas bind to actions
    generic_schemas = {
        "list": ListRequest,
        "create": CreateRequest,
        "get": GetRequest,
        "update": UpdateRequest,
        "delete": DeleteRequest,
    }

    typed_signature = get_typed_signature(func)
    signature_params = typed_signature.parameters

    # 1st argument is self
    # 2st argument is schema_in
    index = 0
    for param_name, param in signature_params.items():
        index += 1
        if index == 2 or param_name == "schema_in":
            schema_in = param.annotation
            if not schema_in:

                if default_by_action:
                    return generic_schemas.get(func.__name__)

                raise ValueError(
                    "Custom actions must provide `schema_in` argument with annotation"
                )

            return schema_in
    else:
        raise ValueError("Custom actions arguments error")
