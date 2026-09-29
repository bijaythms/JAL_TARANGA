# Jal Taranga — Complete Platform Walkthrough, Architecture & Data Provenance Guide

> **"Rise Above Risk. Protect Kerala. From Data to Decisions. From Risk to Resilience."**  
> Developed by **VISIONQUEST**

---

## 1. Project Mission & Overview

**Jal Taranga** is an advanced Earth-observation, hydrological modeling, and disaster intelligence decision-support platform engineered specifically for the state of **Kerala, India**.

### Why Kerala Needs Jal Taranga
Kerala is uniquely vulnerable to climate-induced hydro-meteorological catastrophes:
- **44 River Basins**: Traversing steep gradients from the Western Ghats (up to 2,695 m MSL at Anamudi) to the Arabian Sea within just 60 to 120 kilometers.
- **Extreme Orographic Monsoons**: Annual precipitation between 2,500 mm and over 5,000 mm, causing rapid flood peaks and dangerously short basin times of concentration.
- **Landslide Susceptibility**: Thick saprolite regolith on steep slopes subjected to pore-pressure liquefaction upon sustained rainfall (>180 mm/24 h), as witnessed in Meppadi/Chooralmala (Wayanad), Pettimudi (Munnar), and Kavalappara (Malappuram).
- **Lowland Depression & Tidal Bottlenecks**: Sub-sea-level agrarian polder basins like **Kuttanad** (-1.5 m to +1.5 m MSL) and estuarine urban centers like **Greater Kochi** where river discharge meets high astronomical ocean tides.

Jal Taranga provides government authorities, disaster managers, hydro-engineers, and citizens with a unified **digital twin**: combining real-time multi-spectral satellite imagery, 30-meter hydro-corrected elevation models, deterministic physics equations, Google Gemini 2.5 AI remote sensing, and crowdsourced ground-truth telemetry.

---

## 2. System Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND CLIENT (Leaflet + Tailwind)                      │
│   • Responsive Glassmorphic Dashboard        • Leaflet GIS v1.9.4 Mapping Engine       │
│   • Chart.js Dynamic Hydrographs            • Lucide Spatial Icons & Light/Dark Theme │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP / REST & GeoJSON
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                             BACKEND CORE (FastAPI / Python 3.12)                       │
│   • /api/geospatial (Baselines, DEM Accumulation, Slope FoS, AI Snip, Delineation)     │
│   • /api/srishti    (ISRO Bhuvan SRISHTI/DRISHTI multi-spectral assets & crops)        │
│   • /api/reports    (Crowdsourced field telemetry with server-side email encryption)   │
│   • /api/admin      (Timing-safe HMAC authenticated incident triage portal)            │
└─────────────────────┬───────────────────────────────────────────────┬──────────────────┘
                      │                                               │
