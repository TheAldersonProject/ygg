-- create the contract_server table
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