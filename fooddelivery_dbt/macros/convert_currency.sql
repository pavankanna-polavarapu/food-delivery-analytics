{% macro convert_currency(column_name, rate_var = 'inr_to_usd', precision=2) %}
    round({{ column_name }} * {{ var(rate_var) }}, {{ precision }})
{% endmacro %}