┌─────────────────────▼───────────────────────┐ ┌─────────────────────▼──────────────────┐
│         COMPUTATIONAL ENGINES               │ │              STORAGE & APIS            │
│  • Micro-Terrain 7-Zone Hydrology Solver    │ │  • PostgreSQL 16 + PostGIS Spatial DB  │
│  • Taylor Infinite Slope Stability Solver   │ │  • Local Thread-Safe JSON Fallbacks    │
│  • SCS Curve Number Runoff Accumulator      │ │  • Esri World Imagery REST Server      │
│  • MERIT-Basins Hydro Catchment Engine      │ │  • OpenStreetMap Nominatim Geocoder    │
│  • Google Gemini 2.5 Flash Remote Sensing   │ │  • ISRO Bhuvan PMKSY-WDC Registry      │
│  • Multi-Spectral VARI/NDVI Band Processor  │ │  • Statutory Protected Landmark Shield │
└─────────────────────────────────────────────┘ └────────────────────────────────────────┘
```

| Layer | Technologies Used | Key Responsibilities |
|---|---|---|
| **Frontend** | HTML5, Tailwind CSS v3.4, Vanilla JavaScript, Leaflet.js v1.9.4, MapLibre GL JS, Chart.js, Lucide Spatial Icons | Responsive glassmorphic interface, 2D vector overlays, 3D elevation terrain, dynamic hydrographs, client-side EXIF GPS extraction. |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Passlib (Bcrypt), HMAC-SHA256 | High-performance asynchronous REST endpoints, role authentication, multi-store cache sync, security middleware. |
| **Spatial & GIS** | PostgreSQL 16 + PostGIS 3.5, Shapely, PyProj, GeoJSON, MERIT-Basins | Spatial indexing (GIST), topological point-in-polygon tests, upstream catchment delineation, dendritic stream hierarchy. |
| **Remote Sensing** | NumPy, PIL (Pillow), Esri World Imagery REST API, ISRO Bhuvan SRISHTI | Multi-spectral band processing, VARI-to-NDVI translation, NDWI surface water indexing, dynamic false-color satellite cropping. |
| **AI / ML** | Google Gemini 2.5 Flash SDK (`google-genai`) & 7-Zone Microterrain Solver | Multimodal remote-sensing landscape vision analysis, soil erosion classification, structural intervention planning. |
| **Database & Stores**| PostgreSQL 16 + PostGIS 3.5 (`vellam_db`) & Dual-Write Thread-Safe JSON Stores | Persistent storage for 14 districts, 23 river basins, user tiers (`administrators`, `officers`, `citizens`), and citizen incident reports. |
| **Test Suite** | pytest, pytest-asyncio, HTTPX / Starlette TestClient | 45 automated integration and unit test cases covering API, Auth, Delineation, Hydrology, and Multi-Store Sync. |

---

## 3. Tour of All 11 Application Views

### View 0: Scenic Authentication Portal (`#view-login`)
- **What is showing**:
  - Full-screen scenic portal automatically presented upon initial link load or refresh (prevents unauthenticated direct access).
  - **Segregated Dual-Tier Tabs**:
    - *Admin & Officers*: Requires registered username/email and password or Master Secret Key (`VIP@DUK`). Live database accounts: `priyan`, `aqeeb`, `bijay`, `femin`, and `admin`.
    - *Citizens*: Requires phone/email/username and password.
  - **Citizen Registration Modal**: Interactive registration form with phone/email and password validation. Upon registration, it seamlessly switches to the sign-in tab, pre-fills credentials, and prompts manual login.
  - **Role Navigation Shield**: Strict role-scoped sidebar navigation ensuring Citizens access only Community Incidents, District Rankings, and About, while Officers and Admins receive full operational clearance.
- **Where data comes from**:
  - Authentication: `POST /api/auth/login` and `POST /api/auth/register-citizen`.
  - Security Core: `backend/app/core/security.py` using bcrypt password verification.

---

### View 1: Home (`#view-home`)
- **What is showing**:
  - Hero introduction with quick action buttons: *"Explore Kerala"*, *"Analyse an Area"*, and *"Report a Disaster"*.
  - Feature cards linking directly to Satellite Earth-Obs, Terrain Engine, Rainfall Simulation, and Landslide Hazards.
  - Real-time statewide hazard matrix and emergency bulletins.
- **Where data comes from**: Semantic presentation layout embedded directly in `frontend/index.html`.

---

### View 2: GIS Command Centre & Watershed Delineator (`#view-gis`)
- **What is showing**:
  - **Full-Screen Leaflet Interactive Map**: Satellite imagery basemap with smooth panning and zooming.
  - **7-Pill Floating Map Dock** (top-center pill toolbar):
    1. `Focus`: Toggles Zen Mode, hiding sidebars for 100% clean, unobstructed satellite analysis.
    2. `Tools`: Collapses/expands the left analytical tools drawer.
    3. `Legends`: Collapses/expands the Map Symbols & Legends sidepanel.
    4. `Layers`: Toggles base satellite imagery and tile servers.
    5. `Telemetry`: Displays live hydrological simulation HUD.
    6. `Details`: Collapses/expands the right district telemetry and feature inspection drawer.
    7. `Full`: Toggles browser full-screen map mode.
  - **7 Fine-Grained Layer Toggles** (in *Map Symbols & Legends*):
    1. *Watershed Basins*: Calibrated river catchment spatial boundaries.
    2. *DEM Pooling Zones*: Critical lowland accumulation depressions (Kuttanad, Aluva, Kole wetlands).
    3. *Landslide Hazard Scarps*: High-risk Western Ghats escarpments.
    4. *District Vulnerability Centroids*: Markers for all 14 Kerala districts.
    5. *Citizen Observations*: Live crowdsourced incident markers with color-coded severity.
    6. *Delineated Catchment*: Upstream catchment polygon from point-and-click delineation.
    7. *Tributary Reaches*: Upstream river flow vector hierarchy.
  - **AI Snip Tool**: Bounding-box selection tool allowing the user to drag an arbitrary rectangle on the map.
  - **Statutory Landmark Protection Shield**: Instantly warns and restricts terrain earthworks if snipped over Cochin International Airport (COK), Idukki Dam, or Cochin Port.
  - **Point-and-Click Watershed Delineator**: Click anywhere on the map to trace the complete upstream drainage basin and tributary network using MERIT-Basins.
  - **Live Place Search**: Autocompletes across Kerala districts, towns, rivers, and landmarks bounded strictly to Kerala.
  - **District Inspection Drawer**: Slides out from the right showing vulnerability score, slope, drainage density, and flood/landslide village counts.
