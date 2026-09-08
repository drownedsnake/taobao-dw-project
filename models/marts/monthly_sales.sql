select date_trunc('month', order_date) as sales_month, category,
       count(*) as order_count, count(distinct customer) as customer_count,
       sum(quantity) as units_sold, round(sum(sales_amount), 2) as sales_amount
from {{ ref('fct_orders') }}
group by 1, 2
