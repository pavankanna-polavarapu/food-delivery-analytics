{{ 
    config(materialized='incremental',
           unique_key='order_id',
           incremental_strategy='merge',
           on_schema_change='append_new_columns'
        ) 
}}

-- Grain: one row per valid order

select
    order_id,
    customer_id,
    restaurant_id,
    cast(order_ts as date)          as order_date,
    order_ts,
    order_status,
    payment_method,
    payment_status,
    promo_code,
    promo_code is not null          as has_promo,
    subtotal_amount,
    discount_amount,
    delivery_fee_amount,
    tax_amount,
    total_amount,
    order_status = 'delivered'      as is_delivered, 
    updated_at
from {{ ref('int_orders_enriched') }}
where is_valid_order

{% if is_incremental() %}

  and updated_at > (select dateadd('hour', -3, max(t.updated_at)) from {{ this }} as t)

{% endif %}