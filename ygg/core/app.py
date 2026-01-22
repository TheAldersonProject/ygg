"""Ygg core app implementation."""

import json
from collections import defaultdict
from typing import Any, Literal

from glom import glom
from pydantic import BaseModel, Field

import ygg.core.contract_config as conf


class _YggModelProperty(BaseModel):
    """Ygg model properties."""

    name: str
    type: str
    alias: str
    required: bool | None = Field(default=True)
    primary_key: bool | None = Field(default=False)
    primary_key_position: int | None = Field(default=None)
    unique: bool | None = Field(default=False)
    pattern: str | None = Field(default=None)
    odcs_schema: str | None = Field(default=None)
    enum: list[Any] | None = Field(default=None)
    properties: Any | None = Field(default=None)
    items: Any | None = Field(default=None)
    default: Any | None = Field(default=None)
    description: str | None = Field(default=None)
    examples: list[Any] | None = Field(default=None)


class _YggModelConfig(BaseModel):
    """Ygg model properties."""

    document_path: str | None = Field(default=None)
    type: str
    required: bool | None = Field(default=True)
    entity_name: str
    entity_type: Literal["table", "view"]
    entity_schema: str
    description: str
    odcs_reference: str


class _YggModel(BaseModel):
    """Ygg model."""

    name: str
    config: _YggModelConfig
    properties: list[_YggModelProperty]


class Ygg:
    """Ygg core application class."""

    def __init__(self, odcs_version: str = "v3.1.0"):
        """Initialize the Ygg core application."""

        self._odcs_version: str = odcs_version
        self._odcs_schema: dict = self.load_odcs_schema()
        self._structured_model_configurations: dict[str, dict[str, Any]] = self._structure_model_configuration()

    def load_odcs_schema(self):
        odcs_schema_path: str = conf.ODCS_SCHEMA.format(ODCS_VERSION=self._odcs_version)
        schema_content: dict = {}

        with open(odcs_schema_path, "r") as f:
            schema_content = json.load(f)

        return schema_content

    def load_model_map(self):
        """Loads the Ygg Data Model."""

        if not self._structured_model_configurations:
            raise ValueError("Ygg Structured Model Configurations Cannot be Empty.")

        model_map: dict[str, _YggModel] = {}
        data_type_list: list[str] = []

        for key, value in self._structured_model_configurations.items():
            model_class: str = value.get("name", "")
            config: dict = value.get("config", {})
            properties: dict = value.get("properties", {})

            # model_class: str = key.strip().capitalize()
            _properties: list[_YggModelProperty] = []

            for k, v in properties.items():
                data_type_list.append(v.get("type", None))
                map_ = dict(
                    name=k,
                    type=v.get("type", None),
                    alias=v.get("alias", None),
                    odcs_schema=v.get("odcs_schema", None),
                    required=v.get("required", True),
                    enum=v.get("enum", None),
                    items=v.get("items", None),
                    properties=v.get("properties", None),
                    pattern=v.get("pattern", None),
                    default=v.get("default", None),
                    description=v.get("description", None),
                    examples=v.get("examples", None) or v.get("enum", None),
                    primary_key=v.get("primary_key", False),
                    primary_key_position=v.get("primary_key_position", None),
                    unique=v.get("unique", False),
                )
                ygg_property: _YggModelProperty = _YggModelProperty(**map_)
                _properties.append(ygg_property)

            ygg_model: _YggModel = _YggModel(**{"name": model_class, "properties": _properties, "config": config})
            model_map[model_class] = ygg_model

        l = list(set(data_type_list))
        print(l)
        return model_map

    def _structure_model_configuration(self) -> dict[str, dict[str, Any]]:
        """Loads the Ygg Data Model properties."""

        model_schema: dict[str, dict[str, Any]] = defaultdict(dict)
        for key, item in conf.CONTRACT_BOK.items():
            odcs_schema: dict[str, Any] = defaultdict(dict)

            name: str = item.get("name", "")
            config: dict = item.get("config", {})
            properties: dict = item.get("properties", {})

            for k, v in properties.items():
                try:
                    if "odcs_schema" in v:
                        odcs_content = glom(self._odcs_schema, v.get("odcs_schema", ""))
                        alias_: str = v.get("odcs_schema", "").split(".")[-1]
                        odcs_schema[k] = odcs_content | v | {"alias": alias_ if "alias" not in v else v.get("alias")}
                    else:
                        odcs_schema[k] = v
                except Exception as e:
                    # TODO: ADD LOG!
                    raise e

            model_schema[name.strip().capitalize()] = {
                "properties": odcs_schema,
                "config": config,
                "name": name.strip().capitalize(),
            }

        return model_schema


if __name__ == "__main__":
    y = Ygg()
    m = y.load_model_map()

    print(list(m.keys()))
    # print(m)
    print(m["Fundamentals"].config)
    print(m["Fundamentals"].properties[12])

    # for k, v in m["Fundamentals"].config:
    #     if isinstance(v, list):
    #         #     for x, y in v[0].model_dump():
    #         #         print(x, y)
    #         for i in v:
    #             model_: dict = i.model_dump(mode="python")
    #             for x, y in model_.items():
    #                 if x == "name":
    #                     print(" ", x, ": ", y)
    #                 else:
    #                     # if x == "properties" and y:
    #                     #     m = {model_["alias"].capitalize(): y}
    #                     #     print(m)
    #                     # elif x == "items" and y:
    #                     #     i_dt = y["properties"]["id"]
    #                     #     m = {model_["alias"].capitalize(): y}
    #                     #     print(m)
    #                     print("     ", x, ": ", y)
    #
    #     else:
    #         print(k, v)
