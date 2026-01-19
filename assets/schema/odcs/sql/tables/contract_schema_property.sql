-- create the table contract_schema_property if not exists
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