{% macro load_internal_stage(stage_name, table_name) %}
    {% set sql %}
        COPY INTO MFG_BRONZE_DB.RAW_DATA.{{ table_name }}
        FROM @MFG_BRONZE_DB.EXTERNAL_STAGES.{{ stage_name }}
        FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
        ON_ERROR = 'CONTINUE'
        PURGE = TRUE;
    {% endset %}
    
    {% do run_query(sql) %}
    {{ log("Successfully loaded " ~ table_name ~ " from " ~ stage_name, info=True) }}
{% endmacro %}
