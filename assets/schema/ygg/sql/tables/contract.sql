-- creates the contract table if not exists
create table if not exists data_contracts.contract(
  id StableId not null unique,
  kind Kind not null,
  api_version ApiVersion not null,
  contract_name StableId not null,
  tenant StableId not null,
  contract_domain StableId not null,
  contract_version varchar(24) not null unique,
  status Status not null,
  tags Tags,
  data_product varchar(255),
  authoritative_definitions AuthoritativeDefinition[],
  description StructuredDescription,
  ygg_flow_type YggFlowType not null,
  version_ts timestamp,
  record_create_ts timestamp default get_current_timestamp(),
  record_update_ts timestamp default get_current_timestamp(),
  primary key ( id, contract_version )
)
;