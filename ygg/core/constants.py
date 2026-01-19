"""General constants for the project."""

import datetime
from uuid import UUID

from pydantic import UUID4

DATA_TYPE_DEFINITIONS = {
    "string": {"logical": str, "physical": "VARCHAR"},
    "text": {"logical": str, "physical": "TEXT"},
    "integer": {"logical": int, "physical": "INTEGER"},
    "bigint": {"logical": int, "physical": "BIGINT"},
    "float": {"logical": float, "physical": "FLOAT"},
    "decimal": {"logical": float, "physical": "DECIMAL"},
    "boolean": {"logical": bool, "physical": "BOOLEAN"},
    "date": {"logical": datetime.date, "physical": "DATE"},
    "datetime": {"logical": datetime.datetime, "physical": "DATETIME"},
    "timestamp": {"logical": datetime.datetime, "physical": "TIMESTAMP"},
    "timestamp_ltz": {"logical": datetime.datetime, "physical": "TIMESTAMP_LTZ"},
    "timestamp_ntz": {"logical": datetime.datetime, "physical": "TIMESTAMP_NTZ"},
    "timestamp_ns": {"logical": datetime.datetime, "physical": "TIMESTAMP_NS"},
    "timestamp_s": {"logical": datetime.datetime, "physical": "TIMESTAMP_S"},
    "uuid": {"logical": UUID, "physical": "UUID"},
    "uuid4": {"logical": UUID4, "physical": "UUID"},
    "json": {"logical": dict, "physical": "JSON"},
    "array": {"logical": list, "physical": "ARRAY"},
}


