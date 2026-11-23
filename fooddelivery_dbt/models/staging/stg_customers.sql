select 
    customer_id,
    customer_name,
    {{ clean_string('email') }} as email,
    phone,
    city,
    signup_date,
    updated_at
from {{ source('raw', 'customers')}}