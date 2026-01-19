-- create the table contract_schema if not exists
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