DUCKDB_SQL_DDL: dict = {
    "YggDataContractFundamentals": """-- creates the contract table if not exists
        create table if not exists data_contracts.contract(
          id varchar(256) not null unique,
          kind varchar(24) not null check (kind = 'DataContract'),
          api_version varchar(32) not null check (api_version = 'v3.1.0'),
          contract_name varchar(255) not null,
          tenant varchar(64) not null,
          contract_domain varchar(64) not null,
          contract_version varchar(24) not null unique,
          status varchar(24) not null,
          tags varchar[],
          data_product varchar(255),
          authoritative_definition struct(id varchar, url varchar, type varchar, description varchar),
          description struct(
              purpose varchar,
              limitations varchar,
              usage varchar,
              authoritative_definition struct(id varchar, url varchar, type varchar, description varchar),
              custom_properties struct(id varchar, property varchar, value varchar, description varchar)
            ),
          ygg_flow_type varchar(32) check (lower(ygg_flow_type) in ('input', 'output', 'transform')),
          version_ts timestamp,
          record_create_ts timestamp default get_current_timestamp(),
          record_update_ts timestamp default get_current_timestamp(),
          primary key ( id, contract_version )
        )
        ;    
    """,
    "YggDataContractSchema": """-- create the table contract_schema if not exists
    create table if not exists data_contracts.contract_schema(
      id varchar(256) not null primary key,
      contract_id varchar(256) not null references data_contracts.contract(id),
      contract_version varchar(24) not null references data_contracts.contract(contract_version),
      schema_name varchar(255) not null,
      physical_name varchar(255) not null,
      physical_type varchar(255) not null check (lower(physical_type) in ('view', 'table')),
      description varchar not null,
      business_name varchar(255) not null,
      authoritative_definition struct(id varchar, url varchar, type varchar, description varchar),
      tags varchar[],
      custom_properties struct(id varchar, property varchar, value varchar, description varchar),
      ygg_flow_type varchar(32) check (lower(ygg_flow_type) in ('input', 'output', 'transform')),
      server_name varchar not null references data_contracts.contract_server(server_name),
      data_granularity_description varchar(255),
      record_create_ts timestamp default get_current_timestamp(),
      record_update_ts timestamp default get_current_timestamp()
    )
    ;
    """,
    "YggDataContractServer": """-- create the contract_server table
    create table if not exists data_contracts.contract_server(
      id varchar(256) not null primary key,
      server_name varchar(256) not null unique,
      contract_id varchar(256) not null references data_contracts.contract(id),
      contract_version varchar(24) not null references data_contracts.contract(contract_version),
      server_type varchar(64) not null check (lower(server_type) in ('snowflake', 'duckdb', 'postgresql')),
      description varchar not null,
      environment varchar(255) not null check (lower(server_type) in ('production', 'staging', 'development', 'testing', 'qa', 'local', 'general')),
      custom_properties struct(id varchar, property varchar, value varchar, description varchar),
      database_name varchar(255),
      database_schema varchar(255),
      record_create_ts timestamp default get_current_timestamp(),
      record_update_ts timestamp default get_current_timestamp()
    )
    ;
    """,
    "YggDataContractServiceLevelAgreementContract": """-- create the table data_contracts.contract_sla if not exists
    create table if not exists data_contracts.contract_sla(
      id varchar(256) not null primary key,
      contract_id varchar(256) not null references data_contracts.contract(id),
      contract_version varchar(24) not null references data_contracts.contract(contract_version),
      property varchar(64) not null check (property in ('availability', 'latency', 'retention', 'throughput')),
      property_value UNION(str varchar, num integer, flt float, bln boolean) not null,
      property_unit char(2) not null check (property_unit in ('y', 'm', 'd', 'h', 'mn', 's', 'ms', 'ns' )),
      element varchar[] not null,
      driver varchar(32) check (driver in ('operational', 'regulatory', 'analytics')),
      description varchar not null,
      record_create_ts timestamp default get_current_timestamp(),
      record_update_ts timestamp default get_current_timestamp()
    )
    ;
    """,
    "YggDataContractServiceLevelAgreementSchema": """-- create the table contract_schema_sla if not exists
    create table if not exists data_contracts.contract_schema_sla(
      id varchar(256) not null primary key,
      contract_schema_id varchar(256) not null references data_contracts.contract_schema(id),
      property varchar(64) not null check (property in ('availability', 'latency', 'retention', 'throughput')),
      property_value UNION(str varchar, num integer, flt float, bln boolean) not null,
      property_unit char(2) not null check (property_unit in ('y', 'm', 'd', 'h', 'mn', 's', 'ms', 'ns' )),
      element varchar[] not null,
      driver varchar(32) check (driver in ('operational', 'regulatory', 'analytics')),
      description varchar not null,
      record_create_ts timestamp default get_current_timestamp(),
      record_update_ts timestamp default get_current_timestamp()
    )
    ;
    """,
    "YggDataContractSchemaProperty": """-- create the table contract_schema_property if not exists
    create table if not exists data_contracts.contract_schema_property(
      id varchar(256) not null primary key,
      contract_schema_id varchar(256) not null references data_contracts.contract_schema(id),
      property_name varchar(255) not null,
      physical_name varchar(255) not null,
      physical_type varchar(255) not null,
      description varchar not null,
      business_name varchar(255) not null,
      authoritative_definition struct(id varchar, url varchar, type varchar, description varchar),
      tags varchar[],
      custom_properties struct(id varchar, property varchar, value varchar, description varchar),
      primary_key bool default false,
      primary_key_position int,
      logical_type varchar not null check (lower(logical_type) in ('string', 'integer', 'decimal', 'boolean', 'date', 'timestamp', 'timestamp_ntz', 'timestamp_ltz', 'uuid', 'uuid4', 'json', 'array', 'object', 'float')),
      is_required bool default false,
      is_unique bool default false,
      is_partitioned bool default false,
      partition_key_position int,
      classification varchar(32),
      encrypted_name varchar(32),
      critical_data_element bool default false,
      examples varchar[],
      record_create_ts timestamp default get_current_timestamp(),
      record_update_ts timestamp default get_current_timestamp()
    )
    ;
    """,
}


def get_entity_ddl_from_class_name(class_name: str) -> str:
    return DUCKDB_SQL_DDL.get(class_name, "")
