_SECTION_FUNDAMENTALS_PROPERTIES: dict = {
    "fundamentals": {
        "name": "Fundamentals",
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
                "primary_key_position": 1,
                "unique": True,
            },
            "name": {"type": "StructuredName", "odcs_schema": "properties.name"},
            "version": {
                "type": "SemanticalVersion",
                "odcs_schema": "properties.version",
                "primary_key": True,
                "primary_key_position": 2,
            },
            "status": {"enum": ["draft", "active", "deprecated"], "odcs_schema": "properties.status"},
            "tenant": {"type": "StructuredName", "odcs_schema": "properties.tenant"},
            "tags": {"required": False, "type": "Tags", "odcs_schema": "$defs.Tags"},
            "domain": {"type": "StructuredName", "odcs_schema": "properties.domain"},
            "data_product": {
                "type": "StructuredName",
                "required": False,
                "odcs_schema": "properties.dataProduct",
            },
            "authoritative_definitions": {
                "type": "AuthoritativeDefinitions",
                "required": False,
                "odcs_schema": "$defs.AuthoritativeDefinitions",
            },
            "description": {"type": "StructuredDescription", "odcs_schema": "properties.description"},
            "ygg_flow_type": {
                # "name": "ygg_flow_type",
                "type": "string",
                "description": "Database Name.",
                "alias": "YggFlowType",
                "enum": ["input", "output", "transform"],
            },
        },
    }
}

_SERCTION_SERVER_PROPERTIES: dict = {
    "servers": {
        "server": {"odcs_schema": "$defs.Server.properties.server"},
        "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId"},
        "type": {"enum": ["snowflake", "duckdb", "postgresql"], "odcs_schema": "$defs.Server.properties.type", "": ""},
        "description": {"odcs_schema": "$defs.Server.properties.description"},
        "environment": {
            "enum": ["production", "staging", "development", "testing", "qa", "local", "general"],
            "odcs_schema": "$defs.Server.properties.description",
        },
        "custom_properties": {"type": "CustomProperties", "odcs_schema": "$defs.Server.properties.description"},
        "database_name": {
            "type": "StructuredName",
            "description": "Database Name.",
            "alias": "Database",
        },
        "database_schema": {
            "type": "StructuredName",
            "description": "Schema Name.",
            "alias": "Schema",
        },
    },
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

_SCHEMA_ELEMENT = {
    "id": {"odcs_schema": "$defs.StableId", "alias": "id", "type": "StableId"},
    "name": {"odcs_schema": "$defs.SchemaElement.properties.name", "type": "StructuredName"},
    "physical_type": {"odcs_schema": "$defs.SchemaElement.properties.physicalType"},
    "description": {"odcs_schema": "$defs.SchemaElement.properties.description"},
    "business_name": {"odcs_schema": "$defs.SchemaElement.properties.businessName", "type": "StructuredName"},
    "authoritative_definitions": {
        "type": "AuthoritativeDefinition",
        "odcs_schema": "$defs.AuthoritativeDefinitions",
    },
    "tags": {"type": "Tags", "odcs_schema": "$defs.Tags"},
    "custom_properties": {"type": "CustomProperties", "odcs_schema": "$defs.CustomProperties"},
}

_SECTION_SCHEMA_OBJECT_PROPERTY_PROPERTIES: dict = {
    "schema_object_property": _SCHEMA_ELEMENT
    | {
        "primary_key": {"odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKey"},
        "primary_key_position": {"odcs_schema": "$defs.SchemaBaseProperty.properties.primaryKeyPosition"},
        "logical_type": {"odcs_schema": "$defs.SchemaBaseProperty.properties.logicalType"},
        "physical_type": {"odcs_schema": "$defs.SchemaBaseProperty.properties.physicalType"},
        "physical_name": {"odcs_schema": "$defs.SchemaBaseProperty.properties.physicalName", "type": "StructuredName"},
        "required": {"odcs_schema": "$defs.SchemaBaseProperty.properties.required"},
        "unique": {"odcs_schema": "$defs.SchemaBaseProperty.properties.unique"},
        "partitioned": {"odcs_schema": "$defs.SchemaBaseProperty.properties.partitioned"},
        "partition_key_position": {"odcs_schema": "$defs.SchemaBaseProperty.properties.partitionKeyPosition"},
        "classification": {"odcs_schema": "$defs.SchemaBaseProperty.properties.classification"},
        "encrypted_name": {"odcs_schema": "$defs.SchemaBaseProperty.properties.encryptedName"},
        "examples": {"odcs_schema": "$defs.SchemaBaseProperty.properties.examples", "type": "list_of_strings"},
        "critical_data_element": {"odcs_schema": "$defs.SchemaBaseProperty.properties.criticalDataElement"},
    }
}

_SECTION_SCHEMA_PROPERTIES: dict = {
    "schema_object": _SCHEMA_ELEMENT
    | {
        "logical_type": {"odcs_schema": "$defs.SchemaObject.properties.logicalType", "enum": ["view", "table"]},
        "physical_name": {"odcs_schema": "$defs.SchemaObject.properties.physicalName", "type": "StructuredName"},
        "data_granularity_description": {"odcs_schema": "$defs.SchemaObject.properties.dataGranularityDescription"},
        "properties": {
            "type": "array",
            "items": {"type": "SchemaProperties"},
            "odcs_schema": "$defs.SchemaObject.properties.properties",
        },
    },
}

# _CONTRACT_BOK: dict = (
#     {}
#     | _SECTION_FUNDAMENTALS_PROPERTIES
#     | _SERCTION_SERVER_PROPERTIES
#     | _SECTION_SLA_PROPERTIES
#     | _SECTION_SCHEMA_PROPERTIES
# )

CONTRACT_BOK: dict = (
    {} | _SECTION_FUNDAMENTALS_PROPERTIES
    # | _SERCTION_SERVER_PROPERTIES
    # | _SECTION_SLA_PROPERTIES
    # | _SECTION_SCHEMA_PROPERTIES
)


ODCS_SCHEMA: str = "../assets/odcs-json-schema-{ODCS_VERSION}.json"
