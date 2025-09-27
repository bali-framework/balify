import re
from typing import Any

from pydantic import BaseModel
from sqlmodel.main import SQLModelMetaclass


def pluralize(noun):
    """pluralize a given word

    ref:
    https://www.codespeedy.com/program-that-pluralize-a-given-word-in-python/

    :param noun:
    :return:
    """
    if re.search("[sxz]$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[^aeioudgkprt]h$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[aeiou]y$", noun):
        return re.sub("y$", "ies", noun)
    else:
        return noun + "s"


# TODO: re-check parse_dict usage
def parse_dict(item: Any, schema: BaseModel = None):
    """Parse model instance, schema, dict to dict"""
    if isinstance(item, dict):
        return item

    # Transform model instance to schema
    if hasattr(item, "_sa_instance_state"):
        if not schema:
            raise ValueError("Model instance can't parse to dict without schema")
        return schema.from_orm(item).dict()

    return item.dict()


from typing import get_type_hints, Optional, Dict, Any, Type, ClassVar
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Integer, String, DateTime

TYPE_MAP = {int: Integer, str: String, datetime: DateTime}


def transform_to_sqlmodel(
    cls: Type,
    table_name: Optional[str] = None,
) -> Type[SQLModel]:
    annotations = get_type_hints(cls, include_extras=False)

    attrs: Dict[str, Any] = {"id": Field(primary_key=True)}
    ann: Dict[str, Any] = {"id": int}

    if table_name is None:
        table_name = cls.__name__.lower()
    attrs["__tablename__"] = table_name

    for name, typ in annotations.items():
        # keep the annotation so Pydantic sees the field
        ann[name] = typ
        attrs[name] = None

    attrs["__annotations__"] = ann
    model_name = f"{cls.__name__}SQLModel"

    # An equivalent approach created directly using a metaclass
    sqlmodel_cls = type(model_name, (SQLModel,), attrs, table=True)

    return sqlmodel_cls


# # example base class O (placeholder)
# class O:
#     pass


# class User(O):
#     name: str
#     age: int
#     email: str
#     create_at: datetime
#     updated_at: datetime


# UserModel = transform_to_sqlmodel(User)
# print(UserModel, UserModel.__tablename__)
# print(UserModel.__fields__.keys())
