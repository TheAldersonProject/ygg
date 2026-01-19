"""Ygg Model Parser Module."""

from typing import Type

from pydantic import BaseModel
from yaml import YAMLError

from ygg.core.models import YggDataContract
from ygg.utils import ygg_logs
from ygg.utils.yaml_utils import get_yaml_content

logs = ygg_logs.get_logger()


class YggParser:
    """Ygg Parser Class.

    This module provides functionality to parse and process Ygg Data Models.
    """

    @staticmethod
    def load_data_model_from_file(file_path: str) -> "YggParser":
        """Loads a Data Model from a YAML file."""
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty.")

        data_model = YggParser._load_file_content(file_path=file_path)
        return YggParser(data_model=data_model)

    @staticmethod
    def _load_file_content(file_path: str) -> dict:
        """Retrieves a YAML file content as a dictionary."""
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty.")

        try:
            yaml_content = get_yaml_content(file_path=file_path)

        except FileNotFoundError:
            logs.error("File not found.", file_path=file_path)
            raise ValueError("It was not possible to load the content due to file not found error.")

        except YAMLError as yml:
            logs.error("YAML error.", yml=yml)
            raise ValueError(f"It was not possible to load the content due to YAML error: {yml}")

        return yaml_content

    def __init__(self, data_model: dict) -> None:
        """Initialize the Ygg Parser Module."""
        if not data_model:
            raise ValueError("Data Model cannot be empty.")

        self._data_model = data_model
        self._ygg_data_model: YggDataContract = YggDataContract(**data_model)

    @property
    def ygg_data_model(self) -> YggDataContract:
        """Returns the parsed Ygg Data Model."""
        return self._ygg_data_model

    def data_model_instance(self) -> Type[BaseModel]:
        """Returns the Pydantic model of the YggDataModel."""
        return self.ygg_data_model.logical_model_factory()
