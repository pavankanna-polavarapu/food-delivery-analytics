select
    payment_id,
    order_id,
    lower(payment_method) as payment_method,
    lower(payment_status) as payment_status,
    amount as payment_amount,
    paid_at
from {{ source('raw', 'payments')}}