"""Polyglot Helper."""

from ygg.helpers.data_types import get_data_type
from ygg.helpers.logical_data_models import (
    ModelSettings,
    PolyglotEntity,
    PolyglotEntityColumn,
    PolyglotEntityColumnDataType,
)


class Helper:
    """Helper."""

    @staticmethod
    def cast_to_polyglot_entity(model: ModelSettings) -> PolyglotEntity:
        """Cast the model to a polyglot entity."""

        list_of_columns: list[PolyglotEntityColumn] = []
        for property_ in model.properties:
            data_type = get_data_type(property_.type, "physical")
            column_data_type = PolyglotEntityColumnDataType(
                data_type_name=property_.type,
                duck_db_type=data_type["type"],
                duck_db_regex_pattern=data_type.get("pattern", None),
                duck_lake_type=data_type["type"],
            )

            c: PolyglotEntityColumn = PolyglotEntityColumn(
                name=property_.name,
                data_type=column_data_type,
                enum=property_.enum,
                comment=property_.description,
                nullable=property_.required,
                primary_key=property_.primary_key,
                unique_key=property_.unique,
                check_constraint=None,
                default_value=property_.default
                if property_.default and property_.default != ...
                else None,
                default_value_function=property_.physical_default_function,
            )
            list_of_columns.append(c)

        _polyglot_entity: PolyglotEntity = PolyglotEntity(
            name=model.entity_name, columns=list_of_columns, schema_=model.entity_schema
        )

        return _polyglot_entity
