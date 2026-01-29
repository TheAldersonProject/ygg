# Catalog Schema
CREATE_CATALOG_SCHEMA_IF_NOT_EXISTS: str = "CREATE SCHEMA IF NOT EXISTS {catalog_schema};"
CREATE_CATALOG_SCHEMA_OR_REPLACE: str = "CREATE OR REPLACE SCHEMA {catalog_schema};"

# Table
CREATE_TABLE_IF_NOT_EXISTS_HEADER: str = "CREATE TABLE IF NOT EXISTS {catalog_schema}.{table_name}"
CREATE_TABLE_OR_REPLACE_HEADER: str = "CREATE OR REPLACE TABLE {catalog_schema}.{table_name}"

# Table Columns
DDL_COLUMN_TEMPLATE: str = "{field_name} {field_type}{nullable}{field_pk_uc}{default_value}{field_check_constraint}"
DDL_CREATE_TABLE_STATEMENT_TEMPLATE: str = """\
{create_table_header}   (
{fields_ddl_block}
) ;\
"""
