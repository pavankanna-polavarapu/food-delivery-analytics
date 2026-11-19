with orders as (

    select * from {{ ref('stg_orders') }}

),

customers as (

    select customer_id, city as customer_city
    from {{ ref('stg_customers') }}

),

restaurants as (

    select restaurant_id, restaurant_name, cuisine, city as restaurant_city
    from {{ ref('stg_restaurants') }}

),

payments as (

    select order_id, payment_method, payment_status
    from {{ ref('stg_payments') }}

),

deliveries as (

    select
        order_id,
        delivery_id,
        partner_id,
        pickup_ts,
        delivered_ts,
        delivery_minutes,
        promised_minutes,
        distance_km,
        has_invalid_timestamps
    from {{ ref('stg_deliveries') }}

),

joined as (

    select
        o.order_id,
        o.order_ts,
        o.order_status,
        o.subtotal_amount,
        o.discount_amount,
        o.delivery_fee_amount,
        o.tax_amount,
        o.total_amount,
        o.promo_code,

        o.customer_id,
        c.customer_city,

        o.restaurant_id,
        r.restaurant_name,
        r.cuisine,
        r.restaurant_city,

        p.payment_method,
        p.payment_status,

        d.delivery_id,
        d.partner_id,
        d.pickup_ts,
        d.delivered_ts,
        d.delivery_minutes,
        d.promised_minutes,
        d.distance_km,

        d.delivery_minutes > d.promised_minutes     as is_late_delivery,

        -- the one place where we decide what counts as bad data
        (
            not o.has_invalid_subtotal
            and not coalesce(d.has_invalid_timestamps, false)
        )                                           as is_valid_order

    from orders as o
    left join customers   as c on o.customer_id   = c.customer_id
    left join restaurants as r on o.restaurant_id = r.restaurant_id
    left join payments    as p on o.order_id      = p.order_id
    left join deliveries  as d on o.order_id      = d.order_id

)

select * from joined