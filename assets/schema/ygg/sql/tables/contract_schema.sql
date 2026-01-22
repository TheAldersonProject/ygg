-- create the table contract_schema if not exists
create table if not exists data_contracts.contract_schema(
  id StableId not null primary key,
  contract_id StableId not null references data_contracts.contract(id),
  contract_version varchar(24) not null references data_contracts.contract(contract_version),
  schema_name StableId not null,
  physical_name StableId not null,
  physical_type SchemaPhysicalType not null,
  description varchar(255) not null,
  business_name varchar(255) not null,
  authoritative_definition AuthoritativeDefinition[],
  tags Tags,
  custom_properties CustomProperty[],
  ygg_flow_type YggFlowType not null,
  server_name StableId not null references data_contracts.contract_server(server_name),
  data_granularity_description varchar(255),
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp()
)
;