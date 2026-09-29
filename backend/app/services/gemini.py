"""
VELLAM Geospatial Platform - Google Gemini Remote Sensing Service
Integrates Google Gemini 2.5 generative multimodal models for remote sensing,
topographic feature extraction, and AI watershed management planning.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Check if official Google GenAI SDK is available in environment
try:
    from google import genai
    from google.genai import types

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def query_gemini_for_land_interpretation(
    c_lat: float, c_lng: float, area_km2: float
) -> Optional[Dict[str, Any]]:
    """
    Query Google Gemini 2.5 Flash for remote sensing terrain analysis and watershed recommendations.
    Returns structured JSON data or None if API key is not configured or an error occurs.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key or not GEMINI_AVAILABLE:
        return None

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Act as a senior remote-sensing GIS engineer and hydrologist for KSDMA Kerala.
        Analyse satellite ground coordinates at Lat: {c_lat:.4f}, Lng: {c_lng:.4f} covering {area_km2} km² in Kerala, India.

        Identify:
        1. Local terrain, district, river catchment, and vegetation/urban cover.
        2. Mean slope degree, SCS Curve Number runoff coefficient, baseline soil loss (tonnes/ha/yr).
        3. Real hydrological bottlenecks (landslide, flood, waterlogging).
        4. If this is a critical protected infrastructure (airport, port, dam, etc.) where restructuring is prohibited.
        5. 4 tailored, scientifically defensible watershed-management measures.
        6. Quantitative expected benefits: peak discharge reduction %, soil saved (tonnes/ha), and infiltration gain %.

        Respond ONLY in strict, valid JSON:
        {{
            "is_restricted_property": boolean,
            "property_warning": "string or null",
            "zone": "string describing local physiographic zone and district",
            "mean_slope_deg": number,
            "runoff_coefficient": number,
            "baseline_soil_loss_t_ha": number,
            "action_priority": "string",
            "bottleneck": "string describing specific local risk",
            "scientific_measures": ["string 1", "string 2", "string 3", "string 4"],
            "expected_outcomes": {{
                "discharge_reduction_pct": number,
                "sediment_retention_t_ha": number,
                "recharge_gain_pct": number
            }}
        }}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        if response and response.text:
            return json.loads(response.text)
    except Exception as exc:
        logger.warning(f"Gemini API inference skipped or failed: {exc}")
        return None

    return None
