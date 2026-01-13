"""Ygg Data Model Implementation."""

from typing import Any, Optional, Type

from pydantic import BaseModel, Field, create_model

from ygg.core import constants
from ygg.core.base_models import YggBaseModel, YggDataModelAttributes, YggDataModelProperty
from ygg.utils import logging

logs = logging.get_logger()


class YggDataModel(YggDataModelAttributes):
    """Ygg Data Model Implementation."""

    properties: Optional[list[YggDataModelProperty]] = Field(default=None)

    def logical_model_factory(self) -> Type[BaseModel]:
        """Returns the Pydantic model of the YggDataModel."""

        logs.debug("Starting: create pydantic model for entity.", entity=self.entity)

        base_class: Type[BaseModel] = YggBaseModel
        logs.debug("Setting: base class.", base_class=base_class.__name__)

        model_name = self.entity.strip().replace("_", " ").title().replace(" ", "")
        logs.debug("Setting: model name.", model_name=model_name)

        fields_definition: dict[str, Any] = {}

        logs.debug("Creating fields definition.")
        for idx, prop in enumerate(self.properties, start=1) or []:
            logical = prop.logical_implementation
            field_name = logical.name.strip()
            logs.debug("Setting: field name.", index=idx, field_name=field_name)

            dtf = constants.DATA_TYPE_DEFINITIONS
            logical_data_type = logical.data_type.strip().lower()
            logs.debug("Read: model data type.", index=idx, model_data_type=logical_data_type)

            python_data_type = dtf.get(logical_data_type, {}).get("logical_implementation", str)
            logs.debug("Setting: python data type.", index=idx, python_data_type=str(python_data_type))

            logs.debug("Setting: required field.", index=idx, required_field=logical.required)
            if not logical.required:
                python_data_type = Optional[python_data_type]
                default_value = logical.default_value
            else:
                default_value = ...

            logs.debug("Setting: default_value.", index=idx, required_field=logical.default_value)

            field_info = Field(
                default=default_value,
                alias=logical.alias,
                title=logical.title,
                coerce_numbers_to_str=logical.coerce_numbers_to_str,
                description=logical.description,
            )

            fields_definition[field_name] = (python_data_type, field_info)
            logs.debug("Field created.", index=idx, field_name=field_name)

        logs.debug("Creating model.", model_name=model_name)
        model = create_model(model_name, __base__=base_class, **fields_definition)

        logs.debug("Model created.", model_name=model_name)
        logs.debug("End: create pydantic model for entity.", entity=self.entity)

        return model