- **Where data comes from**:
  - Map tiles: **Esri World Imagery** and **Google Hybrid**.
  - Baseline layers: `GET /api/kerala/baseline` (from PostgreSQL `districts`, `river_basins`, or fallback `districts.json` and `watersheds.json`).
  - Snip Analysis: `POST /api/watershed/ai-plan` (Gemini 2.5 API or 7-Zone Microterrain Hydrology Solver).
  - Delineation: `POST /api/watershed/delineate` (MERIT-Basins dataset or synthetic Kerala catchment engine).
  - Place Search: **OSM Nominatim API** bounded to Kerala `[8.15, 74.80]` to `[12.85, 77.60]`.

---

### View 3: Satellite Earth-Observation (`#view-satellite`)
- **What is showing**:
  - Multi-spectral Earth Observation dashboard aligned with **ISRO Bhuvan SRISHTI & DRISHTI** (PMKSY-WDC watershed programs).
  - **Multi-Spectral Index Visualizer**:
    - **True Color (RGB)**: Natural visual surface.
    - **NDVI (Normalized Difference Vegetation Index)**: Photosynthetic canopy density and greening.
    - **NDWI (Normalized Difference Water Index)**: Water body delineation and open water impoundments.
    - **MNDWI / NDMI**: Modified water index and moisture stress indicators.
    - **BSI (Bare Soil Index)**: Exposed regolith and erosion zones.
  - **Monitored Watershed Assets Table**: Listing check dams, percolation ponds, and recharge shafts across Devikulam, Meppadi, Attappadi, and Kuttanad.
  - **Satellite Crop Inspector**: Interactive comparison showing before/after imagery with NDVI canopy overlays.
  - **DRISHTI Mobile Terminal Registration**: Form for field officers to geotag new watershed conservation assets with compass bearing, altitude, and GPS accuracy.
- **Where data comes from**:
  - Assets & Registry: `GET /api/srishti/assets` (from `backend/app/data/srishti_assets.json`).
  - Satellite Crop Generator: `GET /api/srishti/satellite-crop?lat=...&lng=...&mode=ndvi` (contacts **Esri World Imagery Export REST API**, processes RGB into VARI/NDVI in Python with NumPy, falls back to pre-rendered high-res Sentinel-2 imagery in `frontend/images/watershed/`).
  - Analytics Summary: `GET /api/srishti/analytics`.

---

### View 4: Rainfall Runoff Simulator (`#view-simulator`)
- **What is showing**:
  - Dynamic simulation of precipitation impact on Kerala's river basins.
  - **3 Rain Scenarios**:
    - *Moderate*: 25 mm/h (Standard monsoon shower).
    - *High*: 60 mm/h (Heavy monsoon surge).
    - *Extreme*: 130 mm/h (Cloudburst / 2018-scale disaster storm).
  - Basin selector dropdown (Periyar, Bharathapuzha, Pamba, Chaliyar, etc.).
  - Quantitative Metrics: Accumulated runoff volume in **MCM (Million Cubic Meters)**, Inundated surface footprint in **hectares**, and peak overland flow velocity in **m/s**.
  - Dynamic Hydrograph Curve: Dual-wave Chart.js hydrograph comparing precipitation intensity against discharge propagation over time.
- **Where data comes from**:
  - Endpoint: `POST /api/dem/accumulation`.
  - Service: `compute_water_accumulation()` in `backend/app/services/hydrology.py` using **SCS Curve Number** hydrology formulas calibrated against basin drainage areas in `watersheds.json`.

---

### View 5: Vulnerability Index & District Matrix (`#view-ranking`)
- **What is showing**:
  - Comprehensive vulnerability scoreboard for all **14 administrative districts of Kerala**.
  - Sorted rankings by overall vulnerability score (0 to 100):
    - *Wayanad* (Score 94 - High Landslide Risk)
    - *Idukki* (Score 91 - High Orographic & Slope Risk)
    - *Alappuzha* (Score 89 - Sub-sea-level Flood Basin)
    - *Ernakulam, Pathanamthitta, Thrissur, etc.*
  - Detailed metrics per district: Total revenue villages, flood-prone villages, landslide-prone villages, mean slope in degrees, drainage density, and major draining rivers.
  - Quick action to zoom to any district on the GIS map.
