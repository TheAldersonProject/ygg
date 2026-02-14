"""Shared Model Mixin."""

from typing import Self

from glom import glom
from jinja2 import Template
from tabulate import tabulate

import ygg.utils.commons as cm
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

    @classmethod
    def inflate(cls, data: dict, model_hydrate: dict | None = None) -> Self:
        """Inflate the model."""

        logs.debug("Inflating Model.", name=cls.__name__)

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
                    for k, v in instance_value.items():
                        formatted_value += f"   - **`{k}`**: `{v}`\n"

                    instance_value = "\n" + formatted_value

                elif data_type == "string" and value.get("format", "") == "date-time":
                    if isinstance(instance_value, str):
                        from dateutil.parser import parse

                        instance_value = parse(instance_value)

                    instance_value = instance_value.strftime("%Y-%m-%d %H:%M:%S")

                # if isinstance(instance_value, str) and len(instance_value) > 100:
                #     instance_value = instance_value[:100] + "..."

                template_ += f"#### **{value['title']}:**\n {instance_value}\n"

            template = Template(template_)
            rendered = template.render(**values_)

            return cm.transform_html_to_markdown(rendered)

        return ""
