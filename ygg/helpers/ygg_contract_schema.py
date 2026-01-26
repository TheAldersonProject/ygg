import ygg.config as config

FUNDAMENTALS: dict = {
    "fundamentals": {
        "name": "Fundamentals",
        "version": "0.0.1",
        "config": {
            "document_path": "fundamentals",
            "type": "object",
            "required": True,
            "entity_name": "contract",
            "entity_type": "table",
            "entity_schema": "data_contracts",
            "description": "This section contains general information about the contract. Fundamentals were also called demographics in early versions of ODCS.",
            "odcs_reference": "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/fundamentals",
        },
        "properties": {
            "api_version": {"odcs_schema": "properties.apiVersion", "enum": ["v3.1.0"]},
            "kind": {"odcs_schema": "properties.kind"},
            "id": {
                "odcs_schema": "properties.id",
                "alias": "id",
                "type": "StableId",
                "primary_key": True,
                "unique": False,
            },
            "name": {
                "type": "StructuredName",
                "odcs_schema": "properties.name",
                "primary_key": True,
            },
            "version": {
                "type": "SemanticalVersion",
                "odcs_schema": "properties.version",
                "skip_from_signature": True,
            },
            "status": {
                "enum": ["draft", "active", "deprecated"],
                "odcs_schema": "properties.status",
                "skip_from_signature": True,
            },
            "tenant": {
                "type": "StructuredName",
                "odcs_schema": "properties.tenant",
                "primary_key": True,
            },
            "tags": {
                "required": False,
                "type": "Tags",
                "odcs_schema": "$defs.Tags",
                "alias": "tags",
            },
            "domain": {
                "type": "StructuredName",
                "odcs_schema": "properties.domain",
                "primary_key": True,
            },
            "data_product": {
                "type": "StructuredName",
                "alias": "dataProduct",
                "required": False,
                "odcs_schema": "properties.dataProduct",
            },
            "authoritative_definitions": {
                "type": "AuthoritativeDefinitions",
                "alias": "authoritativeDefinitions",
                "required": False,
                "odcs_schema": "$defs.AuthoritativeDefinitions",
            },
            "description": {"type": "StructuredDescription", "odcs_schema": "properties.description"},
            "record_hash": {
                "type": "string",
                "description": "Record hash will be created while inserting. It ignores specific values to create the hash.",
                "alias": "recordHash",
                "required": False,
                "primary_key": True,
                "unique": False,
                "primary_key_position": 1,
                "skip_from_signature": True,
            },
            "record_creation_ts": {
                "type": "timestamp",
                "description": "Timestamp of the creation of the record.",
                "alias": "recordTimestamp",
                "required": False,
                "primary_key": False,
                "unique": False,
                "skip_from_signature": True,
                "default": None,
                "physical_default_function": "get_current_timestamp()",
            },
            "record_status_ts": {
                "type": "timestamp",
                "description": "Timestamp of the status change of the record.",
                "alias": "recordTimestamp",
                "required": False,
                "primary_key": False,
                "unique": False,
                "skip_from_signature": True,
                "default": None,
                "physical_default_function": "get_current_timestamp()",
            },
        },
    }
}

SERVER: dict = {
    "servers": {
        "name": "Servers",
        "version": "0.0.1",
        "config": {
            "document_path": "servers",
            "type": "object",
            "required": False,
            "entity_name": "contract_server",
            "entity_type": "table",
            "entity_schema": "data_contracts",
            "description": "The servers element describes where the data protected by this data contract is physically located.",
            "odcs_reference": "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/infrastructure-servers/",
        },
        "properties": {
            "server": {"odcs_schema": "$defs.Server.properties.server"},
            "id": {
                "odcs_schema": "$defs.StableId",
                "alias": "id",
                "type": "StableId",
                "primary_key": True,
            },
            "type": {
                "enum": ["snowflake", "duckdb", "postgresql"],
                "odcs_schema": "$defs.Server.properties.type",
            },
            "description": {"odcs_schema": "$defs.Server.properties.description", "type": "string"},
            "environment": {
                "enum": ["production", "staging", "development", "testing", "qa", "local", "general"],
                "odcs_schema": "$defs.Server.properties.environment",
            },
            "database_name": {
                "type": "StructuredName",
                "description": "Database Name.",
                "alias": "databaseName",
                "required": False,
            },
            "database_schema": {
                "type": "StructuredName",
                "description": "Schema Name.",
                "alias": "schemaName",
                "required": False,
            },
            "contract_id": {
                "type": "StableId",
                "description": "Contract Id.",
                "alias": "contractId",
                "required": False,
            },
            "contract_record_hash": {
                "type": "string",
                "description": "Contract Record Hash.",
                "alias": "contractRecordHash",
                "required": False,
            },
            "record_hash": {
                "type": "string",
                "description": "Record hash will be created while inserting. It ignores specific values to create the hash.",
                "alias": "recordHash",
                "required": False,
                "primary_key": True,
                "unique": False,
                "skip_from_signature": True,
            },
        },
    }
}