- **Where data comes from**:
  - Endpoint: `GET /api/kerala/baseline`.
  - Database: PostgreSQL table `districts` (fallback `backend/app/data/districts.json`).
  - Source Authorities: **KSDMA District Disaster Management Plans (DDMP)**, **State Hazard Vulnerability Risk Assessment (HVRA)**, and **Census of India**.

---

### View 6: Erosion & Landslide Hazard Analytics (`#view-landslides`)
- **What is showing**:
  - **Western Ghats High-Risk Scarp Hotspots**: Real-world locations (Chooralmala/Meppadi, Pettimudi, Kavalappara, Kokkayar, Vilangad) with current Factor of Safety (FS), regolith depth, and severity.
  - **Taylor Infinite Slope Stability Interactive Simulator**:
    - Interactive sliders: Slope Angle ($10^\circ$ to $60^\circ$), Soil Saturation ($0\%$ to $100\%$), Regolith Depth ($0.5\text{ m}$ to $8\text{ m}$), Root Cohesion ($0\text{ to }35\text{ kPa}$), and Internal Friction Angle ($15^\circ\text{ to }45^\circ$).
    - Real-Time Calculated Physics:
      - **Factor of Safety (FS)**: $< 1.0$ (Critical Failure Imminent / Red Alert), $1.0 - 1.3$ (Quasi-Stable / Watch Warning), $> 1.3$ (Geotechnically Stable).
      - Resisting Shear Strength vs. Driving Shear Stress (in kPa).
      - Effective biological root anchoring percentage.
      - Geotechnical engineering advisory.
- **Where data comes from**:
  - Hotspot list: `GET /api/landslides/hazards`.
  - Slope Physics Solver: `POST /api/landslides/simulate-slope`.
  - Science Source: **Geological Survey of India (GSI) Western Ghats Landslide Zonation** and **NCESS Landslide Telemetry**. Formulated via the Taylor Infinite Slope limit-equilibrium equation in `backend/app/api/geospatial.py`.

---

### View 3: Watershed Intervention Simulation Lab (`#view-intervention`)
- **What is showing**:
  - Decision-support lab designed for engineers, panchayat officials, and community leaders to evaluate ecological and structural watershed interventions before spending public funds.
  - **4 Primary Intervention Categories**:
    1. *Check Dams* (Loose boulder, masonry, and gabion cascade barriers to slow down gully velocity).
    2. *Contour Bunding* (Staggered earthen bunds and trenches across slope contours to trap sheet runoff).
    3. *Percolation Ponds* (Infiltration basins and recharge shafts to harvest stormwater into aquifers).
    4. *Riparian Afforestation* (Multi-tier native vegetative buffers and vetiver grass to anchor stream banks).
  - **Interactive Parameter Controls**:
    - River Basin selector (Periyar, Bharathapuzha, Pamba, etc.).
    - Intervention density slider (10% to 100% implementation).
    - Design storm event slider (50 mm to 300 mm rainfall).
    - Soil type selector (Laterite, Clayey Loam, Sandy Alluvial, Gravelly Regolith).
  - **Simulated Outcomes**:
    - Peak discharge attenuation percentage.
    - Soil erosion reduction (tons/hectare saved).
    - Aquifer recharge enhancement percentage.
    - Estimated capital expenditure in Indian Rupees (INR) alongside Civil Bill of Quantities (BoQ) and MGNREGS rural labor budgeting.
    - Comparative hydrograph chart (Pre-intervention vs. Post-intervention flood wave).
- **Where data comes from**:
  - Basin metadata: `GET /api/intervention/basins`.
  - Simulation engine: `POST /api/intervention/simulate`.
  - Science Source: Calibrated empirical equations in `simulate_intervention()` in `backend/app/services/hydrology.py`, combining **SCS Runoff Curve Numbers (CN)**, **Universal Soil Loss Equation (USLE)** parameters, and **CWRDM / PMKSY watershed guidelines**.

---

### View 4: Inundation Hydrodynamic Simulator (`#view-inundation`)
- **What is showing**:
  - High-precision hydrodynamic inundation simulator iframe embedded with live simulation telemetry.
  - Variable precipitation intensity controls (50 mm/h to 300 mm/h cloudburst triggers).
  - Dynamic DEM depression pooling across critical lowlands:
    - *Kuttanad Polders*: Sub-sea-level agricultural basin (-1.5 m MSL) subject to prolonged backwater accumulation.
    - *Aluva / Periyar Urban Plains*: Estuarine bottlenecks and urban drainage overflow.
    - *Kole Wetlands (Thrissur)*: Wetland buffering and floodwater storage dynamics.
  - Color-coded depth visualization: Blue flood contours, breach vectors, and submerged infrastructure alerts.
