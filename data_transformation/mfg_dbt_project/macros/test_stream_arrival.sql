{% macro test_stream_arrival(table_name) %}

    {# Define the query to check for fresh records #}
    {% set query %}
        SELECT COUNT(*) 
        FROM MFG_BRONZE_DB.KAFKA_INGEST.{{ table_name }} 
        WHERE INGESTED_AT > CURRENT_TIMESTAMP() - INTERVAL '1 HOUR'
    {% endset %}

    {# Execute the query against Snowflake #}
    {% set results = run_query(query) %}

    {% if execute %}
        {# Extract the count value from the results #}
        {% set row_count = results.columns[0].values()[0] | int %}
        
        {{ log("STREAM HEALTH CHECK: Found " ~ row_count ~ " new records from Kafka.", info=True) }}
        
        {# INDUSTRY STANDARD: If count is 0, fail the task to alert the engineer #}
        {% if row_count == 0 %}
            {% set err_msg = "CRITICAL FAILURE: No Kafka data arrived in '" ~ table_name ~ "' in the last hour!" %}
            {{ exceptions.raise_database_error(err_msg) }}
        {% endif %}
    {% endif %}

{% endmacro %}
