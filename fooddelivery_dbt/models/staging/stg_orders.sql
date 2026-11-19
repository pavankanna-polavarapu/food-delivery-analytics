with source as(
    select * from {{ source('raw', 'orders')}}
),

deduplicated as (
    select *
    from source
    qualify row_number()over(
        partition by order_id
        order by updated_at desc
    ) = 1
),

renamed as (
    select 
        order_id,
        customer_id,
        restaurant_id,
        order_ts,
        lower(trim(order_status))  as order_status,
        subtotal                   as subtotal_amount,
        discount                   as discount_amount,
        tax                        as tax_amount,
        delivery_fee                as delivery_fee_amount,
        total_amount,
        upper(promo_code)           as promo_code,
        updated_at,
        subtotal < 0    as has_invalid_subtotal
    from deduplicated
)

select * from renamed