- **Where data comes from**:
  - DEM Source: CartoDEM 30m / SRTM hydro-corrected elevation dataset.
  - Hydrology engine: `backend/app/services/hydrology.py` (`compute_water_accumulation`).

---

### View 5: Satellite Earth-Observation (`#view-satellite`)
- **What is showing**:
  - Multi-spectral Earth Observation dashboard aligned with **ISRO Bhuvan SRISHTI & DRISHTI** (PMKSY-WDC watershed programs).
  - **Multi-Spectral Index Visualizer**:
    - **True Color (RGB)**: Natural visual surface.
    - **NDVI (Normalized Difference Vegetation Index)**: Photosynthetic canopy density and greening.
    - **NDWI (Normalized Difference Water Index)**: Water body delineation and open water impoundments.
    - **MNDWI / NDMI**: Modified water index and moisture stress indicators.
    - **BSI (Bare Soil Index)**: Exposed regolith and erosion zones.
  - **Monitored Watershed Assets Table**: Listing check dams, percolation ponds, and recharge shafts across Devikulam, Meppadi, Attappadi, and Kuttanad.
  - **Satellite Crop Inspector**: Interactive comparison showing before/after imagery with NDVI canopy overlays.
  - **DRISHTI Mobile Terminal Registration**: Form for field officers to geotag new watershed conservation assets with compass bearing dial, altitude (MSL), and GPS accuracy.
- **Where data comes from**:
  - Assets & Registry: `GET /api/srishti/assets` (from `backend/app/data/srishti_assets.json`).
  - Satellite Crop Generator: `GET /api/srishti/satellite-crop?lat=...&lng=...&mode=ndvi` (contacts **Esri World Imagery Export REST API**, processes RGB into VARI/NDVI in Python with NumPy, falls back to pre-rendered high-res Sentinel-2 imagery in `frontend/images/watershed/`).
  - Analytics Summary: `GET /api/srishti/analytics`.

---

### View 6: Erosion & Landslides 3D Lab (`#view-landslides`)
- **What is showing**:
  - **Western Ghats High-Risk Scarp Hotspots**: Real-world locations (Chooralmala/Meppadi, Pettimudi, Kavalappara, Kokkayar, Vilangad) with current Factor of Safety (FS), regolith depth, and severity.
  - **Dual 2D/3D Mode**: Switch seamlessly between 2D Leaflet spatial map and **3D MapLibre Elevation Terrain Viewer** with real-world topography pitch and bearing.
  - **Taylor Infinite Slope Stability Interactive Simulator**:
    - Interactive sliders: Slope Angle ($10^\circ$ to $60^\circ$), Soil Saturation ($0\%$ to $100\%$), Regolith Depth ($0.5\text{ m}$ to $8\text{ m}$), Root Cohesion ($0\text{ to }35\text{ kPa}$), and Internal Friction Angle ($15^\circ\text{ to }45^\circ$).
    - Real-Time Calculated Physics:
      - **Factor of Safety (FS)**: $< 1.0$ (Critical Failure Imminent / Red Alert), $1.0 - 1.3$ (Quasi-Stable / Watch Warning), $> 1.3$ (Geotechnically Stable).
      - Resisting Shear Strength vs. Driving Shear Stress (in kPa).
      - Effective biological root anchoring percentage.
      - Geotechnical engineering advisory.
  - **USLE / RUSLE Soil Erosion Loss Calculator**:
    - Computes annual soil loss ($A = R \times K \times LS \times C \times P$) in tons/hectare/year.
- **Where data comes from**:
  - Hotspot list: `GET /api/landslides/hazards`.
  - Slope Physics Solver: `POST /api/landslides/simulate-slope`.
  - Science Source: **Geological Survey of India (GSI) Western Ghats Landslide Zonation** and **NCESS Landslide Telemetry**. Formulated via the Taylor Infinite Slope limit-equilibrium equation in `backend/app/api/geospatial.py`.

---

### View 7: Rainfall Runoff Scenario Simulator (`#view-simulator`)
- **What is showing**:
  - Dynamic simulation of precipitation impact on Kerala's river basins.
  - **3 Rain Scenarios**:
    - *Moderate*: 25 mm/h (Standard monsoon shower).
    - *High*: 60 mm/h (Heavy monsoon surge).
    - *Extreme*: 130 mm/h (Cloudburst / 2018-scale disaster storm).
  - Basin selector dropdown (Periyar, Bharathapuzha, Pamba, Chaliyar, etc.).
  - Quantitative Metrics: Accumulated runoff volume in **MCM (Million Cubic Meters)**, Inundated surface footprint in **hectares**, and peak overland flow velocity in **m/s**.
  - Dynamic Hydrograph Curve: Dual-wave Chart.js hydrograph comparing precipitation intensity against discharge propagation over time.
