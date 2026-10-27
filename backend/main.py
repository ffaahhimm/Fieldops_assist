"""
FieldOps Assist — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db import models  # noqa: F401 — import models so they register with Base
from app.db.base import Base
from app.db.seed import seed_demo_data

# ── Import all routers ────────────────────────────────────────────────────────
from app.api.routes import (
    health,
    auth,
    users,
    customers,
    sites,
    assets,
    tickets,
    technicians,
    contracts,
    maintenance,
    knowledge,
    assistant,
    reports,
    dashboard,
    audit,
)

# ── Create tables on startup ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


def create_application() -> FastAPI:
    application = FastAPI(
        title="FieldOps Assist API",
        description=(
            "IT & Security Field Service Platform with AI Troubleshooting.\n\n"
            "Portfolio demonstration — fictional data only."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    prefix = "/api"
    application.include_router(health.router, prefix=prefix, tags=["Health"])
    application.include_router(auth.router, prefix=prefix, tags=["Auth"])
    application.include_router(users.router, prefix=prefix, tags=["Users"])
    application.include_router(customers.router, prefix=prefix, tags=["Customers"])
    application.include_router(sites.router, prefix=prefix, tags=["Sites"])
    application.include_router(assets.router, prefix=prefix, tags=["Assets"])
    application.include_router(tickets.router, prefix=prefix, tags=["Tickets"])
    application.include_router(technicians.router, prefix=prefix, tags=["Technicians"])
    application.include_router(contracts.router, prefix=prefix, tags=["Contracts"])
    application.include_router(maintenance.router, prefix=prefix, tags=["Maintenance"])
    application.include_router(knowledge.router, prefix=prefix, tags=["Knowledge"])
    application.include_router(assistant.router, prefix=prefix, tags=["AI Assistant"])
    application.include_router(reports.router, prefix=prefix, tags=["Reports"])
    application.include_router(dashboard.router, prefix=prefix, tags=["Dashboard"])
    application.include_router(audit.router, prefix=prefix, tags=["Audit"])

    return application


app = create_application()


@app.on_event("startup")
async def on_startup() -> None:
    if settings.SEED_DEMO_DATA:
        seed_demo_data()
