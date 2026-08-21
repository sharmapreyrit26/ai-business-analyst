import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.analytics import (
    router as analytics_router,
)
from backend.app.routes.dashboard import (
    router as dashboard_router,
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
        "http://localhost:5173",
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


app.include_router(
    analytics_router
)

app.include_router(
    dashboard_router
)