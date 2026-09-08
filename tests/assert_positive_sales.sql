select * from {{ ref('fct_orders') }} where sales_amount <= 0
