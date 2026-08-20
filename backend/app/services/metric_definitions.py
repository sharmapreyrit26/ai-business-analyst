METRIC_DEFINITIONS = {

    "revenue": {
        "name": "Revenue",
        "formula": "sum(price)",
        "required_fields": [
            "order_id",
            "order_status",
            "price"
        ],
        "source": "olist_order_items_dataset.csv",
        "unit": "currency",
        "aggregation": "sum",
        "period": "monthly",
        "dependencies": [],
        "status": "actual"
    },

    "orders": {
        "name": "Orders",
        "formula": "count(unique(order_id))",
        "required_fields": [
            "order_id"
        ],
        "source": "olist_orders_dataset.csv",
        "unit": "count",
        "aggregation": "count_distinct",
        "period": "monthly",
        "dependencies": [],
        "status": "actual"
    },

    "aov": {
        "name": "Average Order Value",
        "formula": "revenue / orders",
        "required_fields": [
            "revenue",
            "orders"
        ],
        "source": "derived",
        "unit": "currency_per_order",
        "aggregation": "derived",
        "period": "monthly",
        "dependencies": [
            "revenue",
            "orders"
        ],
        "status": "derived"
    },

    "delivery_rate": {
        "name": "Delivery Rate",
        "formula": "delivered_orders / total_orders * 100",
        "required_fields": [
            "order_id",
            "order_status"
        ],
        "source": "olist_orders_dataset.csv",
        "unit": "percent",
        "aggregation": "ratio",
        "period": "monthly",
        "dependencies": [
            "orders"
        ],
        "status": "actual"
    },

    "cancellation_rate": {
        "name": "Cancellation Rate",
        "formula": "cancelled_orders / total_orders * 100",
        "required_fields": [
            "order_id",
            "order_status"
        ],
        "source": "olist_orders_dataset.csv",
        "unit": "percent",
        "aggregation": "ratio",
        "period": "monthly",
        "dependencies": [
            "orders"
        ],
        "status": "actual"
    },

    "freight_value": {
        "name": "Freight Value",
        "formula": "sum(freight_value)",
        "required_fields": [
            "order_id",
            "freight_value"
        ],
        "source": "olist_order_items_dataset.csv",
        "unit": "currency",
        "aggregation": "sum",
        "period": "monthly",
        "dependencies": [],
        "status": "actual"
    },

    "items": {
        "name": "Items",
        "formula": "sum(order_item_id)",
        "required_fields": [
            "order_id",
            "order_item_id"
        ],
        "source": "olist_order_items_dataset.csv",
        "unit": "count",
        "aggregation": "sum",
        "period": "monthly",
        "dependencies": [],
        "status": "actual"
    },

}