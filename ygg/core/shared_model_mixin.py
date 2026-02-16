"""Shared Model Mixin."""

from typing import Any, Self

from glom import glom
from jinja2 import Template
from tabulate import tabulate

import ygg.utils.commons as cm
from ygg.helpers.logical_data_models import PolyglotEntity, YggBaseModel
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="SharedModelMixin")


class SharedModelMixin:
    """Shared Model Mixin."""

    def _model_hydrate(self, hydrate_data: dict) -> None:
        """Hydrate the model."""

        if not hydrate_data:
            return

        me = self
        dct = {k: v for k, v in hydrate_data.items() if k in me.model_fields}  #  type: ignore
        for k, v in dct.items():
            setattr(self, k, v)

    @property
    def statement_map(self) -> dict[str, Any]:
        """Get the insert statement."""

        from ygg.helpers.logical_data_models import PolyglotEntity

        entity: PolyglotEntity = None
        me: YggBaseModel = self

        if isinstance(me, YggBaseModel):
            if polyglot_entity := getattr(me, "polyglot_entity", None):
                entity = polyglot_entity
            else:
                return None

        values_map = me.model_dump()
        entity_catalog: str = entity.catalog
        entity_schema: str = entity.schema_
        entity_name: str = entity.name

        signature_skip_columns = [c.name for c in entity.columns if c.skip_from_signature]
        signature_dictionary = {k: v for k, v in values_map.items() if v and k not in signature_skip_columns}
        record_signature = cm.get_json_signature(signature_dictionary)

        values_map["record_hash"] = record_signature
        logs.debug("Record signature", signature=record_signature)

        empty_columns = [k for k, v in values_map.items() if v in (None, "None", "")]
        non_model_columns = [m for m in list(values_map.keys()) if m not in [e.name for e in entity.columns]]
        drop_columns: list = [
            c.name
            for c in entity.columns
            if c.skip_from_physical_model or c.name in empty_columns or c.name in non_model_columns
        ] + non_model_columns or []

        if drop_columns:
            logs.debug("Dropping columns from the model.", columns=drop_columns)

        for drop in drop_columns or []:
            if drop in values_map:
                del values_map[drop]

        primary_key_columns: list[str] = [c.name for c in entity.columns if c.primary_key]
        hydrate_return: dict = {}
        for pk in primary_key_columns:
            hydrate_return[f"{entity_name}_{pk}"] = values_map.get(pk)

        first_layer_db_header: list[str] = [
            f
            for f in me.model_fields.keys()
            if f in list(values_map.keys()) and f in [c.name for c in entity.columns] and f not in drop_columns
        ]
        params: list[str] = ", ".join(["?" for f in first_layer_db_header])
        first_layer_db_header_string: str = ", ".join(first_layer_db_header)

        second_layer_db_header: list[str] = [c.name for c in entity.columns]
        second_layer_db_header_string: str = ", ".join(second_layer_db_header)

        values_list = list(values_map.values())
        values_list = [None if v in ("None", ...) else v for v in values_list]

        on_conflict_ignore = not entity.update_allowed
        first_layer_db_insert_statement: str = f"""INSERT INTO {entity_schema}.{entity_name} ({first_layer_db_header_string}) VALUES ({params}) {" ON CONFLICT DO NOTHING" if on_conflict_ignore else ""}"""

        logs.debug("First Layer Database Insert Statement Created.")

        second_layer_db_insert_statement: str = f"""INSERT INTO {entity_catalog}.{entity_schema}.{entity_name} ({second_layer_db_header_string})SELECT {second_layer_db_header_string} FROM {entity_schema}.{entity_name}"""
        second_layer_merge_constraints = "".join([f" and t.{pk} = s.{pk}" for pk in primary_key_columns])
        second_layer_db_merge_statement: str = f"""
            MERGE INTO {entity_catalog}.{entity_schema}.{entity_name} t
            USING (SELECT {second_layer_db_header_string} FROM {entity_schema}.{entity_name}) s
            ON (1=1 {second_layer_merge_constraints}) 
            {"WHEN MATCHED THEN UPDATE" if entity.update_allowed else ""}
            WHEN NOT MATCHED THEN INSERT
        """

        logs.debug("Second Layer Database Insert Statement Created.")
        statement_map = {
            "hydrate_return": hydrate_return,
            "first_layer_db_write_statement": first_layer_db_insert_statement,
            "first_layer_db_write_values": values_list,
            "second_layer_db_insert_statement": second_layer_db_insert_statement,
            "second_layer_db_merge_statement": second_layer_db_merge_statement,
        }
        logs.info("Insert Statement Created.")

        return statement_map

    @classmethod
    def inflate(cls, data: dict, polyglot_entity: PolyglotEntity, model_hydrate: dict | None = None) -> Self:
        """Inflate the model."""

        logs.debug("Inflating Model.", name=cls.__name__)

        data.update({"polyglot_entity": polyglot_entity})
        model = cls(**data)
        if model_hydrate:
            model._model_hydrate(model_hydrate)

        return model

    @property
    def content_report(self) -> str:
        """Build a content report in Markdown format."""

        def sanitize_for_markdown_table(data_list):
            sanitized_list = []
            for row in data_list:
                new_row = {}
                for key, value in row.items():
                    # Replace literal newlines with HTML <br> tag
                    v_ = cm.transform_html_to_markdown(str(value))
                    v_ = v_.replace("\n", " ").replace("<br>", " ").strip()
                    new_row[key] = v_
                sanitized_list.append(new_row)
            return sanitized_list

        template_ = """# Document: {{ title }} - {{ description }}\n### Attributes:\n"""
        model_as_json = self.model_json_schema()
        model_instance_as_dict = self.model_dump()

        values_ = {
            "title": glom(model_as_json, "title", default="No title available"),
            "description": glom(model_as_json, "description", default="No description available."),
        }
        if "properties" in model_as_json:
            for key, value in model_as_json["properties"].items():
                if "$ref" in value:
                    value = model_as_json["$defs"][value["$ref"].split("/")[-1]]

                data_type = value["type"] if "type" in value else "string"
                instance_value = glom(model_instance_as_dict, f"{key}", default={})

                if not instance_value:
                    continue

                if isinstance(instance_value, list):
                    if isinstance(instance_value[0], dict):
                        instance_value = tabulate(
                            sanitize_for_markdown_table(instance_value),
                            headers="keys",
                            tablefmt="github",
                        )

                    else:
                        instance_value = [f"    - {i}" for i in instance_value]
                        instance_value = "\n".join(instance_value)
                        instance_value = "\n" + instance_value

                elif isinstance(instance_value, dict):
                    formatted_value = "\n"
                    lov = []
                    for k, v in instance_value.items():
                        formatted_value += f"   - **`{k}`**: `{v}`\n"
                        lov.append(formatted_value)

                    instance_value = "".join(lov)

                elif data_type == "string" and value.get("format", "") == "date-time":
                    if isinstance(instance_value, str):
                        from dateutil.parser import parse

                        instance_value = parse(instance_value)

                    instance_value = instance_value.strftime("%Y-%m-%d %H:%M:%S")

                title_ = value["title"] if "title" in value else key.capitalize()
                template_ += f"#### **{title_}:**\n {instance_value}\n"

            template = Template(template_)
            rendered = template.render(**values_)

            return cm.transform_html_to_markdown(rendered)

        return ""
