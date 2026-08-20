"""
Legacy analytics compatibility module.

Business logic should live in dedicated service modules.

FastAPI routes must live under:
    backend.app.routes

Order summary logic now lives in:
    backend.app.services.order_analysis

This compatibility import can be removed later once
all legacy references have been eliminated.
"""

from backend.app.services.order_analysis import (
    get_order_summary,
)


__all__ = [
    "get_order_summary",
]