import logging
import os
from fastapi import FastAPI
from app.routes import health, system

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SysInfo API",
    description="A simple System Information API — intern Linux deployment exercise.",
    version="1.0.0",
)

# Register routes
app.include_router(health.router)
app.include_router(system.router)


@app.on_event("startup")
async def on_startup():
    logger.info("SysInfo API started successfully.")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("SysInfo API shutting down.")
