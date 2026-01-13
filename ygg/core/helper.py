"""A collection of helper functions for Ygg."""

import uuid
from typing import Any


def enforce_authoritative_definition(v: Any) -> Any:
    """Handles the authoritative catalog to retrieve a list of AuthoritativeDefinitions."""
    from ygg.core.base_models import AuthoritativeDefinition

    if not v:
        return []

    if isinstance(v, AuthoritativeDefinition):
        return [v]

    elif isinstance(v, str):
        cleaned = v.strip()
        return [{"url": cleaned}] if cleaned else []

    elif isinstance(v, (AuthoritativeDefinition, dict)):
        return [v]

    elif isinstance(v, list):
        normalized_list = []
        for item in v:
            if isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    normalized_list.append({"url": cleaned})
            else:
                normalized_list.append(item)
        return normalized_list

    return v


def generate_uuid4():
    return uuid.uuid4()
