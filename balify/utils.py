import re
from typing import Any

from pydantic import BaseModel


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
