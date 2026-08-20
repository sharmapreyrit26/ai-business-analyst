from copy import deepcopy


DEFAULT_BUSINESS_MEMORY = {
    "business_profile": {
        "business_name": None,
        "business_category": None,
        "primary_markets": [],
        "currency": "INR",
    },

    "targets": {
        "revenue_growth_percent": None,
        "aov": None,
        "delivery_rate_percent": None,
        "cancellation_rate_percent": None,

        # Future metrics
        "gross_margin_percent": None,
        "contribution_margin_percent": None,
        "rto_rate_percent": None,
        "cac": None,
        "roas": None,
        "ltv": None,
    },

    "business_model": {
        "cod_percentage": None,
        "prepaid_percentage": None,
        "typical_seasonality": [],
    },

    "constraints": {
        "minimum_margin_percent": None,
        "maximum_rto_percent": None,
        "maximum_cac": None,
        "minimum_roas": None,
    },
}


# --------------------------------------------------
# V1 IN-MEMORY STORE
#
# Later this will move to PostgreSQL.
# --------------------------------------------------

_business_memory_store = deepcopy(
    DEFAULT_BUSINESS_MEMORY
)


def get_business_memory():
    """
    Return the currently stored business context.
    """

    return deepcopy(
        _business_memory_store
    )


def update_business_profile(
    business_name=None,
    business_category=None,
    primary_markets=None,
    currency=None,
):
    """
    Update basic business profile information.
    """

    profile = _business_memory_store[
        "business_profile"
    ]

    if business_name is not None:
        profile["business_name"] = (
            business_name
        )

    if business_category is not None:
        profile["business_category"] = (
            business_category
        )

    if primary_markets is not None:
        profile["primary_markets"] = (
            list(primary_markets)
        )

    if currency is not None:
        profile["currency"] = currency

    return get_business_memory()


def update_target(
    metric: str,
    value
):
    """
    Update a target metric.

    Only supported targets can be updated.
    """

    targets = _business_memory_store[
        "targets"
    ]

    if metric not in targets:
        raise ValueError(
            f"Unsupported target metric: {metric}"
        )

    targets[metric] = value

    return {
        "metric": metric,
        "target": value,
    }


def update_constraint(
    constraint: str,
    value
):
    """
    Update a business constraint.
    """

    constraints = _business_memory_store[
        "constraints"
    ]

    if constraint not in constraints:
        raise ValueError(
            f"Unsupported business constraint: "
            f"{constraint}"
        )

    constraints[constraint] = value

    return {
        "constraint": constraint,
        "value": value,
    }


def update_business_model(
    cod_percentage=None,
    prepaid_percentage=None,
    typical_seasonality=None,
):
    """
    Update business-model information.
    """

    business_model = _business_memory_store[
        "business_model"
    ]

    if cod_percentage is not None:
        business_model[
            "cod_percentage"
        ] = cod_percentage

    if prepaid_percentage is not None:
        business_model[
            "prepaid_percentage"
        ] = prepaid_percentage

    if typical_seasonality is not None:
        business_model[
            "typical_seasonality"
        ] = list(
            typical_seasonality
        )

    return get_business_memory()


def reset_business_memory():
    """
    Reset memory back to the default V1 structure.

    Mainly useful for testing.
    """

    global _business_memory_store

    _business_memory_store = deepcopy(
        DEFAULT_BUSINESS_MEMORY
    )

    return get_business_memory()