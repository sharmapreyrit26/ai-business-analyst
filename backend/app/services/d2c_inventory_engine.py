from functools import lru_cache

import pandas as pd

from backend.app.services.d2c_data_loader import (
    load_inventory,
    load_products,
)


# ============================================================
# INVENTORY BASE
# ============================================================


@lru_cache(maxsize=1)
def _get_inventory_base_cached():
    """
    Build canonical SKU x warehouse inventory dataset.

    inventory.csv is treated as a current/snapshot inventory
    table, not as a historical monthly inventory table.
    """

    inventory = (
        load_inventory()
        .copy()
    )

    products = (
        load_products()
        .copy()
    )

    required_inventory_columns = {
        "sku_id",
        "warehouse",
        "opening_stock",
        "closing_stock",
        "units_sold",
        "units_received",
        "reorder_point",
    }

    missing_inventory = (
        required_inventory_columns
        - set(
            inventory.columns
        )
    )

    if missing_inventory:
        raise ValueError(
            "Missing required inventory columns: "
            + ", ".join(
                sorted(
                    missing_inventory
                )
            )
        )

    required_product_columns = {
        "sku_id",
        "product_name",
        "category",
        "list_price",
        "cogs_per_unit",
    }

    missing_products = (
        required_product_columns
        - set(
            products.columns
        )
    )

    if missing_products:
        raise ValueError(
            "Missing required product columns: "
            + ", ".join(
                sorted(
                    missing_products
                )
            )
        )

    base = (
        inventory.merge(
            products[
                [
                    "sku_id",
                    "product_name",
                    "category",
                    "list_price",
                    "cogs_per_unit",
                ]
            ],
            on="sku_id",
            how="left",
            validate="many_to_one",
        )
    )

    numeric_columns = [
        "opening_stock",
        "closing_stock",
        "units_sold",
        "units_received",
        "reorder_point",
        "list_price",
        "cogs_per_unit",
    ]

    for column in numeric_columns:
        base[column] = (
            pd.to_numeric(
                base[column],
                errors="coerce",
            )
            .fillna(0.0)
        )

    # ========================================================
    # STOCK ECONOMICS
    # ========================================================

    base[
        "inventory_cost_value"
    ] = (
        base[
            "closing_stock"
        ]
        * base[
            "cogs_per_unit"
        ]
    )

    base[
        "inventory_retail_value"
    ] = (
        base[
            "closing_stock"
        ]
        * base[
            "list_price"
        ]
    )

    # ========================================================
    # STOCK COVERAGE
    # ========================================================

    # The dataset has no explicit inventory-period duration.
    # Therefore this is a ratio, not "days of cover".
    base[
        "stock_to_sales_ratio"
    ] = (
        base[
            "closing_stock"
        ]
        .div(
            base[
                "units_sold"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    base[
        "reorder_gap_units"
    ] = (
        base[
            "reorder_point"
        ]
        - base[
            "closing_stock"
        ]
    ).clip(
        lower=0
    )

    base[
        "stock_above_reorder_units"
    ] = (
        base[
            "closing_stock"
        ]
        - base[
            "reorder_point"
        ]
    ).clip(
        lower=0
    )

    # ========================================================
    # INVENTORY HEALTH FLAGS
    # ========================================================

    base[
        "is_out_of_stock"
    ] = (
        base[
            "closing_stock"
        ]
        <= 0
    )

    base[
        "is_below_reorder_point"
    ] = (
        base[
            "closing_stock"
        ]
        <= base[
            "reorder_point"
        ]
    )

    # Low stock:
    # between reorder point and 1.5x reorder point.
    base[
        "is_low_stock"
    ] = (
        (
            base[
                "closing_stock"
            ]
            > base[
                "reorder_point"
            ]
        )
        & (
            base[
                "closing_stock"
            ]
            <= (
                base[
                    "reorder_point"
                ]
                * 1.5
            )
        )
    )

    # Overstock signal:
    # stock exceeds 2.5x the inventory-period units sold.
    base[
        "is_overstock"
    ] = (
        base[
            "units_sold"
        ]
        > 0
    ) & (
        base[
            "closing_stock"
        ]
        > (
            base[
                "units_sold"
            ]
            * 2.5
        )
    )

    # Slow moving:
    # closing stock is at least 2x units sold.
    base[
        "is_slow_moving"
    ] = (
        base[
            "units_sold"
        ]
        > 0
    ) & (
        base[
            "closing_stock"
        ]
        >= (
            base[
                "units_sold"
            ]
            * 2.0
        )
    )

    # ========================================================
    # ESTIMATED VALUE AT RISK / TRAPPED CAPITAL
    # ========================================================

    base[
        "reorder_gap_cost_value"
    ] = (
        base[
            "reorder_gap_units"
        ]
        * base[
            "cogs_per_unit"
        ]
    )

    base[
        "potential_revenue_at_risk"
    ] = (
        base[
            "reorder_gap_units"
        ]
        * base[
            "list_price"
        ]
    )

    base[
        "estimated_excess_stock_units"
    ] = (
        base[
            "closing_stock"
        ]
        - (
            base[
                "units_sold"
            ]
            * 2.5
        )
    ).clip(
        lower=0
    )

    base[
        "estimated_trapped_inventory_cost"
    ] = (
        base[
            "estimated_excess_stock_units"
        ]
        * base[
            "cogs_per_unit"
        ]
    )

    numeric_output_columns = [
        "inventory_cost_value",
        "inventory_retail_value",
        "stock_to_sales_ratio",
        "reorder_gap_units",
        "stock_above_reorder_units",
        "reorder_gap_cost_value",
        "potential_revenue_at_risk",
        "estimated_excess_stock_units",
        "estimated_trapped_inventory_cost",
    ]

    base[
        numeric_output_columns
    ] = (
        base[
            numeric_output_columns
        ]
        .round(2)
    )

    return base


def get_inventory_base():
    """
    Return a safe copy of the current inventory snapshot.
    """

    return (
        _get_inventory_base_cached()
        .copy()
    )


# ============================================================
# INVENTORY SUMMARY
# ============================================================


def get_inventory_summary():
    """
    Return headline inventory-health metrics.
    """

    df = (
        get_inventory_base()
    )

    total_rows = int(
        len(df)
    )

    total_skus = int(
        df[
            "sku_id"
        ]
        .nunique()
    )

    total_stock_units = int(
        df[
            "closing_stock"
        ]
        .sum()
    )

    inventory_cost_value = float(
        df[
            "inventory_cost_value"
        ]
        .sum()
    )

    inventory_retail_value = float(
        df[
            "inventory_retail_value"
        ]
        .sum()
    )

    below_reorder = int(
        df[
            "is_below_reorder_point"
        ]
        .sum()
    )

    low_stock = int(
        df[
            "is_low_stock"
        ]
        .sum()
    )

    out_of_stock = int(
        df[
            "is_out_of_stock"
        ]
        .sum()
    )

    overstock = int(
        df[
            "is_overstock"
        ]
        .sum()
    )

    slow_moving = int(
        df[
            "is_slow_moving"
        ]
        .sum()
    )

    potential_revenue_at_risk = float(
        df[
            "potential_revenue_at_risk"
        ]
        .sum()
    )

    trapped_inventory_cost = float(
        df[
            "estimated_trapped_inventory_cost"
        ]
        .sum()
    )

    return {
        "inventory_scope": (
            "current_snapshot"
        ),

        "historical_inventory_available": (
            False
        ),

        "sku_warehouse_rows": (
            total_rows
        ),

        "total_skus": (
            total_skus
        ),

        "warehouses": int(
            df[
                "warehouse"
            ]
            .nunique()
        ),

        "total_closing_stock_units": (
            total_stock_units
        ),

        "inventory_cost_value": round(
            inventory_cost_value,
            2,
        ),

        "inventory_retail_value": round(
            inventory_retail_value,
            2,
        ),

        "below_reorder_rows": (
            below_reorder
        ),

        "low_stock_rows": (
            low_stock
        ),

        "out_of_stock_rows": (
            out_of_stock
        ),

        "overstock_rows": (
            overstock
        ),

        "slow_moving_rows": (
            slow_moving
        ),

        "potential_revenue_at_risk": round(
            potential_revenue_at_risk,
            2,
        ),

        "estimated_trapped_inventory_cost": round(
            trapped_inventory_cost,
            2,
        ),

        "stock_coverage_unit": (
            "stock_to_period_sales_ratio"
        ),
    }


# ============================================================
# SKU INVENTORY PERFORMANCE
# ============================================================


def get_sku_inventory_performance():
    """
    Aggregate current inventory health across warehouses
    at SKU level.
    """

    df = (
        get_inventory_base()
    )

    sku = (
        df.groupby(
            "sku_id",
            dropna=False,
        )
        .agg(
            product_name=(
                "product_name",
                "first",
            ),
            category=(
                "category",
                "first",
            ),
            warehouses=(
                "warehouse",
                "nunique",
            ),
            opening_stock=(
                "opening_stock",
                "sum",
            ),
            closing_stock=(
                "closing_stock",
                "sum",
            ),
            units_sold=(
                "units_sold",
                "sum",
            ),
            units_received=(
                "units_received",
                "sum",
            ),
            reorder_point=(
                "reorder_point",
                "sum",
            ),
            inventory_cost_value=(
                "inventory_cost_value",
                "sum",
            ),
            inventory_retail_value=(
                "inventory_retail_value",
                "sum",
            ),
            potential_revenue_at_risk=(
                "potential_revenue_at_risk",
                "sum",
            ),
            estimated_trapped_inventory_cost=(
                "estimated_trapped_inventory_cost",
                "sum",
            ),
            below_reorder_locations=(
                "is_below_reorder_point",
                "sum",
            ),
            low_stock_locations=(
                "is_low_stock",
                "sum",
            ),
            overstock_locations=(
                "is_overstock",
                "sum",
            ),
            slow_moving_locations=(
                "is_slow_moving",
                "sum",
            ),
        )
        .reset_index()
    )

    sku[
        "stock_to_sales_ratio"
    ] = (
        sku[
            "closing_stock"
        ]
        .div(
            sku[
                "units_sold"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    sku[
        "is_reorder_candidate"
    ] = (
        sku[
            "below_reorder_locations"
        ]
        > 0
)

    numeric_columns = [
        "inventory_cost_value",
        "inventory_retail_value",
        "potential_revenue_at_risk",
        "estimated_trapped_inventory_cost",
        "stock_to_sales_ratio",
    ]

    sku[
        numeric_columns
    ] = (
        sku[
            numeric_columns
        ]
        .round(2)
    )

    return (
        sku.sort_values(
            [
                "is_reorder_candidate",
                "potential_revenue_at_risk",
                "closing_stock",
            ],
            ascending=[
                False,
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# WAREHOUSE PERFORMANCE
# ============================================================


def get_warehouse_inventory_performance():
    """
    Return inventory health by warehouse.
    """

    df = (
        get_inventory_base()
    )

    warehouse = (
        df.groupby(
            "warehouse",
            dropna=False,
        )
        .agg(
            skus=(
                "sku_id",
                "nunique",
            ),
            closing_stock=(
                "closing_stock",
                "sum",
            ),
            units_sold=(
                "units_sold",
                "sum",
            ),
            units_received=(
                "units_received",
                "sum",
            ),
            inventory_cost_value=(
                "inventory_cost_value",
                "sum",
            ),
            inventory_retail_value=(
                "inventory_retail_value",
                "sum",
            ),
            below_reorder_rows=(
                "is_below_reorder_point",
                "sum",
            ),
            low_stock_rows=(
                "is_low_stock",
                "sum",
            ),
            overstock_rows=(
                "is_overstock",
                "sum",
            ),
            slow_moving_rows=(
                "is_slow_moving",
                "sum",
            ),
            potential_revenue_at_risk=(
                "potential_revenue_at_risk",
                "sum",
            ),
            estimated_trapped_inventory_cost=(
                "estimated_trapped_inventory_cost",
                "sum",
            ),
        )
        .reset_index()
    )

    warehouse[
        "stock_to_sales_ratio"
    ] = (
        warehouse[
            "closing_stock"
        ]
        .div(
            warehouse[
                "units_sold"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    numeric_columns = [
        "inventory_cost_value",
        "inventory_retail_value",
        "potential_revenue_at_risk",
        "estimated_trapped_inventory_cost",
        "stock_to_sales_ratio",
    ]

    warehouse[
        numeric_columns
    ] = (
        warehouse[
            numeric_columns
        ]
        .round(2)
    )

    return (
        warehouse.sort_values(
            "inventory_cost_value",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# CATEGORY INVENTORY PERFORMANCE
# ============================================================


def get_category_inventory_performance():
    """
    Return current inventory health by product category.
    """

    df = (
        get_inventory_base()
    )

    category = (
        df.groupby(
            "category",
            dropna=False,
        )
        .agg(
            skus=(
                "sku_id",
                "nunique",
            ),
            closing_stock=(
                "closing_stock",
                "sum",
            ),
            units_sold=(
                "units_sold",
                "sum",
            ),
            inventory_cost_value=(
                "inventory_cost_value",
                "sum",
            ),
            inventory_retail_value=(
                "inventory_retail_value",
                "sum",
            ),
            below_reorder_rows=(
                "is_below_reorder_point",
                "sum",
            ),
            overstock_rows=(
                "is_overstock",
                "sum",
            ),
            potential_revenue_at_risk=(
                "potential_revenue_at_risk",
                "sum",
            ),
            estimated_trapped_inventory_cost=(
                "estimated_trapped_inventory_cost",
                "sum",
            ),
        )
        .reset_index()
    )

    category[
        "stock_to_sales_ratio"
    ] = (
        category[
            "closing_stock"
        ]
        .div(
            category[
                "units_sold"
            ]
            .replace(
                0,
                pd.NA,
            )
        )
        .fillna(0.0)
    )

    numeric_columns = [
        "inventory_cost_value",
        "inventory_retail_value",
        "potential_revenue_at_risk",
        "estimated_trapped_inventory_cost",
        "stock_to_sales_ratio",
    ]

    category[
        numeric_columns
    ] = (
        category[
            numeric_columns
        ]
        .round(2)
    )

    return (
        category.sort_values(
            "inventory_cost_value",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )