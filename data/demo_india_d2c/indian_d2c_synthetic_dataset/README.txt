INDIAN D2C SYNTHETIC DATASET

All data is synthetic.

ROWS
products.csv: 250
customers.csv: 58,000
couriers.csv: 5
orders.csv: 100,000
order_items.csv: 173,969
payments.csv: 100,000
marketing.csv: 2,222
inventory.csv: 750

TIME RANGE
2025-01-10 to 2025-12-18. January and December are intentionally partial.

RELATIONSHIPS
customers.customer_id -> orders.customer_id
orders.order_id -> order_items.order_id
orders.order_id -> payments.order_id
products.sku_id -> order_items.sku_id
products.sku_id -> inventory.sku_id
couriers.courier_id -> orders.courier_id

FINANCIAL LOGIC
Gross Revenue = selling_price × quantity
Net Revenue = gross_revenue − discount
Order Value = sum(net revenue) + shipping charge

Contribution Profit can be calculated as:
Net Revenue − COGS − Forward Shipping − COD Fee − RTO Cost − Payment Fee − Allocated Marketing Spend

INTENTIONAL IMPERFECTIONS
1–4% missing values in selected fields; campaign attribution gaps; partial months; missing timestamps; high-risk COD pincodes; Diwali demand spike; delayed NDR deliveries; and several poor-margin SKUs.
