{% macro generate_schema_name(custom_schema_name, node) -%}
    {# 
       This macro overrides dbt's default behavior.
       We add a check for 'target.schema' to ensure the IDE can resolve the path.
    #}
    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}

{%- endmacro %}
