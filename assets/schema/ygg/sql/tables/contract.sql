-- creates the contract table if not exists
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