- **Where data comes from**:
  - Endpoint: `POST /api/dem/accumulation`.
  - Service: `compute_water_accumulation()` in `backend/app/services/hydrology.py` using **SCS Curve Number** hydrology formulas calibrated against basin drainage areas in `watersheds.json`.

---

### View 8: Community Field Hazard Reporting (`#view-community`)
- **What is showing**:
  - Citizen participatory GIS portal allowing field observers and residents to report live flood, landslide, or drainage incidents.
  - Report Form:
    - Incident Category (Landslide / Slope Failure, Flood / Water Accumulation, River Spillover, Blocked Culvert).
    - District and GPS Coordinates (with "Use My Location" browser geolocation).
    - Incident description.
    - Submitter email (encrypted on server for privacy).
    - Photo proof file upload with **client-side EXIF GPS extraction** (auto-populates latitude and longitude from photo metadata).
  - Public Feed: Live list of reported incidents showing status badge (`Under Review`, `Verified`, `Action Initiated`, `Resolved`), timestamps, and photo inspection lightbox.
- **Where data comes from**:
  - Public feed: `GET /api/reports` (returns sanitized entries with submitter personal emails and phone numbers redacted).
  - Submission: `POST /api/reports`.
  - Storage: PostgreSQL table `citizen_reports` (with fallback to thread-safe multi-store JSON cache).

---

### View 9: Vulnerability Index & District Matrix (`#view-ranking`)
- **What is showing**:
  - Comprehensive vulnerability scoreboard for all **14 administrative districts of Kerala**.
  - Sorted rankings by overall vulnerability score (0 to 100):
    - *Wayanad* (Score 94 - High Landslide Risk)
    - *Idukki* (Score 91 - High Orographic & Slope Risk)
    - *Alappuzha* (Score 89 - Sub-sea-level Flood Basin)
    - *Ernakulam, Pathanamthitta, Thrissur, etc.*
  - Detailed metrics per district: Total revenue villages, flood-prone villages, landslide-prone villages, mean slope in degrees, drainage density, and major draining rivers.
  - Quick action to zoom to any district on the GIS map.
- **Where data comes from**:
  - Endpoint: `GET /api/kerala/baseline`.
  - Database: PostgreSQL table `districts` (fallback `backend/app/data/districts.json`).
  - Source Authorities: **KSDMA District Disaster Management Plans (DDMP)**, **State Hazard Vulnerability Risk Assessment (HVRA)**, and **Census of India**.

---

### View 10: State Emergency Operations Centre Admin Portal (`#view-admin`)
- **What is showing**:
  - Restricted operational console for disaster management personnel and district administrators.
  - Access controlled via administrative authentication and Master Secret Key (`VIP@DUK`).
  - **Live Incident Moderation Table**: Full access to all raw incident reports, including contact email, GPS coordinates, and photographic evidence.
  - **Action Controls**:
    - Update triage status: Move incident from *Under Review* to *Verified*, *Action Initiated*, or *Resolved*.
    - Delete spam or invalid submissions.
  - **Multi-Tier Database User Ledger**:
    - Live inspection of registered users across Administrator, Officer, and Citizen tiers.
    - Synchronized live telemetry showing PostgreSQL connection health and JSON multi-storage status.
- **Where data comes from**:
  - Authentication: `POST /api/auth/login` and `POST /api/admin/verify-key` (verified using timing-safe `hmac.compare_digest`).
  - Full reports feed: `GET /api/admin/reports`.
  - User ledger: `GET /api/admin/users`.
  - Status updates: `PATCH /api/admin/reports/{id}/status`.
  - Deletions: `DELETE /api/admin/reports/{id}`.

---

### View 11: About Jal Taranga & Core Team Showcase (`#view-about`)
- **What is showing**:
  - Project vision, institutional acknowledgments, and development context.
  - Scientific citations: KSDMA, GSI, NCESS, CWRDM, NRSC/ISRO Bhuvan, Survey of India, and MERIT-Hydro.
  - **Team Roster & Core Members Showcase**:
    - Uniform, elegant profile cards honoring all 6 core team contributors with clean initials and designation badges:
      - **Femin Johny** — Team Leader & Project Lead
      - **Rajana Jyothirmayi** — Core Team & Researcher
      - **Gayathry S R** — Core Team & Researcher
      - **Priyadarsan G P** — Core Team & Engineer
      - **M.Aqeeb Baba** — Core Team & Engineer
      - **Bijay Thomas** — Core Team & Developer