_SECTION_SLA_PROPERTIES: dict = {
    "sla": {
        "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId"},
        "property": {"odcs_schema": "$defs.ServiceLevelAgreementProperty.properties.property"},
        "property_value": {
            # "name": "property_value",
            "type": "Any",
            "description": "Agreement value. The label will change based on the property itself.",
            "alias": "value",
        },
        "property_unit": {
            "odcs_schema": "$defs.ServiceLevelAgreementProperty.properties.unit",
            "enum": ["y", "m", "d", "h", "mn", "s", "ms", "ns"],
        },
        "element": {"odcs_schema": "$defs.ServiceLevelAgreementProperty.properties.element"},
        "driver": {
            "odcs_schema": "$defs.ServiceLevelAgreementProperty.properties.driver",
            "enum": ["operational", "regulatory", "analytics"],
        },
        "description": {"odcs_schema": "$defs.ServiceLevelAgreementProperty.properties.description"},
    }
}

#
# _SCHEMA_ELEMENT = {
#     "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId"},
#     "name": {"odcs_schema": "$defs.SchemaElement.properties.name", "type": "StructuredName"},
#     "physical_type": {"odcs_schema": "$defs.SchemaElement.properties.physicalType"},
#     "description": {"odcs_schema": "$defs.SchemaElement.properties.description"},
#     "business_name": {"odcs_schema": "$defs.SchemaElement.properties.businessName", "type": "StructuredName"},
#     "authoritative_definitions": {
#         "type": "AuthoritativeDefinition",
#         "odcs_schema": "$defs.AuthoritativeDefinitions",
#     },
#     "tags": {"type": "Tags", "odcs_schema": "$defs.Tags"},
#     "custom_properties": {"type": "CustomProperties", "odcs_schema": "$defs.CustomProperties"},
# }
#
# _SECTION_SCHEMA_OBJECT_PROPERTY_PROPERTIES: dict = {
#     "schema_object_property": _SCHEMA_ELEMENT
#     | {
#         "primary_key": {"odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKey"},
#         "primary_key_position": {"odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKeyPosition"},
#         "logical_type": {"odcs_schema": "$defs.SchemaBaseProperty.properties.logicalType"},
#         "physical_type": {"odcs_schema": "$defs.SchemaBaseProperty.properties.physicalType"},
#         "physical_name": {"odcs_schema": "$defs.SchemaBaseProperty.properties.physicalName", "type": "StructuredName"},
#         "required": {"odcs_schema": "$defs.SchemaBaseProperty.properties.required"},
#         "unique": {"odcs_schema": "$defs.SchemaBaseProperty.properties.unique"},
#         "partitioned": {"odcs_schema": "$defs.SchemaBaseProperty.properties.partitioned"},
#         "partition_key_position": {"odcs_schema": "$defs.SchemaBaseProperty.properties.partitionKeyPosition"},
#         "classification": {"odcs_schema": "$defs.SchemaBaseProperty.properties.classification"},
#         "encrypted_name": {"odcs_schema": "$defs.SchemaBaseProperty.properties.encryptedName"},
#         "examples": {"odcs_schema": "$defs.SchemaBaseProperty.properties.examples", "type": "list_of_strings"},
#         "critical_data_element": {"odcs_schema": "$defs.SchemaBaseProperty.properties.criticalDataElement"},
#     }
# }

# _SECTION_SCHEMA_PROPERTIES: dict = {
#     "schema_object": _SCHEMA_ELEMENT
#     | {
#         "logical_type": {"odcs_schema": "$defs.SchemaObject.properties.logicalType", "enum": ["view", "table"]},
#         "physical_name": {"odcs_schema": "$defs.SchemaObject.properties.physicalName", "type": "StructuredName"},
#         "data_granularity_description": {"odcs_schema": "$defs.SchemaObject.properties.dataGranularityDescription"},
#         "properties": {
#             "type": "array",
#             "items": {"type": "SchemaProperties"},
#             "odcs_schema": "$defs.SchemaObject.properties.properties",
#             "skip_from_physical_model": True,
#         },
#     },
# }

