"""Core service factory module for Ygg.

This module provides a factory for creating and managing services within the Ygg framework.
"""

from typing import Type

from pydantic import Field

from ygg.core.logical_model_factory import LogicalModelFactory
from ygg.helpers.logical_model_helper import YggBaseModel, YggModel
from ygg.services.physical_model_tools import PhysicalModelTools

"""
    * read the contract structure:
        * fundamentals
        * servers
        * schema
            * schema properties
    * create the target database
    * create the target schema
    * create the target tables (schemas) for the contract
    *     

    ### How to
    
    1. load the contract into pydantic models
    2. 

"""


class ServiceFilter(YggBaseModel):
    """Service Filter."""

    name: str | None = Field(default=None)
    id: str | None = Field(default=None)
    record_hash: str | None = Field(default=None)
    version: str | None = Field(default=None)


class ServiceFactory:
    """Service Factory."""

    def __init__(self, service_filter: ServiceFilter | None = None) -> None:
        """Initialize the Service Factory."""

        if not service_filter:
            raise ValueError("Service Service Filter must be informed.")

        if (
            not service_filter.id
            and not service_filter.name
            and not service_filter.record_hash
            and not service_filter.version
        ):
            raise ValueError("Service Service Filter must have at least one filter.")

        self._filter: ServiceFilter = service_filter
        self._logical_model: LogicalModelFactory = LogicalModelFactory()

    def service_factory(self) -> None:
        """Service Factory."""

        contract: Type[YggBaseModel] = self._load_contract()

    def _load_contract(self) -> Type[YggBaseModel]:
        """Load the contract model."""

        filters_kp: dict = {}
        if self._filter.id:
            filters_kp["id"] = f"'{self._filter.id}'"

        if self._filter.version:
            filters_kp["version"] = f"'{self._filter.version}'"

        if self._filter.record_hash:
            filters_kp["record_hash"] = f"'{self._filter.record_hash}'"

        if self._filter.name:
            filters_kp["name"] = f"'{self._filter.name}'"

        contract: Type[YggModel] = self._logical_model.contract

        tools: PhysicalModelTools = PhysicalModelTools(model=contract)
        contract_data: dict = tools.load_contract_data()

        contract_data = contract_data[0] if isinstance(contract_data, list) else contract_data
        model = contract.instance(**contract_data)

        return model

    def load_contract_server(self, contract: Type[YggBaseModel]) -> Type[YggBaseModel]:
        """Load the contract server into a dictionary."""

        export_keys: dict = {"contract_id": contract.id, "contract_record_hash": contract.record_hash}
        servers: Type[YggModel] = self._logical_model.servers

        tools: PhysicalModelTools = PhysicalModelTools(model=servers)
        servers_data: dict = tools.load_contract_data()

        servers_data = servers_data[0] if isinstance(servers_data, list) else servers_data
        model = contract.instance(**servers_data)

        return model
