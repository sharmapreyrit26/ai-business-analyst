import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.d2c import (
    router as d2c_router,
)

from backend.app.routes.intelligence import (
    router as intelligence_router,
)

from backend.app.routes.internal import (
    router as internal_router,
)


app = FastAPI(
    title="ProfitLens",
    description=(
        "Deterministic-first AI business analytics "
        "for D2C brands."
    ),
    version="0.1.0",
)


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    )

    return [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "ProfitLens API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# PRODUCTION D2C API
# ============================================================

app.include_router(
    d2c_router
)

app.include_router(
    intelligence_router
)


# ============================================================
# INTERNAL / DEVELOPMENT API
# ============================================================

app.include_router(
    internal_router
)

