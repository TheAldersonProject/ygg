-- create the table data_contracts.contract_sla if not exists
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