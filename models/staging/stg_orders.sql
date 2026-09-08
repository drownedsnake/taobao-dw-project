with ranked as (
    select
        cast(order_id as varchar) as order_id,
        trim(cast(customer as varchar)) as customer,
        trim(cast(category as varchar)) as category,
        try_cast(quantity as integer) as quantity,
        round(try_cast(unit_price as double), 2) as unit_price,
        try_cast(order_date as date) as order_date,
        row_number() over (
            partition by cast(order_id as varchar)
            order by try_cast(order_date as date) desc
        ) as row_num
    from {{ source('raw', 'raw_orders') }}
)
select order_id, customer, category, quantity, unit_price,
       round(quantity * unit_price, 2) as sales_amount, order_date
from ranked
where row_num = 1 and order_id is not null and customer is not null
  and category is not null and quantity > 0 and unit_price > 0
  and order_date is not null
