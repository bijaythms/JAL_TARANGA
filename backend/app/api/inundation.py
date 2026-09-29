"""
Jal Taranga - Inundation Simulator 2.0 API Router
=================================================
Integrates the physics-based FastFlood hydrodynamic steady-state inundation engine
(van den Bout et al., 2026) with Copernicus GLO-30 30m real DEMs and India calibration.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import matplotlib
matplotlib.use("Agg")

# Ensure PROJ_DATA fix before rasterio
try:
    import rasterio
    rasterio_dir = Path(rasterio.__file__).parent
    proj_db = rasterio_dir / "proj_data" / "proj.db"
    if proj_db.exists():
        os.environ["PROJ_DATA"] = str(proj_db.parent)
        os.environ["PROJ_LIB"] = str(proj_db.parent)
except Exception:
    pass

import numpy as np
if not hasattr(np, "in1d"):
    np.in1d = np.isin

# Add Inundation Engine directory to sys.path
ENGINE_ROOT = Path(r"D:\New Inundation Model\New Inundation Model")
if ENGINE_ROOT.exists() and str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field
import requests

from main import IndiaFloodEngine
from visualization.flood_map_plot import (
    depth_to_rgba,
    risk_to_rgba,
    velocity_to_rgba,
    _array_to_base64_png,
)

logger = logging.getLogger("inundation_api")

from app.core.config import settings
OUTPUT_DIR = ENGINE_ROOT / "web_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR = settings.FRONTEND_DIR / "inundation"

router = APIRouter(tags=["Inundation Simulator 2.0"])

# Global simulation state
simulation_state: Dict[str, Any] = {
    "status": "idle",
    "progress": 0,
    "current_step": "",
    "error": None,
    "last_result": None,
    "engine_instance": None,
}

# Pre-defined scenario presets
SCENARIOS = {
    "kerala_2018": {
        "name": "Kerala 2018 Monsoon Flood",
        "description": "Extreme orographic deluge in Western Ghats (Ernakulam / Idukki)",
        "bbox": [76.50, 9.90, 76.90, 10.30],
        "rainfall_mm": 150.0,
        "duration_hr": 12.0,
        "amc": "III",
        "region": "Western Ghats & Konkan Coast",
    },
    "kerala_idukki": {
        "name": "Idukki Reservoir Catchment Spill",
        "description": "Periyar river flash discharge across high-gradient gorge",
        "bbox": [76.85, 9.75, 77.15, 10.05],
        "rainfall_mm": 210.0,
        "duration_hr": 16.0,
        "amc": "III",
        "region": "Western Ghats & Konkan Coast",
    },
    "kerala_kuttanad": {
        "name": "Kuttanad Backwater Basin Overflow",
        "description": "Pamba & Meenachil basin delta sub-sea-level ponding",
        "bbox": [76.32, 9.35, 76.58, 9.58],
        "rainfall_mm": 140.0,
        "duration_hr": 24.0,
        "amc": "III",
        "region": "Western Ghats & Konkan Coast",
    },
    "chennai_2015": {
        "name": "Chennai 2015 Cloudburst",
        "description": "Catastrophic coastal cloudburst over Adyar & Cooum basins",
        "bbox": [80.05, 12.90, 80.30, 13.15],
        "rainfall_mm": 280.0,
        "duration_hr": 12.0,
        "amc": "III",
        "region": "Peninsular India (East Coast)",
    },
    "assam_2020": {
        "name": "Assam Brahmaputra Flood",
        "description": "Monsoon riverine flood across Kaziranga floodplain",
        "bbox": [93.10, 26.50, 93.50, 26.80],
        "rainfall_mm": 180.0,
        "duration_hr": 24.0,
        "amc": "III",
        "region": "Brahmaputra Valley",
    },
    "mumbai_2005": {
        "name": "Mumbai 2005 Mega Deluge",
        "description": "Historical 944mm record rainfall event over Mithi river",
        "bbox": [72.78, 18.98, 72.98, 19.22],
        "rainfall_mm": 350.0,
        "duration_hr": 18.0,
        "amc": "III",
        "region": "Western Ghats & Konkan Coast",
    },
    "delhi_2023": {
        "name": "Delhi Yamuna Flood 2023",
        "description": "Upper catchment discharge combined with urban flash flooding",
        "bbox": [77.10, 28.55, 77.32, 28.75],
        "rainfall_mm": 120.0,
        "duration_hr": 8.0,
        "amc": "II",
        "region": "Indo-Gangetic Plain",
    },
}


class SimRequest(BaseModel):
    bbox: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    rainfall_mm: float = Field(default=120.0, ge=1.0, le=2000.0)
    duration_hr: float = Field(default=12.0, ge=0.5, le=168.0)
    amc: str = Field(default="III")
    dem_type: str = Field(default="cop30")
    use_synthetic: bool = Field(default=False)


@router.get("/inundation", response_class=HTMLResponse)
@router.get("/inundation/", response_class=HTMLResponse)
def serve_inundation_ui():
    """Serve the styled Inundation Simulator UI."""
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        index_file = ENGINE_ROOT / "web" / "index.html"
    if index_file.exists():
        resp = FileResponse(str(index_file))
        resp.headers["X-Frame-Options"] = "ALLOWALL"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    return HTMLResponse("<h3>Inundation simulator UI template not found.</h3>", status_code=404)


@router.get("/api/presets")
@router.get("/api/inundation/presets")
def get_presets():
    """Return available scenario presets."""
    return SCENARIOS


@router.get("/api/weather")
@router.get("/api/inundation/weather")
def fetch_weather(lat: float = Query(...), lon: float = Query(...)):
    """Fetch live 7-day weather forecast from Open-Meteo."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation,weather_code",
            "forecast_days": 7,
            "timezone": "auto",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        hourly = data.get("hourly", {})
        precip = hourly.get("precipitation", [])
        times = hourly.get("time", [])

        total_24h = sum(precip[:24]) if len(precip) >= 24 else sum(precip)
        total_48h = sum(precip[:48]) if len(precip) >= 48 else sum(precip)
        total_7d = sum(precip)
        max_hourly = max(precip) if precip else 0.0

        suggested_rain = round(total_24h if total_24h > 10.0 else max(total_48h, 25.0), 1)
        suggested_dur = 24.0 if total_24h > 10.0 else 48.0

        return {
            "status": "success",
            "location": {"lat": lat, "lon": lon},
            "summary": {
                "total_24h_mm": round(total_24h, 1),
                "total_48h_mm": round(total_48h, 1),
                "total_7d_mm": round(total_7d, 1),
                "max_hourly_mm": round(max_hourly, 1),
                "suggested_rainfall_mm": suggested_rain,
                "suggested_duration_hr": suggested_dur,
            },
            "hourly_precipitation": precip[:48],
            "hourly_times": times[:48],
        }
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast: {e}")


