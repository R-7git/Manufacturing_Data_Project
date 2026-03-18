{% macro load_internal_stage(stage_name, table_name) %}
    {% set sql %}
        COPY INTO STG_DB.STG_SCHEMA.{{ table_name }}
        FROM @STG_DB.STG_SCHEMA.{{ stage_name }}
        FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1);
    {% endset %}
    
    {% do run_query(sql) %}
    {% do log("Successfully loaded data from " ~ stage_name ~ " to " ~ table_name, info=True) %}
{% endmacro %}
