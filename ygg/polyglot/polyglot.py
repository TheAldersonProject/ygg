"""Database Polyglot Service."""

import re
from typing import Annotated, Any, Optional, Type, Union

from pydantic import AliasChoices, ConfigDict, Field, create_model

from ygg.config import YggSetup
from ygg.core.shared_model_mixin import SharedModelMixin
from ygg.helpers.data_types import get_data_type
from ygg.helpers.logical_data_models import (
    PolyglotEntity,
    YggBaseModel,
)
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="Polyglot")


class Polyglot:
    """Database Polyglot Service."""

    def __init__(self, entity: PolyglotEntity):
        """Initialize the Database Polyglot Service."""

        if not entity:
            logs.error("Entity cannot be empty.")
            raise ValueError("Entity cannot be empty.")

        self._entity: PolyglotEntity = entity
        logs.info("Initializing Polyglot Service.", entity=self._entity.name)

        self._setup: YggSetup = YggSetup(create_ygg_folders=False, config_data=None)
        self._dynamic_instance: Type[Union[YggBaseModel, SharedModelMixin]] | None = None

    @property
    def instance(self) -> Type[Union[YggBaseModel, SharedModelMixin]]:
        """Get the dynamic model instance."""
        if not self._dynamic_instance:
            logs.error("Dynamic Model Instance not found.")
            raise ValueError("Dynamic Model Instance not found.")

        return self._dynamic_instance

    def build(self) -> None:
        """Build the dynamic model instances."""

        self._build_dynamic_model_instances()
        logs.info("Polyglot Instance Built.", instance=self.instance.__name__)

    def _build_dynamic_model_instances(self) -> None:
        """Build the dynamic model instances."""

        logical_entity_name = re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), self._entity.name)

        fields_map: dict[str, Any] = {}
        for col in self._entity.columns:
            field = Field(
                default=col.default_value,
                validation_alias=AliasChoices(col.name, col.alias),
                description=col.comment,
                examples=col.examples,
                pattern=col.data_type.regex_pattern,
            )

            logical_type = get_data_type(col.data_type.data_type_name, "logical")
            annotated_field = Annotated[
                logical_type["type"] if not col.nullable else Optional[logical_type["type"]], field
            ]
            fields_map[col.name] = annotated_field

        polyglot_field = Field(default=None, description="Polyglot Entity")
        polyglot_entity = Annotated[Optional[PolyglotEntity], polyglot_field]
        fields_map["polyglot_entity"] = polyglot_entity

        instance = create_model(
            logical_entity_name,
            __config__=ConfigDict(title=self._entity.comment),
            __base__=(YggBaseModel, SharedModelMixin),
            **fields_map,
        )

        logs.debug("Dynamic Model Instance Created.", instance=instance.__name__)
        self._dynamic_instance = instance


if __name__ == "__main__":
    from ygg.core.data_contract_loader import DataContractLoader
    from ygg.helpers.enums import Model
    from ygg.utils.commons import get_json_file_content, get_yaml_content

    additional_config = get_yaml_content("/home/thiago/projects/ygg/ygg/assets/ygg_schemas/config.yaml")
    dyna = DataContractLoader(
        model=Model.CONTRACT,
        data_contract_schema_config=additional_config,
        odcs_schema_reference=get_json_file_content(
            "/home/thiago/projects/ygg/ygg/assets/odcs_schemas/odcs-json-schema-v3.1.0.json"
        ),
        data_contract_schema=get_yaml_content("/home/thiago/projects/ygg/ygg/assets/ygg_schemas/schema.yaml"),
    )

    entity_ = dyna.polyglot_entity
    p = Polyglot(entity_)
    p.build()
    instance_ = p.instance

    contract = get_yaml_content("/home/thiago/projects/.ygg/local-dev/contract.yaml")
    contract = contract.get("schema", {})
    for c in contract:
        instance_ = instance_.inflate(data=c, polyglot_entity=entity_)

        from ygg.core.polyglot_contract import PolyglotContract

        # DataDocument(polyglot_entity=entity_).setup()
        w = PolyglotContract(entity=instance_).setup().write_contract()
        print(w)
        # PolyglotContract(entity=instance_).setup()
        # PolyglotContract(entity=instance_).write_contract()
