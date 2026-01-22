-- create the table contract_schema_sla if not exists
create table if not exists data_contracts.contract_schema_sla(
  id StableId not null primary key,
  contract_schema_id StableId not null references data_contracts.contract_schema(id),
  property SlaProperty not null,
  property_value SlaPropertyValue not null,
  property_unit SlaPropertyUnit,
  element varchar[] not null,
  driver SlaDriver,
  description varchar(255) not null,
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp()
)
;