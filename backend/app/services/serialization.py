import math
from datetime import date, datetime

import numpy as np
import pandas as pd


def make_json_safe(value):
    """
    Convert Pandas/NumPy values into standard Python values
    that can safely be serialized as JSON.
    """

    # None
    if value is None:
        return None

    # Dictionaries
    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    # Lists / tuples
    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    # NumPy arrays
    if isinstance(value, np.ndarray):
        return [
            make_json_safe(item)
            for item in value.tolist()
        ]

    # NumPy integers
    if isinstance(value, np.integer):
        return int(value)

    # NumPy floating-point values
    if isinstance(value, np.floating):
        number = float(value)

        if not math.isfinite(number):
            return None

        return number

    # NumPy booleans
    if isinstance(value, np.bool_):
        return bool(value)

    # Python floats
    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    # Dates / timestamps
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()

    # Pandas missing values
    if pd.isna(value):
        return None

    return value