- **Where data comes from**: Static layout and local storage logic in `frontend/index.html` and `frontend/js/app.js`.

---

## 4. Master Data Provenance & Fetching Matrix

| Data Element | Real-World Source / Agency | Retrieval Path / Backend Endpoint | Implementation File | Fallback / Offline Behavior |
|---|---|---|---|---|
| **14 Kerala Districts** (Vulnerability, Villages, Slope, Centroids) | **KSDMA** State Hazard Atlas & **Census of India** administrative boundaries | `GET /api/kerala/baseline` $\to$ `get_districts()` | `backend/app/core/database.py` & `data_loader.py` | Reads from `backend/app/data/districts.json` if PostgreSQL is unavailable. |
| **44 River Basins** (Boundaries, Catchment Area, Discharge, Bottlenecks) | **NCESS** & **CWRDM** Kerala River Basins Atlas (41 west-flowing, 3 east-flowing) | `GET /api/kerala/baseline` $\to$ `get_watersheds()` | `backend/app/core/database.py` & `data_loader.py` | Reads from `backend/app/data/watersheds.json`. |
| **DEM Lowland Depressions** (Kuttanad, Aluva, Kole Wetlands) | **CartoDEM 30m / SRTM Hydro-corrected DEM** & **2018 Kerala Flood Inundation Extents** | `GET /api/kerala/baseline` $\to$ `get_inundation_zones()` | `backend/app/core/data_loader.py` | Built-in high-precision geodetic boundary coordinates. |
| **Landslide Hazard Scarps** (Chooralmala, Meppadi, Pettimudi, Kavalappara) | **GSI (Geological Survey of India)** Landslide Susceptibility Atlas & **NCESS** | `GET /api/landslides/hazards` $\to$ `get_landslide_zones()` | `backend/app/core/data_loader.py` | Static calibrated Western Ghats escarpment registry. |
| **Taylor Infinite Slope Stability** (Factor of Safety, Shear Stress/Strength) | Limit-Equilibrium Geotechnical Soil Mechanics Equation | `POST /api/landslides/simulate-slope` | `backend/app/api/geospatial.py` | Pure deterministic physics calculation executed in Python memory. |
| **Rainfall Accumulation & Overland Velocity** | **SCS Runoff Curve Number (USDA-NRCS)** & Rational Runoff Equation | `POST /api/dem/accumulation` | `backend/app/services/hydrology.py` | Calibrated numerical solver in Python memory. |
| **Watershed Catchment Delineation** | **MERIT-Hydro / MERIT-Basins** Megabasin 45 (South Asia, ~90m hydro-conditioned DEM by Dr. Dai Yamazaki) | `POST /api/watershed/delineate` | `backend/app/services/delineation.py` | **Instant Synthesis Fallback**: If the 950MB South Asia DB is absent or downloading, `synthesize_kerala_catchment()` computes the upstream polygon and stream reaches in $<25\text{ ms}$. |
| **Multi-Spectral Satellite Imagery** | **Esri World Imagery MapServer REST API** & **Sentinel-2 L2A / Landsat-9** | `GET /api/srishti/satellite-crop` | `backend/app/api/srishti.py` | Dynamic export via HTTP request; converts RGB to VARI/NDVI using NumPy; falls back to pre-rendered Sentinel-2 files in `frontend/images/watershed/`. |
| **Bhuvan SRISHTI & DRISHTI Assets** | **ISRO / NRSC Bhuvan Portal** & **PMKSY-WDC (IWMP)** Watershed Registry | `GET /api/srishti/assets` & `POST /api/srishti/assets` | `backend/app/data/srishti_assets.json` | Local thread-safe JSON registry with 16 pre-seeded verified structures. |
| **AI Watershed Mitigation Plan** | **Google Gemini 2.5 Flash** Multimodal Remote Sensing Inference | `POST /api/watershed/ai-plan` | `backend/app/services/gemini.py` | **7-Zone Microterrain Solver**: If `GEMINI_API_KEY` is not provided or quota fails, automatically falls back to calibrated deterministic models across 7 Kerala physiographic zones. |
| **Statutory Protected Landmarks** (Airports, Ports, Dams, Technopark) | **AAI**, **DGCA**, **Cochin Port Authority**, **KSDMA** Statutory Zoning | Checked during `POST /api/watershed/ai-plan` | `backend/app/services/hydrology.py` & `landmarks.json` | Enforces regulatory shield preventing heavy landscape earthworks on strategic national infrastructure. |
| **Place Search & Geocoding** | **OpenStreetMap Nominatim Geocoder** | Client-side fetch in `frontend/js/app.js` | `frontend/js/app.js` (`searchLocation`) | Filtered strictly to Kerala bounding box `viewbox=74.80,12.85,77.60,8.15&bounded=1`. |
| **Citizen Hazard Reports** | Crowdsourced Ground-Truth Telemetry from Citizen Field Observers | `GET /api/reports` & `POST /api/reports` | `backend/app/core/database.py` & `data_loader.py` | Stored in PostgreSQL `citizen_reports` table; falls back to in-memory store; emails encrypted before public display. |
| **Admin Authentication & Triage** | State Disaster Management Administrative Credentials | `POST /api/admin/verify-key` | `backend/app/core/security.py` | Constant-time HMAC comparison against `ADMIN_SECRET_KEY` (`VIP@DUK`). |

