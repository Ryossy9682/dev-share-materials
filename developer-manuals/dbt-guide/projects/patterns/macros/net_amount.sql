{% macro net_amount(amount_column, discount_column) -%}
round(cast({{ amount_column }} as numeric) * (1 - cast({{ discount_column }} as numeric)), 2)
{%- endmacro %}
