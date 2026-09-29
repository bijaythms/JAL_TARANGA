"""
Jal Taranga — Kerala Watershed & Disaster Intelligence Platform
FastAPI Python Backend & Advanced Geospatial Command Core
Data Source: Grounded in KSDMA, GSI, and NCESS Hydrological Baselines.
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path so 'app' package is always resolvable
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import ensure_schema_upgrades
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.geospatial import router as geospatial_router
from app.api.reports import router as reports_router
from app.api.srishti import router as srishti_router
from app.api.notifications import router as notifications_router
from app.api.ksdma import router as ksdma_router
from app.api.inundation import router as inundation_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
def on_startup():
    import threading
    def _bg_migration():
        try:
            ensure_schema_upgrades()
        except Exception:
            pass
    threading.Thread(target=_bg_migration, daemon=True).start()

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def disable_browser_cache(request, call_next):
    """Keep local development pages and assets in sync with source changes."""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Include API Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(geospatial_router)
app.include_router(reports_router)
app.include_router(srishti_router)
app.include_router(notifications_router)
app.include_router(ksdma_router)
app.include_router(inundation_router)

# Mount Frontend Static Assets
frontend_path = settings.FRONTEND_DIR
if frontend_path.exists():
    css_dir = frontend_path / "css"
    js_dir = frontend_path / "js"
    images_dir = frontend_path / "images"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    if images_dir.exists():
        app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")
    data_dir = frontend_path / "data"
    if data_dir.exists():
        app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    icon_path = frontend_path / "images" / "favicon.png"
    if not icon_path.exists():
        icon_path = frontend_path / "favicon.ico"
    return FileResponse(str(icon_path), media_type="image/png")


@app.get("/health", tags=["Health & Status"])
def health_check():
    """System health check endpoint for monitoring and container orchestration."""
    from app.core.database import get_database_status
    return {
        "status": "healthy",
        "service": "Jal Taranga Geospatial Engine",
        "version": settings.VERSION,
        "database": get_database_status(),
    }


@app.get("/", response_class=HTMLResponse, tags=["Portal"])
def serve_portal():
    """Serves the interactive Leaflet GIS single-page application."""
    index_file = settings.FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        content="<h2>Jal Taranga GIS Engine running. Frontend index.html not found.</h2>",
        status_code=200,
    )


if __name__ == "__main__":
    print("\n==================================================================")
    print("  Jal Taranga — Kerala Geospatial Earth Observation Core")
    print("  Developed by VISIONQUEST")
    print("  Interactive Map Search & Place Finder: ONLINE")
    display_host = "localhost" if settings.HOST in ["0.0.0.0", "127.0.0.1"] else settings.HOST
    print(f"  Open in Browser:     http://{display_host}:{settings.PORT}")
    print(f"  Alternative Link:    http://127.0.0.1:{settings.PORT}")
    print(f"  API Documentation:   http://{display_host}:{settings.PORT}/docs")
    print("==================================================================\n")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True, app_dir=str(backend_dir))
