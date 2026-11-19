select 
    customer_id,
    customer_name,
    lower(trim(email))  as email,
    phone,
    city,
    signup_date,
    updated_at
from {{ source('raw', 'customers')}}