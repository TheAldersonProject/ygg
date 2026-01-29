"""Ygg Factory Module

This module provides a factory class for creating Ygg objects based on configuration data.
"""

import ygg.config as configs
from ygg.helpers.duck_db import DuckDbHelper
from ygg.helpers.ygg_models import TargetContractMap
from ygg.services.physical_model_tools import PhysicalModelTools
from ygg.utils.files_utils import save_yaml_content
from ygg.utils.ygg_logs import get_logger

logs = get_logger()


class YggFactory:
    """Factory for creating Ygg objects."""

    def __init__(self, contract_id: str, contract_version: str, db_url: str | None = None):
        """Initialize the Ygg Factory."""

        logs.debug(f"Initializing Ygg Factory for contract: {contract_id} version: {contract_version}")

        if not contract_id or not contract_version:
            raise ValueError("Contract ID and version cannot be empty.")

        self._contract_id = contract_id
        self._contract_version = contract_version
        self._target_contract_map: TargetContractMap | None = None
        self._db_url = db_url if db_url else ":memory:"

        logs.debug("Ygg Factory Initialized.")

    @property
    def contract_map(self):
        return self._target_contract_map

    def _db_load_target_contract(self) -> None:
        """Load the target contract."""

        contract_stmt: str = f"""
                select  id as "id",
                        version as "version",
                        record_hash as "record_hash" ,
                        tenant as "catalog",
                        domain as "catalog_schema"
                from    data_contracts.contract c
                where   true
                and     c.id = '{self._contract_id}' and c.version = '{self._contract_version}';"""
        contract = PhysicalModelTools.run_sql_statement(self._db_url, contract_stmt)
        contract_pk: dict = {
            "id": contract[0]["id"],
            "version": contract[0]["version"],
            "record_hash": contract[0]["record_hash"],
        }

        contract_schema_stmt: str = f"""
                select  id as "id", record_hash as "record_hash",
                        physical_name as "entity", physical_type as "physical_type",
                        contract_id as "contract_id", contract_record_hash as "contract_record_hash"
                from    data_contracts.contract_schema c 
                where   true 
                and     c.contract_id = '{self._contract_id}'
                and     c.contract_record_hash = '{contract_pk["record_hash"]}';
            """
        contract_schema = PhysicalModelTools.run_sql_statement(self._db_url, contract_schema_stmt)

        for sc_ in contract_schema:
            contract_schema_pk: dict = {
                "contract_schema_id": sc_["id"],
                "contract_schema_record_hash": sc_["record_hash"],
            }
            contract_schema_property_stmt: str = f"""
                select  physical_name as "name", description as "description", primary_key as "is_key",
                        is_unique as "is_unique", is_required as "is_required", physical_type as "physical_type",
                        ID as "id", record_hash as "record_hash", contract_schema_id as "contract_schema_id",
                        contract_schema_record_hash as "contract_schema_record_hash"
                from    data_contracts.contract_schema_property c 
                where   true 
                and     c.contract_schema_id = '{contract_schema_pk["contract_schema_id"]}'
                and     c.contract_schema_record_hash = '{contract_schema_pk["contract_schema_record_hash"]}';
            """
            contract_schema_properties = PhysicalModelTools.run_sql_statement(
                self._db_url, contract_schema_property_stmt
            )
            sc_["properties"] = contract_schema_properties

        contract_ = contract[0]
        contract_["schemas"] = contract_schema
        contract_map = TargetContractMap(**contract_)
        self._target_contract_map = contract_map

    def _sink_ygg_contract(self, sink_path: str) -> None:
        """Sink the Ygg Contract."""

        contract_map = self.contract_map
        sink_contract_root_folder = contract_map.catalog
        sink_contract_folder = contract_map.catalog_schema

        for sc in contract_map.schemas:
            sink_contract_file_name = f"{sc.entity}.yaml"
            path_ = sink_path / sink_contract_root_folder / sink_contract_folder / sink_contract_file_name
            json_content = sc.model_dump()
            save_yaml_content(path_, json_content)

    def _sink_database(self) -> None:
        ddb = DuckDbHelper(self._target_contract_map, replace_existing=True)
        ddb.build_output()

    def build_ygg_contract(self, sinc_result: bool = True, sink_path: str | None = None) -> None:
        """Build the Ygg Contract."""

        sink_path = sink_path if sink_path else configs.YGG_MAPS_FOLDER
        self._db_load_target_contract()
        if sinc_result:
            self._sink_ygg_contract(sink_path)
            self._sink_database()
