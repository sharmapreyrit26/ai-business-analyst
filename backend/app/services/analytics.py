from backend.app.services.data_loader import load_orders

def get_order_summary():
        df = load_orders()


        total_orders = len(df)

        delivered_orders = (
            df["order_status"] == "delivered"
        ).sum()

        cancelled_orders = (
            df["order_status"] == "canceled"
        ).sum()

        delivery_rate = (
            delivered_orders / total_orders * 100
            if total_orders
            else 0
        )

        cancellation_rate = (
            cancelled_orders / total_orders * 100
            if total_orders
            else 0
        )

        return {
            "total_orders": int(total_orders),
            "delivered_orders": int(delivered_orders),
            "cancelled_orders": int(cancelled_orders),
            "delivery_rate_percent": round(
                delivery_rate,
                2
            ),
            "cancellation_rate_percent": round(
                cancellation_rate,
                2
            )
        }

