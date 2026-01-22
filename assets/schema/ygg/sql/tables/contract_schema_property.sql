-- create the table contract_schema_property if not exists
create table if not exists data_contracts.contract_schema_property(
  id StableId not null primary key,
  contract_schema_id StableId not null references data_contracts.contract_schema(id),
  property_name varchar(255) not null,
  physical_name StableId not null,
  physical_type StableId not null,
  description varchar not null,
  business_name varchar(255) not null,
  authoritative_definitions AuthoritativeDefinition[],
  tags Tags,
  custom_properties CustomProperty[],
  primary_key bool default false,
  primary_key_position int,
  logical_type LogicalType not null,
  is_required bool default false,
  is_unique bool default false,
  is_partitioned bool default false,
  partition_key_position int,
  classification varchar(32),
  encrypted_name StableId,
  critical_data_element bool default false,
  examples varchar[],
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp()
)
;