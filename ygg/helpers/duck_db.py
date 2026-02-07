"""DuckDB Helper."""

from pathlib import Path

import duckdb

import ygg.config as constants
import ygg.helpers.physical_db_helpers as db_helpers
from ygg.helpers.ygg_models import TargetContractMap, TargetContractSchemaMap
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class DuckDbHelper:
    """DuckDB Helper."""

    def __init__(
        self,
        contract: TargetContractMap,
        db_in_path: str | None = None,
        db_out_path: str | None = None,
        replace_existing: bool = False,
    ):
        """Initialize the DuckDB Helper."""

        logs.debug("Initializing DuckDB Helper.")

        self._contract: TargetContractMap = contract
        self._catalog: str = contract.catalog
        self._catalog_schema: str = contract.catalog_schema
        self._replace_existing: bool = replace_existing

        self._db_in_path: str = db_in_path or constants.DATABASE_FOLDER
        self._db_out_path: str | Path = db_out_path or constants.YGG_DBS_FOLDER
        self._db_out_name: str = contract.catalog

    def build_output(self) -> None:
        """Build the output database."""

        logs.debug(f"Building output database for contract: {self._contract.id}")
        if isinstance(self._db_out_path, str):
            self._db_out_path = Path(self._db_out_path)
        self._db_out_path.mkdir(parents=True, exist_ok=True)
        self._create_database()
        logs.debug("Output database built successfully.")

    def _create_database(self) -> None:
        """Create the DuckDB database."""

        db_file_name: str = f"{self._db_out_name}.duckdb"
        db_path = self._db_out_path / db_file_name
        ddb = duckdb.connect(read_only=False, database=db_path)

        ddb.execute("install ducklake")
        ddb.execute("load ducklake")

        dl_attach_stmt: str = f"""
            ATTACH '{self._contract.catalog_schema.lower()}' (
                TYPE ducklake,
                METADATA_PATH '{self._db_in_path}',
                DATA_PATH '{self._db_in_path}'
            )
        """
        ddb.execute(dl_attach_stmt)

        ddb.execute(self._get_ddl_create_catalog_schema())

        logs.debug("Database Created.", db_path=str(db_path))

        for schema_ in self._contract.schemas:
            logs.debug("Creating schema.", entity=schema_.entity)
            ddb.execute(self._get_ddl_create_schema_entity(schema_))

    def _get_ddl_create_catalog_schema(self) -> str:
        """Generate DDL to create a DuckDB catalog schema based on the provided contract schema."""

        return db_helpers.CREATE_CATALOG_SCHEMA_IF_NOT_EXISTS.format(catalog_schema=self._catalog_schema.upper())

    def _get_ddl_create_schema_entity(self, contract_schema: TargetContractSchemaMap) -> str:
        """Generate DDL to create a DuckDB schema entity based on the provided contract schema."""

        create_table_header: str = db_helpers.CREATE_TABLE_IF_NOT_EXISTS_HEADER
        if self._replace_existing:
            create_table_header = db_helpers.CREATE_TABLE_OR_REPLACE_HEADER

        create_table_header = create_table_header.format(
            catalog_schema=self._catalog_schema, table_name=contract_schema.entity
        )
        create_table_header = create_table_header.upper()

        properties_ddl: list[str] = []
        primary_key_list: list[str] = []
        for prop in contract_schema.properties:
            property_ddl: str = db_helpers.DDL_COLUMN_TEMPLATE

            is_nullable: str = " NOT NULL" if prop.is_required else ""
            is_key: str = "" if prop.is_key else ""
            is_unique: str = " UNIQUE" if prop.is_unique else ""
            is_pk_unique: str = is_key + is_unique
            property_ddl = property_ddl.format(
                field_name=prop.name.upper(),
                field_type=prop.physical_type.upper(),
                nullable=is_nullable,
                field_pk_uc=is_pk_unique,
                default_value="",
                field_check_constraint="",
            )
            properties_ddl.append(property_ddl)
            if prop.is_key:
                primary_key_list.append(prop.name.upper())

        ddl_statement: str = db_helpers.DDL_CREATE_TABLE_STATEMENT_TEMPLATE
        if primary_key_list:
            properties_ddl.append(f"PRIMARY KEY ({', '.join(primary_key_list)})")
        properties_ddl_str = ",\n".join(properties_ddl)
        ddl_statement = ddl_statement.format(
            create_table_header=create_table_header,
            fields_ddl_block=properties_ddl_str,
        )

        return ddl_statement
