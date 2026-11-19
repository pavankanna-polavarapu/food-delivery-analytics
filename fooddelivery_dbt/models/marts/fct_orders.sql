{{ config(materialized='table') }}

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
    order_status = 'delivered'      as is_delivered
from {{ ref('int_orders_enriched') }}
where is_valid_order