SCHEMA_PROPERTY: dict = {
    "schema": {
        "name": "SchemaProperty",
        "version": "0.0.1",
        "config": {
            "document_path": "",
            "type": "object",
            "required": True,
            "entity_name": "contract_schema_property",
            "entity_type": "table",
            "entity_schema": "data_contracts",
            "description": "This entity describes the schema properties of the data contract.",
            "odcs_reference": "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/schema/#applicable-to-properties",
        },
        "properties": {
            "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId", "primary_key": True},
            "name": {"odcs_schema": "$defs.SchemaElement.properties.name", "type": "StructuredName"},
            "description": {"odcs_schema": "$defs.SchemaElement.properties.description"},
            "business_name": {"odcs_schema": "$defs.SchemaElement.properties.businessName", "type": "string"},
            "authoritative_definitions": {
                "type": "AuthoritativeDefinitions",
                "odcs_schema": "$defs.AuthoritativeDefinitions",
                "required": False,
            },
            "tags": {
                "type": "Tags",
                "odcs_schema": "$defs.Tags",
                "required": False,
            },
            "custom_properties": {
                "type": "CustomProperties",
                "odcs_schema": "$defs.CustomProperties",
                "required": False,
            },
            "primary_key": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKey",
                "required": False,
                "default": False,
            },
            "primary_key_position": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKeyPosition",
                "required": False,
                "type": "integer",
                "default": -1,
            },
            "logical_type": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.logicalType",
                "enum": [
                    "string",
                    "date",
                    "timestamp",
                    "time",
                    "number",
                    "integer",
                    "object",
                    "array",
                    "boolean",
                    "float",
                ],
            },
            "physical_type": {"odcs_schema": "$defs.SchemaBaseProperty.properties.physicalType"},
            "physical_name": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.physicalName",
                "type": "StructuredName",
            },
            "is_required": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.required",
                "alias": "required",
                "type": "boolean",
                "required": False,
                "default": True,
            },
            "is_unique": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.unique",
                "alias": "unique",
                "type": "boolean",
                "required": False,
                "default": False,
            },
            "is_partitioned": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.partitioned",
                "alias": "partitioned",
                "type": "boolean",
                "required": False,
                "default": False,
            },
            "partition_key_position": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.partitionKeyPosition",
                "required": False,
            },
            "classification": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.classification",
                "required": False,
            },
            "encrypted_name": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.encryptedName",
                "required": False,
            },
            "examples": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.examples",
                "type": "list_of_strings",
                "required": False,
            },
            "critical_data_element": {
                "odcs_schema": "$defs.SchemaBaseProperty.properties.criticalDataElement",
                "required": False,
                "default": False,
            },
            "contract_schema_id": {
                "type": "StableId",
                "description": "Contract Id.",
                "alias": "contractId",
                "required": False,
            },
            "contract_schema_record_hash": {
                "type": "string",
                "description": "Contract Record Hash.",
                "alias": "contractRecordHash",
                "required": False,
            },
            "record_hash": {
                "type": "string",
                "description": "Record hash will be created while inserting. It ignores specific values to create the hash.",
                "alias": "recordHash",
                "required": False,
                "primary_key": False,
                "unique": True,
                "skip_from_signature": True,
            },
        },
    }
}

SCHEMA: dict = {
    "schema": {
        "name": "Schema",
        "version": "0.0.1",
        "config": {
            "document_path": "schema",
            "type": "object",
            "required": True,
            "entity_name": "contract_schema",
            "entity_type": "table",
            "entity_schema": "data_contracts",
            "description": "This entity describes the schema of the data contract.",
            "odcs_reference": "https://bitol-io.github.io/open-data-contract-standard/v3.1.0/schema/",
        },
        "properties": {
            "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId", "primary_key": True},
            "name": {"odcs_schema": "$defs.SchemaElement.properties.name", "type": "StructuredName"},
            "physical_type": {"odcs_schema": "$defs.SchemaElement.properties.physicalType", "enum": ["view", "table"]},
            "description": {"odcs_schema": "$defs.SchemaElement.properties.description"},
            "business_name": {"odcs_schema": "$defs.SchemaElement.properties.businessName", "type": "string"},
            "authoritative_definitions": {
                "type": "AuthoritativeDefinitions",
                "alias": "authoritativeDefinitions",
                "required": False,
                "odcs_schema": "$defs.AuthoritativeDefinitions",
            },
            "tags": {
                "required": False,
                "type": "Tags",
                "odcs_schema": "$defs.Tags",
                "alias": "tags",
            },
            "custom_properties": {
                "type": "CustomProperties",
                "odcs_schema": "$defs.CustomProperties",
                "required": False,
            },
            "physical_name": {"odcs_schema": "$defs.SchemaObject.properties.physicalName", "type": "StructuredName"},
            "data_granularity_description": {"odcs_schema": "$defs.SchemaObject.properties.dataGranularityDescription"},
            "flow_type": {
                "type": "string",
                "description": "Database Name.",
                "alias": "flowType",
                "enum": ["input", "output", "transform", "map"],
            },
            "server_id": {
                "odcs_schema": "$defs.StableId",
                "alias": "serverId",
                "type": "StableId",
                "primary_key": False,
                "unique": True,
                "description": "Server Id.",
            },
            "contract_id": {
                "type": "StableId",
                "description": "Contract Id.",
                "alias": "contractId",
                "required": False,
            },
            "contract_record_hash": {
                "type": "string",
                "description": "Contract Record Hash.",
                "alias": "contractRecordHash",
                "required": False,
            },
            "record_hash": {
                "type": "string",
                "description": "Record hash will be created while inserting. It ignores specific values to create the hash.",
                "alias": "recordHash",
                "required": False,
                "primary_key": True,
                "primary_key_position": 3,
                "skip_from_signature": True,
            },
        },
    }
}

ODCS_SCHEMA: str = config.ASSETS_FOLDER_ODCS_SCHEMA / "odcs-json-schema-v3.1.0.json"
