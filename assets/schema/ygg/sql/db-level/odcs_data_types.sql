-- odcs data contract kind
CREATE TYPE IF NOT EXISTS Kind AS ENUM('DataContract');

-- odcs status allowed
CREATE TYPE IF NOT EXISTS Status AS ENUM('draft', 'active', 'deprecated');

-- odcs api versions allowed
CREATE TYPE IF NOT EXISTS ApiVersion AS ENUM('v3.1.0');

-- odcs sla property
CREATE TYPE IF NOT EXISTS SlaProperty AS ENUM('availability', 'latency', 'retention', 'throughput');

-- odcs sla property value
CREATE TYPE IF NOT EXISTS SlaPropertyValue AS UNION(str varchar, num integer, flt float, bln boolean) ;

-- odcs sla property unit
CREATE TYPE IF NOT EXISTS SlaPropertyUnit AS ENUM('y', 'm', 'd', 'h', 'mn', 's', 'ms', 'ns' );

-- odcs sla driver
CREATE TYPE IF NOT EXISTS SlaDriver AS ENUM('operational', 'regulatory', 'analytics');

-- odcs logical type
CREATE TYPE IF NOT EXISTS LogicalType AS ENUM('string', 'integer', 'decimal', 'boolean', 'date', 'timestamp', 'timestamp_ntz', 'timestamp_ltz', 'uuid', 'uuid4', 'json', 'array', 'object', 'float');

-- odcs authoritative definition
CREATE TYPE IF NOT EXISTS AuthoritativeDefinition AS STRUCT(id VARCHAR, url VARCHAR, type VARCHAR, description VARCHAR);

-- odcs custom properties
CREATE TYPE IF NOT EXISTS CustomProperty AS STRUCT(id VARCHAR, property VARCHAR, value VARCHAR, description VARCHAR);

-- odcs stable id
CREATE TYPE  IF NOT EXISTS StableId AS VARCHAR(256);

-- odcs tags
CREATE TYPE IF NOT EXISTS Tags AS VARCHAR[];

-- odcs structured description
CREATE TYPE IF NOT EXISTS StructuredDescription AS STRUCT(purpose VARCHAR, limitations VARCHAR, usage VARCHAR, authoritative_definitions AuthoritativeDefinition[], custom_properties CustomProperty[]);

-- odcs
CREATE TYPE IF NOT EXISTS SchemaPhysicalType AS ENUM('view', 'table');

-- odcs server type
CREATE TYPE IF NOT EXISTS ServerType AS ENUM('snowflake', 'duckdb', 'postgresql');

-- odcs server environment
CREATE TYPE IF NOT EXISTS Environment AS ENUM('production', 'staging', 'development', 'testing', 'qa', 'local', 'general');
