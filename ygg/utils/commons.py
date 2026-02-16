"""Local files utilities."""

import base64
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


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


def replace_placeholders_with_env_values(config) -> dict[str, str | Any]:
    """Replace placeholders with environment variables."""
    load_dotenv()
    pattern = re.compile(r"\$\{([^}]+)\}")

    def replace_match(match):
        """Replace a match with the corresponding environment variable value."""
        var = match.group(1)
        if ":-" in var:
            var_name, default = var.split(":-", 1)
        else:
            var_name, default = var, None

        return os.getenv(var_name, default)

    def replace_dict(d) -> None:
        """Recursively replace placeholders in a dictionary."""
        for key, value in d.items():
            if isinstance(value, dict):
                replace_dict(value)
            elif isinstance(value, str):
                d[key] = pattern.sub(replace_match, value)

    replace_dict(config)

    return config


def get_json_signature(data: dict, algorithm: str = "sha256") -> str:
    """Generates a sha256 signature for a JSON object."""

    canonical_json = json.dumps(data, sort_keys=True, indent=None, separators=(",", ":"))
    hasher = hashlib.new(algorithm)
    hasher.update(canonical_json.encode("utf-8"))

    return hasher.hexdigest()


def pack_json_content_as_base64(content: dict) -> str:
    return base64.b64encode(json.dumps(content).encode("utf-8")).decode("utf-8")


def transform_html_to_markdown(html: str) -> str:
    """Transform HTML to Markdown."""
    if not isinstance(html, str):
        return html

    # convertion = convert(html)
    convertion = html
    return convertion or ""


def camel_to_snake(name: str) -> str:
    """
    Converts a camelCase string to a snake_case string.

    Handles acronyms and leading capitals correctly.
    """
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)

    return name.lower()
