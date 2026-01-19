"""Ygg Data Model Implementation."""

from typing import Any, Optional, Type

from pydantic import BaseModel, Field, create_model

from ygg.core import constants
from ygg.core.models import YggBaseModel, YggDataContract, YggDataContractSchema
from ygg.utils import ygg_logs

logs = ygg_logs.get_logger()


class DataContract(YggDataContract):
    """Ygg Data Contract Implementation."""

    def logical_model_factory(self) -> Type[BaseModel]:
        """Returns the Pydantic model of the DataContract."""

        base_class: Type[BaseModel] = YggBaseModel

        # model_name: str = self.entity.strip().replace("_", " ").title().replace(" ", "")

        if self.schema_ and isinstance(self.schema_, list):
            for item in self.schema_ or []:
                fields_definition: dict[str, Any] = {}
                sc: YggDataContractSchema = item
                model_name: str = sc.business_name or sc.name
                model_description: str = sc.description or ""

                for idx, prop in enumerate(self.properties, start=1) or []:
                    logical = prop.logical_implementation
                    field_name = logical.name.strip()

                    dtf = constants.DATA_TYPE_DEFINITIONS
                    logical_data_type = logical.data_type.strip().lower()

                    python_data_type = dtf.get(logical_data_type, {}).get(
                        "logical_implementation", str
                    )

                    if not logical.required:
                        python_data_type = Optional[python_data_type]
                        default_value = logical.default_value
                    else:
                        default_value = ...

                    field_info = Field(
                        default=default_value,
                        alias=logical.alias,
                        title=logical.title,
                        coerce_numbers_to_str=logical.coerce_numbers_to_str,
                        description=logical.description,
                    )

                    fields_definition[field_name] = (python_data_type, field_info)

                model = create_model(
                    model_name, __base__=base_class, **fields_definition
                )

        return model
