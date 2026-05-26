"""FastAPI entrypoint for the offline-capable reconciliation MVP."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import demo, health, reconcile, report, upload


load_dotenv()

app = FastAPI(
    title="Treasury AI Reconciliation Agent",
    version="0.1.0",
    description="Explainable cross-border reconciliation with deterministic money logic.",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(demo.router)
app.include_router(reconcile.router)
app.include_router(upload.router)
app.include_router(report.router)


@app.get("/")
def root() -> dict:
    return {
        "name": "Treasury AI Reconciliation Agent",
        "status": "ready",
        "demo_endpoint": "/api/demo",
        "docs": "/docs",
    }
