"""Project configuration."""

from pathlib import Path

CURRENT_FILE_PATH = Path(__file__).resolve()
SRC_FOLDER = CURRENT_FILE_PATH.parent
PROJECT_ROOT = SRC_FOLDER.parent

DOCS_FOLDER = PROJECT_ROOT / "docs"
DEV_FOLDER = PROJECT_ROOT / "dev"
DB_TEMPORARY_FOLDER = DEV_FOLDER / "data"

ASSETS_FOLDER = SRC_FOLDER / "assets"
ODCS_SCHEMA_FOLDER = ASSETS_FOLDER / "odcs_schemas"
YGG_SCHEMAS_FOLDER = ASSETS_FOLDER / "ygg_schemas"

YGG_SCHEMA_CONFIG_FILE = YGG_SCHEMAS_FOLDER / "config.yaml"
