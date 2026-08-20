from fastapi import FastAPI

from backend.app.routes.analytics import (
    router as analytics_router,
)

from backend.app.routes.dashboard import (
    router as dashboard_router,
)


app = FastAPI(
    title="ProfitLens",
    description="AI-powered D2C business analytics system",
    version="0.1.0",
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