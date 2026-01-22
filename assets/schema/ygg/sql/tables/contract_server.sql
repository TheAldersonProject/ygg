-- create the contract_server table
create table if not exists data_contracts.contract_server(
  id StableId not null primary key,
  server_name StableId not null unique,
  contract_id StableId not null references data_contracts.contract(id),
  contract_version StableId not null references data_contracts.contract(contract_version),
  server_type ServerType not null,
  description varchar(255) not null,
  environment Environment not null,
  custom_properties CustomProperty[],
  database_name StableId,
  database_schema StableId,
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp()
)
;