@router.post("/api/simulate")
@router.post("/api/inundation/simulate")
def run_simulation(req: SimRequest):
    """Execute the full 5-step FastFlood simulation and return map overlays."""
    global simulation_state

    bbox = tuple(req.bbox)
    if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        raise HTTPException(status_code=400, detail="Invalid bounding box [min_lon, min_lat, max_lon, max_lat]")

    logger.info(f"Starting FastFlood simulation: rain={req.rainfall_mm}mm, dur={req.duration_hr}h, bbox={bbox}")
    simulation_state["status"] = "running"
    simulation_state["progress"] = 5
    simulation_state["current_step"] = "Initializing FastFlood hydrodynamic engine..."

    try:
        force_synthetic = (req.dem_type == "synthetic")

        config = {
            "amc": req.amc,
            "dem_type": "cop30" if not force_synthetic else "synthetic",
            "stream_threshold_km2": 0.5,
            "use_synthetic_dem": force_synthetic,
            "use_synthetic_lulc": force_synthetic,
            "use_default_soil": force_synthetic,
            "save_geotiff": True,
            "save_html_map": True,
            "save_png_map": True,
        }

        # Clear previous run outputs while preserving raw cached tiles
        import shutil
        for fname in ["dem_cop30.tif", "dem_synthetic.tif", "dem_nasadem.tif"]:
            fpath = OUTPUT_DIR / "dem" / fname
            if fpath.exists():
                fpath.unlink(missing_ok=True)
        terrain_dir = OUTPUT_DIR / "terrain"
        if terrain_dir.exists():
            shutil.rmtree(terrain_dir, ignore_errors=True)

        engine = IndiaFloodEngine(
            bbox=bbox,
            output_dir=str(OUTPUT_DIR),
            config=config,
        )
        simulation_state["engine_instance"] = engine

        # Step 1: Terrain Conditioning
        dem_label = "Synthetic Benchmark Terrain" if force_synthetic else "Copernicus GLO-30 Real DEM"
        simulation_state["progress"] = 20
        simulation_state["current_step"] = f"Step 1/5: {dem_label} — hydro-conditioning..."
        engine.load_terrain()
        engine.load_land_cover()
        engine.load_soils()
        engine.prepare_model_parameters()

        # Step 2: D8 Flow Routing
        simulation_state["progress"] = 45
        simulation_state["current_step"] = "Step 2/5: Computing D8 flow routing & accumulation"
        engine.compute_flow_network()

        # Step 3: Steady-State Discharge (SCS-CN)
        simulation_state["progress"] = 65
        simulation_state["current_step"] = "Step 3/5: Computing SCS-CN steady-state discharge"
        engine.compute_steady_discharge(req.rainfall_mm, req.duration_hr)

        # Step 4: Partial Steady-State Lag Correction
        simulation_state["progress"] = 80
        simulation_state["current_step"] = "Step 4/5: Applying partial steady-state lag correction"
        engine.apply_partial_correction(req.duration_hr)

        # Step 5: Depth Inversion & HAND
        simulation_state["progress"] = 90
        simulation_state["current_step"] = "Step 5/5: Inverting Manning equation & HAND flood mapping"
        engine.estimate_flood_depth()

        # Generate outputs
        simulation_state["progress"] = 95
        simulation_state["current_step"] = "Generating raster outputs and visual overlays"
        output_paths = engine.generate_outputs(req.rainfall_mm, req.duration_hr)

        # Generate Base64 Overlays
        depth_rgba = depth_to_rgba(engine.flood_depth)
        depth_b64 = _array_to_base64_png(depth_rgba)

        risk_rgba = risk_to_rgba(engine.flood_depth)
        risk_b64 = _array_to_base64_png(risk_rgba)

        vel_rgba = velocity_to_rgba(engine.velocity)
        vel_b64 = _array_to_base64_png(vel_rgba)

        min_lon, min_lat, max_lon, max_lat = bbox
        bounds = [[min_lat, min_lon], [max_lat, max_lon]]
        center = [(min_lat + max_lat) / 2.0, (min_lon + max_lon) / 2.0]

        result_payload = {
            "status": "success",
            "bounds": bounds,
            "center": center,
            "stats": engine.stats,
            "overlays": {
                "depth": depth_b64,
                "risk": risk_b64,
                "velocity": vel_b64,
            },
            "downloads": {
                "depth_geotiff": "/api/download/flood_depth_m.tif",
                "risk_geotiff": "/api/download/flood_risk_class.tif",
                "velocity_geotiff": "/api/download/flood_velocity_ms.tif",
                "hand_geotiff": "/api/download/flood_hand_m.tif",
                "flow_regime_geotiff": "/api/download/flood_flow_regime.tif",
                "shapefile_zip": "/api/download/flood_extent_shapefile.zip",
                "geojson": "/api/download/flood_extent.geojson",
                "static_map": "/api/download/flood_map.png",
                "interactive_html": "/api/download/flood_map_interactive.html",
                "report_json": "/api/download/flood_report.json",
            },
        }

        simulation_state["status"] = "completed"
        simulation_state["progress"] = 100
        simulation_state["current_step"] = "Simulation Complete"
        simulation_state["last_result"] = result_payload

        return result_payload

    except Exception as e:
        logger.exception(f"Inundation simulation failed: {e}")
        simulation_state["status"] = "error"
        simulation_state["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/query_point")
