"""Local files utilities."""

import json

import yaml


def get_file_string_content(file_path: str) -> str:
    """Get file content as string."""
    with open(file_path, "r") as file:
        return file.read()


def get_json_file_content(file_path: str) -> dict:
    """Get file content as JSON."""

    with open(file_path, "r") as f:
        schema_content = json.load(f)

    return schema_content or {}


def get_yaml_content(file_path: str) -> dict:
    """Loads a YAML file and returns its content as a dictionary."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
