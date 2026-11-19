with customers as (

    select * from {{ ref('stg_customers') }}

),

order_stats as (

    select
        customer_id,
        min(order_ts)       as first_order_ts,
        max(order_ts)       as last_order_ts,
        count(*)            as total_delivered_orders,
        sum(total_amount)   as lifetime_value
    from {{ ref('int_orders_enriched') }}
    where is_valid_order
      and order_status = 'delivered'
    group by 1

)

select
    c.customer_id,
    c.customer_name,
    c.email,
    c.phone,
    c.city,
    c.signup_date,
    s.first_order_ts,
    s.last_order_ts,
    coalesce(s.total_delivered_orders, 0)   as total_delivered_orders,
    coalesce(s.lifetime_value, 0)           as lifetime_value
from customers as c
left join order_stats as s on c.customer_id = s.customer_id