"""Local files utilities."""

import json
from pathlib import Path

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


def get_yaml_from_json_content(json_content: dict) -> str:
    """Converts a JSON content to YAML format."""
    return yaml.dump(json.loads(json_content), sort_keys=False, default_flow_style=False, indent=4)


def save_yaml_content(file_path: str, content: dict) -> None:
    """Save YAML content to a file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as file:
        yaml.dump(content, file)