@router.get("/api/inundation/query_point")
def query_point(lat: float = Query(...), lon: float = Query(...)):
    """Query flood depth, velocity, flow type, baseline river depth, and elevation at any clicked map point."""
    engine = simulation_state.get("engine_instance")
    if engine is None or engine.flood_depth is None or engine.meta is None:
        return {"found": False, "message": "No active simulation"}

    try:
        from rasterio.transform import rowcol
        r, c = rowcol(engine.meta["transform"], lon, lat)
        rows, cols = engine.flood_depth.shape

        if 0 <= r < rows and 0 <= c < cols:
            depth = float(engine.flood_depth[r, c])
            vel = float(engine.velocity[r, c]) if engine.velocity is not None else 0.0
            elev = float(engine.dem[r, c]) if engine.dem is not None else 0.0
            hand = float(engine.hand[r, c]) if engine.hand is not None else 0.0
            base_depth = float(engine.base_river_depth[r, c]) if hasattr(engine, "base_river_depth") and engine.base_river_depth is not None else 0.0
            regime = int(engine.flow_regime[r, c]) if hasattr(engine, "flow_regime") and engine.flow_regime is not None else 0

            if depth <= 0.05:
                flow_label = "Dry Ground"
            elif regime == 1 or vel >= 0.15:
                flow_label = "Active River / Stream Flow"
            else:
                flow_label = "Surface Puddle / Depression Ponding"

            if depth <= 0.05:
                risk_label = "Dry / Normal"
                risk_code = 0
            elif depth < 0.3:
                risk_label = "Low (Ankle deep)"
                risk_code = 1
            elif depth < 1.0:
                risk_label = "Medium (Knee to waist)"
                risk_code = 2
            elif depth < 2.0:
                risk_label = "High (Life danger)"
                risk_code = 3
            else:
                risk_label = "Extreme (Catastrophic)"
                risk_code = 4

            return {
                "found": True,
                "lat": lat,
                "lon": lon,
                "depth_m": round(depth, 2),
                "base_river_depth_m": round(base_depth, 2),
                "total_water_depth_m": round(depth + base_depth, 2),
                "velocity_ms": round(vel, 2),
                "elevation_m": round(elev, 1),
                "hand_m": round(hand, 1),
                "flow_type": flow_label,
                "risk_class": risk_code,
                "risk_label": risk_label,
            }
        else:
            return {"found": False, "message": "Clicked point is outside simulation domain"}
    except Exception as e:
        return {"found": False, "error": str(e)}


@router.get("/api/download/{filename}")
@router.get("/api/inundation/download/{filename}")
def download_output_file(filename: str):
    """Download output GeoTIFF, Shapefile zip, GeoJSON, PNG, HTML map, or JSON report."""
    target = OUTPUT_DIR / filename
    if target.exists():
        media_type = "application/octet-stream"
        if filename.endswith(".html"):
            media_type = "text/html"
        elif filename.endswith(".png"):
            media_type = "image/png"
        elif filename.endswith(".json"):
            media_type = "application/json"
        elif filename.endswith(".geojson"):
            media_type = "application/geo+json"
        elif filename.endswith(".zip"):
            media_type = "application/zip"
        elif filename.endswith(".tif"):
            media_type = "image/tiff"
        return FileResponse(str(target), filename=filename, media_type=media_type)
    raise HTTPException(status_code=404, detail=f"File {filename} not found")
