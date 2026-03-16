{% macro generate_schema_name(custom_schema_name, node) -%}
    {# 
       This macro overrides dbt's default behavior of prefixing custom schemas 
       with the target schema name. It ensures our Medallion layers 
       (RAW_DATA, STAGING_CLEANED, DATA_MARTS) are created exactly as named.
    #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
