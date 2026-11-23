select
    payment_id,
    order_id,
    {{ clean_string('payment_method') }} as payment_method,
    {{ clean_string('payment_status') }} as payment_status,
    amount as payment_amount,
    paid_at
from {{ source('raw', 'payments')}}