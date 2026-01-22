"""Server Implementation."""

from typing import ClassVar, Optional

from pydantic import Field

import ygg.core.commons as commons
import ygg.core.odcs_fields as odcs_fields


class YggDataContractServer(commons.YggBaseModel):
    """Data Contract Server."""

    id: odcs_fields.StableId = Field(default=None, alias="id")
    server_name: odcs_fields.StableId = Field(default=None, alias="server")
    server_type: commons.YggDataContractServerType = Field(alias="type")
    description: Optional[str] = Field(default=None)
    environment: commons.YggDataContractServerEnvironment
    custom_properties: Optional[odcs_fields.CustomPropertiesField] = Field(
        default=None,
        alias="customProperties",
    )
    database_name: odcs_fields.StableId = Field(alias="database", description="Name of the database.")
    database_schema: odcs_fields.StableId = Field(alias="schema", description="Name of the schema in the database.")

    TABLE_NAME: ClassVar[str] = "contract_server"
    contract_id: odcs_fields.StableId = Field(default=None)
    contract_version: odcs_fields.StableId = Field(default=None)

    def model_hydrate(self, contract_id: odcs_fields.StableId, contract_version: odcs_fields.SemanticalVersionField):
        """Hydrate the model with the contract_id and contract_version."""

        if not self.contract_id or not self.contract_version:
            raise ValueError("Contract ID and version cannot be empty.")

        self.contract_id = contract_id
        self.contract_version = contract_version