---

## 5. Mathematical Formulations & Hydrological Solvers

### 1. Taylor Infinite Slope Stability Equation (Landslides)
Used in `backend/app/api/geospatial.py` to evaluate slope failure risk in the Western Ghats:

$$\text{FS} = \frac{c' + (\gamma_{\text{soil}} \cdot z - m \cdot \gamma_{\text{water}} \cdot z) \cos^2\beta \cdot \tan\phi'}{\gamma_{\text{soil}} \cdot z \cdot \sin\beta \cdot \cos\beta}$$

Where:
- $c' = c_{\text{soil}} + c_{\text{root}}$ (Effective cohesion: base soil cohesion + biological root cohesion).
- $\gamma_{\text{soil}} = 18.5\text{ kN/m}^3$ (Unit weight of regolith soil).
- $\gamma_{\text{water}} = 9.81\text{ kN/m}^3$ (Unit weight of water).
- $z$ = Regolith soil mantle depth (meters).
- $\beta$ = Slope inclination angle (radians).
- $\phi'$ = Effective internal friction angle of soil (radians).
- $m$ = Saturation fraction of the soil column ($0.0$ to $1.0$).

### 2. Surface Water Accumulation Volume (Flooding)
Used in `backend/app/services/hydrology.py`:

$$V_{\text{acc}} = \left( A_{\text{basin}} \times \frac{P}{1000} \times C \right) \times 0.48 \times M_{\text{surge}}$$

Where:
- $A_{\text{basin}}$ = Basin drainage area in $\text{km}^2$.
- $P$ = Precipitation intensity ($\text{mm/h}$).
- $C$ = Calibrated runoff coefficient ($0.45$ for Moderate, $0.78$ for High, $0.95$ for Extreme).
- $M_{\text{surge}}$ = Hydrograph surge multiplier ($1.0$ to $4.5$).

### 3. Geodetic Distance (Haversine Formula)
Used for landmark proximity checks and place searches:

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

Where $R = 6,371\text{ km}$, $\phi$ is latitude, and $\lambda$ is longitude.

---

## 6. Zero-Downtime Reliability & Fail-Safe Architecture

Jal Taranga is engineered so that **no external network outage or missing API key can cause the application to crash**:

1. **Database Resilience**:
   - Live PostgreSQL + PostGIS queries are attempted first.
   - If PostgreSQL is offline, `data_loader.py` seamlessly falls back to thread-safe local JSON files (`districts.json`, `watersheds.json`, `landmarks.json`, `srishti_assets.json`).
2. **AI Engine Fallback**:
   - If `GEMINI_API_KEY` is present, Google Gemini 2.5 Flash analyzes the snipped landscape.
   - If missing or quota is exhausted, the backend executes the deterministic **7-Zone Microterrain Hydrological Solver** calibrated to Kerala's physiography.
3. **Catchment Delineation Fallback**:
   - If the 950 MB South Asia MERIT-Basins dataset is present, it computes topological stream snapping.
   - If absent or downloading, `synthesize_kerala_catchment()` synthesizes exact catchment boundaries and tributary networks in $<25\text{ ms}$.
4. **Satellite Imagery Fallback**:
   - If the live Esri World Imagery REST export times out, pre-processed multi-spectral Sentinel-2 crops in `frontend/images/watershed/` are served instantly.
5. **Security & Privacy**:
   - Administrative endpoints use timing-safe comparison (`hmac.compare_digest`) against `ADMIN_SECRET_KEY` (`VIP@DUK`).
   - Citizen field report submitter emails are never exposed to public feeds.
   - Critical national infrastructure (Airports, Ports, Dams) is protected by statutory spatial geofences preventing destructive terrain modification plans.
