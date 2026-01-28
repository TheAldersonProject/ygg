"""Set of database operations and utilities for physical models."""

import duckdb

import ygg.config as config
from ygg.core.dynamic_models_factory import ModelSettings
from ygg.helpers.physical_model_helper import PhysicalModelHelper
from ygg.utils.ygg_logs import get_logger

"""
    *. connect to a database - options for physical -- DONE for physical! ✅
    *. connect to a database - options for memory 
    *. create the schema -- DONE! ✅
    *. create the physical model -- DONE! ✅
    *. generate fake
    *. reader connector for snowflake
    *. samples
    *. insert -- DONE! ✅
    *. update
    *. upsert | merge
    *. delete
    *. time travel
"""

logs = get_logger()

#
# class SnowflakeSettings(BaseSettings):
#     """Snowflake Connector Configuration."""
#
#     account: SecretStr
#     user: SecretStr
#     auth_type: str
#     authenticator: str
#     private_key_file: str
#     private_key_password: SecretStr
#     role: str
#     warehouse: str
#     database: str
#     schema_: str
#     read_only: bool = Field(default=True)
#
#     model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class PhysicalModelTools:
    """Tools for physical model operations."""

    def __init__(self, model: ModelSettings) -> None:
        logs.info("Initializing Physical Model Tools.")

        if not model:
            raise ValueError("Ygg Model Cannot be Empty.")

        self._model: ModelSettings = model
        self._helper: PhysicalModelHelper = PhysicalModelHelper(model)

        self._db_url: str = f"{config.DB_TEMPORARY_FOLDER}/file.duckdb"

    def _execute(self, statement: str, validation_query_console: str | None = None) -> bool:
        """Execute a SQL statement against the database."""

        with duckdb.connect(self._db_url, read_only=False) as con:
            try:
                logs.debug("Executing SQL statement.")
                con.execute(statement)
                logs.debug("SQL statement executed successfully.")

                if validation_query_console:
                    logs.debug("Executing validation query.")
                    try:
                        con.sql(validation_query_console).show()
                    except Exception as e:
                        logs.error(f"Error executing validation query: {e}")

                return True
            except Exception as e:
                logs.error(f"Error executing SQL statement: {e}")
                print(statement)
                raise e

    # @staticmethod
    # def create_snowflake_connector(settings: SnowflakeSettings) -> str:
    #     """Create a Snowflake connector for the physical model."""
    #
    #     p = settings.private_key_password
    #
    #     secret_name: str = "my_sso_secret"
    #     install_extension: str = """INSTALL snowflake FROM community;"""
    #     load_extension: str = """LOAD snowflake;"""
    #
    #     template: str = """
    #     CREATE SECRET IF NOT EXISTS {secret_name} (
    #         TYPE snowflake,
    #         ACCOUNT '{account}',
    #         DATABASE '{database}',
    #         WAREHOUSE '{warehouse}',
    #         AUTH_TYPE 'ext_browser'
    #     );
    #     """
    #
    #     test_connector: str = """SELECT snowflake_version();"""
    #
    #     attach_template: str = """
    #     -- Use the secret (browser will open for authentication)
    #     ATTACH '' AS sf (TYPE snowflake, SECRET {secret_name}, READ_ONLY={read_only});
    #     SELECT * FROM sf.schema.table LIMIT 10;
    #     """
    #
    #
    #     return ""

    def create_schema(self) -> None:
        """Create the schema for the physical model."""

        logs.info("Creating Schema.", schema=self._model.entity_schema)
        schema_ddl: str = self._helper.get_create_schema_ddl()
        schema_name = self._model.entity_schema.upper()

        validation_query: str = "SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE UPPER(schema_name) = '{schema_name}';"
        validation_query = validation_query.format(schema_name=schema_name)
        self._execute(schema_ddl, validation_query_console=validation_query)

        logs.info("Schema Created.", schema=self._model.entity_schema)

    def create_table(self, recreate_existing: bool = False) -> bool:
        """Create the schema table for the physical model."""

        logs.info("Creating Table.", table=self._model.entity_name)
        schema_ddl: str = self._helper.get_create_table_ddl(recreate_existing=recreate_existing)
        validation_query: str = f"""
            DESC TABLE {self._model.entity_schema.upper()}.{self._model.entity_name.upper()};
        """
        self._execute(schema_ddl, validation_query_console=validation_query)
        table_comments: list[str] = self._helper.get_table_columns_comments()
        if table_comments:
            self._execute("\n".join(table_comments))
            logs.info("Table Comments Created.")

        logs.info("Table Created.")
        return True

    # def insert_data(
    #     self, data: dict, hydrate_model: dict | None = None, on_conflict_ignore: bool = True
    # ) -> Union[int, dict]:
    #     """Insert data into the physical model."""
    #
    #     if not isinstance(data, dict):
    #         logs.error("Data must be a dictionary.")
    #         raise ValueError("Data must be a dictionary.")
    #
    #     entity: Type[YggBaseModel] = self._model.instance
    #     entity_schema: str = self._model.config.entity_schema
    #     entity_name: str = self._model.config.entity_name
    #     affected_rows: int = 0
    #     hydrate_return: dict = {}
    #     entity = entity(**data)
    #     values_map = entity.model_dump()
    #
    #     if hydrate_model:
    #         hydrate = {k: v for k, v in hydrate_model.items() if k in list(values_map.keys())}
    #         values_map.update(hydrate)
    #
    #     drop_columns: list = [c.name for c in self._model.properties if c.skip_from_physical_model]
    #     for drop in drop_columns or []:
    #         if values_map.get(drop):
    #             del values_map[drop]
    #
    #     signature_skip_columns = [c.name for c in self._model.properties if c.skip_from_signature]
    #     values_signature = "".join(
    #         list(sorted([str(v) for k, v in values_map.items() if v and k not in signature_skip_columns]))
    #     )
    #     record_hash = str(hashlib.md5(str(values_signature).encode()).hexdigest())
    #     values_map["record_hash"] = record_hash
    #
    #     pk_columns = [c.name for c in self._model.properties if c.primary_key]
    #     for pk in pk_columns:
    #         hydrate_return[f"{entity_name}_{pk}"] = values_map.get(pk)
    #
    #     header: list[str] = [f for f in list(entity.model_fields.keys())]
    #     params: list[str] = ", ".join(["?" for f in header])
    #     header_string: str = ", ".join(header)
    #
    #     values_list = list(values_map.values())
    #     statement: str = f"""INSERT INTO {entity_schema}.{entity_name} ({header_string}) VALUES ({params}) """
    #     # statement: str = f"""INSERT INTO {entity_schema}.{entity_name} ({header_string}) VALUES ({params}) {" ON CONFLICT DO NOTHING" if on_conflict_ignore else ""}"""
    #     print(statement)
    #     with duckdb.connect(self._db_url, read_only=False) as con:
    #         try:
    #             logs.debug("Executing SQL statement.")
    #             con.execute(statement, values_list)
    #             print(statement, values_list)
    #             logs.debug("SQL statement executed successfully.")
    #             affected_rows += 1
    #
    #         except Exception as e:
    #             logs.error(f"Error executing SQL statement: {e}", header_string=header_string, values=values_map)
    #             raise e
    #
    #     return affected_rows, hydrate_return

    # def load_contract_data(self, return_single_records: bool = True, **kwargs) -> list[dict]:
    #     """Load the contract into a dictionary."""
    #
    #     statement: str = (
    #         f"SELECT * FROM {self._model.config.entity_schema}.{self._model.config.entity_name} where true  "
    #     )
    #
    #     if kwargs:
    #         for k, v in kwargs.items():
    #             statement += f" AND {k} = {v}"
    #
    #     if return_single_records:
    #         statement += " LIMIT 1"
    #
    #     result = self.load_all_content(statement)
    #     result = result[0] if return_single_records else result
    #
    #     return result
    #
    # def load_all_content(self, statement: str | None = None) -> list[dict]:
    #     """Load the content of the physical model."""
    #
    #     with duckdb.connect(self._db_url, read_only=False) as con:
    #         if not statement:
    #             statement: str = (
    #                 f"SELECT * FROM {self._model.config.entity_schema}.{self._model.config.entity_name} where true  "
    #             )
    #
    #         content = con.sql(statement)
    #         content = content.to_df()
    #         # content.columns = content.columns.str.lower()
    #
    #         ygg_mapped_model: dict = {}
    #         for p in self._model.properties:
    #             if p.name.upper() in content.columns:
    #                 ygg_mapped_model[p.name.upper()] = p.alias or p.name
    #
    #         content = content.rename(columns=ygg_mapped_model)
    #         content = content.to_dict("records")
    #
    #         if not isinstance(content, list):
    #             content = [content]
    #
    #         return content
