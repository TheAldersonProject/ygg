-- create the table data_contracts.contract_sla if not exists
create table if not exists data_contracts.contract_sla(
  id StableId not null primary key,
  contract_id StableId not null references data_contracts.contract(id),
  contract_version StableId not null references data_contracts.contract(contract_version),
  property SlaProperty not null,
  property_value SlaPropertyValue not null,
  property_unit SlaPropertyUnit not null,
  element varchar[] not null,
  driver SlaDriver not null,
  description varchar(255) not null,
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp()
)
;