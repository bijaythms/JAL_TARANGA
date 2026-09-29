# Jal Taranga — Kerala Geospatial Watershed & Hydro-Disaster Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B%20PostGIS%203.5-336791?logo=postgresql&logoColor=white)](https://postgis.net/)
[![Leaflet](https://img.shields.io/badge/Leaflet-v1.9.4-199900?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3.4-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CRS](https://img.shields.io/badge/CRS-EPSG%3A32643%20(UTM%2043N)-cyan)]()
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?logo=google&logoColor=white)](https://ai.google.dev/)
[![ISRO Bhuvan](https://img.shields.io/badge/ISRO%20Bhuvan-SRISHTI%20%7C%20DRISHTI-green)](https://bhuvan.nrsc.gov.in/)

> **"Rise Above Risk. Protect Kerala. From Data to Decisions. From Risk to Resilience."**  
> Engineered by **VISIONQUEST**

---

## 📑 Table of Contents

1. [🌍 Overview & Mission](#-1-overview--mission)
2. [🏗️ High-Level System Architecture](#️-2-high-level-system-architecture)
3. [🔄 Master End-to-End Workflow](#-3-master-end-to-end-workflow)
4. [👥 Role-Based Workflows & User Lifecycles](#-4-role-based-workflows--user-lifecycles)
   - [Citizen Workflow](#41-citizen-workflow-ground-incident-reporting)
   - [Field Officer & Analyst Workflow](#42-field-officer--hydrologist-workflow-operational-intelligence)
   - [Administrator & SEOC Commander Workflow](#43-administrator--seoc-commander-workflow-triage--governance)
5. [🔬 Core Disaster Engineering Workflows](#-5-core-disaster-engineering-workflows)
   - [Dynamic Watershed Catchment Delineation](#51-dynamic-watershed-catchment-delineation-workflow)
   - [Rainfall Accumulation & Inundation Modeling](#52-hydro-meteorological-inundation--rainfall-simulation-workflow)
   - [Geotechnical Slope Stability & Landslide Forecasting](#53-western-ghats-geotechnical-slope-stability-workflow)
   - [Multi-Spectral Satellite Earth Observation](#54-multi-spectral-satellite-earth-observation-workflow)
   - [Multimodal AI Mitigation Planning & 7-Zone Microterrain Solver](#55-ai-multimodal-watershed-mitigation-plan-workflow)
6. [🗺️ The 11 Application Workspaces](#️-6-the-11-application-workspaces)
7. [💾 Database Architecture & Multi-Storage Synchronization](#-7-database-architecture--multi-storage-synchronization)
8. [📐 Mathematical & Scientific Formulations](#-8-mathematical--scientific-formulations)
9. [📁 Project Directory Structure](#-9-project-directory-structure)
10. [🚀 Quick Start & Local Setup](#-10-quick-start--local-setup)
11. [🐳 Docker Deployment](#-11-docker-deployment)
12. [📡 REST API Reference](#-12-rest-api-reference)
13. [🧪 Automated Test Suite & Verification](#-13-automated-test-suite--verification)
14. [👥 Team & Credits](#-14-team--credits)

---

## 🌍 1. Overview & Mission

**Jal Taranga** is an advanced Earth-observation, hydrological modeling, and disaster intelligence decision-support platform engineered specifically for the state of **Kerala, India**.

### Why Kerala Needs Jal Taranga
Kerala is uniquely vulnerable to climate-induced hydro-meteorological catastrophes:
- **44 River Basins**: Traversing steep gradients from the Western Ghats (up to 2,695 m MSL at Anamudi) to the Arabian Sea within just 60 to 120 kilometers.
- **Extreme Orographic Monsoons**: Annual precipitation between 2,500 mm to over 5,000 mm, causing rapid flood peaks and dangerously short basin times of concentration.
- **Landslide Susceptibility**: Thick saprolite regolith on steep slopes subjected to pore-pressure liquefaction upon sustained rainfall (>180 mm/24 h), as witnessed in Meppadi/Chooralmala (Wayanad), Pettimudi (Munnar), and Kavalappara (Malappuram).
- **Lowland Depression & Tidal Bottlenecks**: Sub-sea-level agrarian polder basins like **Kuttanad** (-1.5 m to +1.5 m MSL) and estuarine urban centers like **Greater Kochi** where river discharge meets high astronomical ocean tides.

Jal Taranga provides government authorities, disaster managers, hydro-engineers, and citizens with a unified **digital twin**: combining real-time multi-spectral satellite imagery, 30-meter hydro-corrected elevation models, deterministic physics equations, Google Gemini 2.5 AI remote sensing, and crowdsourced ground-truth telemetry.

---

## 🏗️ 2. High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND CLIENT (Leaflet + Tailwind)                      │
│   • Responsive Glassmorphic Dashboard        • Leaflet GIS v1.9.4 Mapping Engine       │
│   • Chart.js Dynamic Hydrographs            • Transparent Fetch Proxy Interceptor      │
│   • Role-Based Guarded Routing               • Pure White Full-Screen Scenic Portal    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP / REST & GeoJSON
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                             BACKEND CORE (FastAPI / Python 3.12)                       │
│   • /api/auth       (Role-scoped auth, live store status, multi-storage synchronization)│
│   • /api/geospatial (Baselines, DEM Accumulation, Slope FoS, AI Snip, Delineation)     │
│   • /api/srishti    (ISRO Bhuvan SRISHTI/DRISHTI multi-spectral assets & crops)        │
│   • /api/reports    (Crowdsourced field telemetry with server-side email encryption)   │
│   • /api/admin      (Timing-safe HMAC authenticated incident triage & user ledger)     │
└─────────────────────┬───────────────────────────────────────────────┬──────────────────┘
                      │                                               │
┌─────────────────────▼───────────────────────┐ ┌─────────────────────▼──────────────────┐
│         COMPUTATIONAL ENGINES               │ │              STORAGE & APIS            │
│  • Micro-Terrain 7-Zone Hydrology Solver    │ │  • PostgreSQL 16 + PostGIS Spatial DB  │
│  • Taylor Infinite Slope Stability Solver   │ │  • Thread-Safe JSON Fallback Stores    │
│  • SCS Curve Number Runoff Accumulator      │ │  • Esri World Imagery REST Server      │
│  • MERIT-Basins Hydro Catchment Engine      │ │  • OpenStreetMap Nominatim Geocoder    │
│  • Google Gemini 2.5 Flash Remote Sensing   │ │  • ISRO Bhuvan PMKSY-WDC Registry      │
│  • Multi-Spectral VARI/NDVI Band Processor  │ │  • Statutory Protected Landmark Shield │
└─────────────────────────────────────────────┘ └────────────────────────────────────────┘
```

---

## 🔄 3. Master End-to-End Workflow

The diagram below illustrates the complete operational data flow across client sessions, backend services, external APIs, and the PostgreSQL storage layer:

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Citizen / Officer / Admin)
    participant Client as Web Frontend (Leaflet/Tailwind)
    participant Proxy as Fetch Proxy Interceptor
    participant API as FastAPI Gateway (:8000)
    participant Engine as Physics & AI Engines
    participant DB as PostgreSQL 16 + PostGIS (vellam_db)
    participant External as External Satellite & Tile APIs

    %% Session Initialization
    User->>Client: Open Platform (http://127.0.0.1:8000)
    Client->>Proxy: GET /health & /api/kerala/baseline
    Proxy->>API: Route HTTP Request
    API->>DB: Query 14 Districts & 44 River Basins
    DB-->>API: GeoJSON Features + PostGIS Geometry
    API-->>Client: Baseline Spatial Data
    Client->>External: Load Esri / Google Hybrid Imagery
    External-->>Client: 256x256 Satellite Tile Grid

    %% Role Authentication
    User->>Client: Authenticate (Officer / Citizen / Admin)
    Client->>API: POST /api/auth/login or /api/admin/verify-key
    API->>DB: Verify Credentials against Role Tables
    DB-->>API: User Record & Role Clearance Token
    API-->>Client: Session Object (Role, Name, District)
    Client->>Client: Apply Role-Based Navigation Filter & Route Landing Tab

    %% Operational Action Example: Delineation & AI Plan
    opt Spatial Delineation & Simulation
        User->>Client: Click Map Pour Point / Drag Snip Box
        Client->>API: POST /api/watershed/delineate or /ai-plan
        API->>Engine: Run MERIT-Basins / 7-Zone Microterrain Solver
        Engine-->>API: Upstream Boundary Polygon + Interventions
        API-->>Client: Render Vector Delineation & Conservation Report
    end

    %% Field Telemetry Example: Citizen Hazard Reporting
    opt Ground Incident Submission
        User->>Client: Submit Incident (GPS, Category, Evidence Photo)
        Client->>API: POST /api/reports
        API->>DB: Insert into citizen_reports (geom Point)
        DB-->>API: Persisted Report ID
        API-->>Client: Real-Time Submission Confirmation
    end
```

---

## 👥 4. Role-Based Workflows & User Lifecycles

Jal Taranga implements strict role-based access control (RBAC). Upon login, the interface filters sidebar items, profile actions, and access permissions:

```mermaid
graph TD
    A[User Arrives at Login Portal] --> B{Select Role Tier}
    
    %% Citizen Path
    B -->|Citizen| C[Citizen Sign In / Register]
    C --> D[Land on Ground Reports]
    D --> D1[Submit Geotagged Hazard]
    D --> D2[Browse Community Alerts Feed]
    D --> D3[Track Incident Resolution Status]
    
    %% Officer Path
    B -->|Officer / Analyst| E[Officer Sign In]
    E --> F[Land on GIS Overview]
    F --> F1[GIS Command Centre & Layer Toggles]
    F --> F2[Upstream Catchment Delineation]
    F --> F3[Rainfall Runoff Accumulation Simulation]
    F --> F4[Satellite Earth-Observation NDVI/NDWI]
    F --> F5[Taylor Slope Stability Landslide Modeling]
    F --> F6[Watershed Conservation Intervention Lab]
    
    %% Admin Path
    B -->|Admin| G[Admin Secret Clearance VIP@DUK]
    G --> H[Land on Admin Command Centre]
    H --> H1[Incident Moderation & Triage Queue]
    H --> H2[Live Database User Ledger]
    H --> H3[System Health & Emergency Overrides]
    H --> H4[Home Overview Access]
```

### 4.1 Citizen Workflow: Ground Incident Reporting
1. **Access**: Citizen logs in or registers a new account (specifying Name, Email, Phone, District, Username, Password). Data is saved directly to PostgreSQL `citizens` and synced with `citizens.json`.
2. **Landing**: Automatically lands on **Reports & Insights** (`#nav-community`). Disallowed operations tabs are completely hidden from the sidebar.
3. **Incident Creation**:
   - Captures GPS coordinates automatically using browser geolocation or map pin.
   - Selects disaster type (*Landslide / Slope Failure*, *Flood / Water Accumulation*, *River Spillover*, *Blocked Culvert*).
   - Uploads photographic proof from the field.
   - Provides on-ground observations.
4. **Privacy Protection**: The citizen's email is encrypted on the server before public listing.
5. **Tracking**: Citizen monitors the public live feed to observe status transitions (*Under Review* &rarr; *Verified* &rarr; *Action Initiated* &rarr; *Resolved*).

### 4.2 Field Officer & Hydrologist Workflow: Operational Intelligence
1. **Access**: Officers log in using assigned department credentials.
2. **Landing**: Lands on **Home** (`#nav-home`) with full GIS and watershed modeling permissions.
3. **Interactive Delineation**:
   - Clicks any pour point on a stream in the **GIS Command Centre** (`#view-gis`).
   - The engine computes the complete upstream contributing catchment area and tributary stream order in $<25	ext{ ms}$.
4. **Hydro-Meteorological Stress Testing**:
   - Switches to **Rain Simulator** (`#view-simulator`).
   - Selects a river basin and simulates *Moderate (25 mm/h)*, *High (60 mm/h)*, or *Extreme (130 mm/h)* storms.
   - Analyzes peak runoff volume (MCM), inundated hectares, and discharge hydrographs.
5. **Western Ghats Landslide Analysis**:
   - Opens **Erosion & Landslides** (`#view-landslides`).
   - Adjusts Taylor Infinite Slope parameters (slope angle, regolith depth, saturation, biological root cohesion).
   - Generates real-time Factor of Safety (FS) curves to identify failure thresholds.
6. **Watershed Planning**:
   - Uses **Intervention Lab** (`#view-intervention`) to simulate structural measures (check dams, contour bunds, percolation ponds, riparian afforestation).
   - Evaluates runoff reduction %, soil loss prevented (tons/ha), and cost estimates (INR).

### 4.3 Administrator & SEOC Commander Workflow: Triage & Governance
1. **Access**: Authenticates with SEOC clearance key (`VIP@DUK`) or Admin credentials.
2. **Landing**: Directly accesses the **Admin Operations Console** (`#view-admin`) with additional access to **Home** (`#view-home`).
3. **Incident Triage & Verification**:
   - Reviews unredacted citizen submissions, inspecting high-resolution photographic evidence and accurate GPS coordinates.
   - Updates report status:
     - `Under Review` $	o$ Initial triage.
     - `Verified` $	o$ Field personnel dispatched.
     - `Action Initiated` $	o$ KSDMA/Fire & Rescue intervention underway.
     - `Resolved` $	o$ Hazard cleared and water receding.
   - Deletes false alarms, spam, or invalid submissions.
4. **User Ledger Governance**:
   - Inspects the live **PostgreSQL Database Users Ledger** showing User ID, Name, Username, Role, District, and Target Table across all tiers.
   - Monitors live connection state to PostgreSQL `vellam_db`.

---

## 🔬 5. Core Disaster Engineering Workflows

### 5.1 Dynamic Watershed Catchment Delineation Workflow
```mermaid
flowchart LR
    A[User Map Pour Point Click] --> B{MERIT-Basins 90m DB Available?}
    B -->|Yes| C[Trace Hydrological Upstream Graph]
    B -->|No / Downloading| D[Execute Instant Synthetic Delineator]
    D --> E[Compute Upstream Convex Hull & Ridge Stream Reaches]
    C --> F[Format GeoJSON FeatureCollection]
    E --> F
    F --> G[Render Boundary & Tributaries on Leaflet Map]
    F --> H[Calculate Basin Area km² & Time of Concentration]
```
- **Backend Service**: `backend/app/services/delineation.py`
- **Algorithm**: Topographic flow accumulation tracking based on MERIT-Hydro. If the 950 MB South Asia dataset is unindexed, the engine activates `synthesize_kerala_catchment()` to ensure zero client latency.

### 5.2 Hydro-Meteorological Inundation & Rainfall Simulation Workflow
```mermaid
flowchart TD
    A[Select Basin & Rainfall Scenario] --> B[Retrieve Basin Area km² & Hydrologic Group]
    B --> C[Compute Runoff Volume: SCS Curve Number Formulation]
    C --> D[Apply Hydrograph Surge Multiplier: 1.0 to 4.5x]
    D --> E[Compute Peak Overland Velocity: Manning Equation]
    E --> F[Calculate Inundated Footprint: Hectares]
    F --> G[Generate Chart.js Precipitation vs Discharge Hydrograph]
```
- **Backend Service**: `backend/app/services/hydrology.py` (`compute_water_accumulation`)
- **Key Equation**:
  $$V_{	ext{acc}} = \left( A_{	ext{basin}} 	imes rac{P}{1000} 	imes C ight) 	imes 0.48 	imes M_{	ext{surge}}$$

### 5.3 Western Ghats Geotechnical Slope Stability Workflow
```mermaid
flowchart TD
    A[Input Slope Angle β, Saturation m, Depth z] --> B[Compute Total Cohesion: c_soil + c_root]
    B --> C[Compute Effective Normal Stress on Failure Plane]
    C --> D[Compute Mobilized Shear Stress: Gravity Driving Force]
    D --> E[Solve Taylor Limit-Equilibrium Factor of Safety FS]
    E --> F{FS Evaluation}
    F -->|FS < 1.0| G[CRITICAL FAILURE IMMINENT: Red Alert Warning]
    F -->|1.0 <= FS <= 1.3| H[QUASI-STABLE: Watch Warning & Evacuation Alert]
    F -->|FS > 1.3| I[GEOTECHNICALLY STABLE: Low Immediate Risk]
```
- **Backend Service**: `backend/app/api/geospatial.py` (`simulate_slope`)
- **Formula**:
  $$	ext{FS} = rac{c' + (\gamma_{	ext{soil}} \cdot z - m \cdot \gamma_{	ext{water}} \cdot z) \cos^2eta \cdot 	an\phi'}{\gamma_{	ext{soil}} \cdot z \cdot \sineta \cdot \coseta}$$

### 5.4 Multi-Spectral Satellite Earth Observation Workflow
```mermaid
flowchart LR
    A[Select Target Lat/Lng & Asset] --> B[Fetch Esri World Imagery REST Tile Grid]
    B --> C[Decode RGB Bands in NumPy Memory]
    C --> D[Calculate Visible Atmospherically Resistant Index: VARI]
    D --> E[Map VARI to Calibrated NDVI: -1.0 to +1.0]
    E --> F[Apply Color Ramp: Brown to Lush Green]
    F --> G[Render False-Color Vegetative Canopy Overlay]
```
- **Backend Service**: `backend/app/api/srishti.py` (`get_satellite_crop`)
- **VARI Formulation**:
  $$	ext{VARI} = rac{ho_{	ext{Green}} - ho_{	ext{Red}}}{ho_{	ext{Green}} + ho_{	ext{Red}} - ho_{	ext{Blue}}}$$

### 5.5 AI Multimodal Watershed Mitigation Plan Workflow
```mermaid
flowchart TD
    A[Snip Bounding Box on GIS Map] --> B{Statutory Protected Landmark Check}
    B -->|Within Proximity Zone| C[Trigger Regulatory Shield: Restrict Excavation]
    B -->|Clear Zone| D{Gemini 2.5 API Key Configured?}
    D -->|Yes| E[Execute Google Gemini 2.5 Flash Remote Sensing Inference]
    D -->|No / Quota Limit| F[Execute Deterministic 7-Zone Microterrain Solver]
    E --> G[Generate Structured Mitigation Plan]
    F --> G
    G --> H[Output GeoJSON Structures, Runoff Reduction %, Cost Estimate]
```
- **Backend Service**: `backend/app/services/gemini.py` & `hydrology.py`
- **7 Physiographic Zones**: Coastal Alluvium, Kuttanad Polders, Midland Laterite, Foothills, High Ranges, Palakkad Gap, Wayanad Plateau.

---

## 🗺️ 6. The 11 Application Workspaces

| # | Workspace View | DOM Element | Primary Functions & Displayed Data |
|---|---|---|---|
| 0 | **Scenic Auth Portal** | `#view-login` | Full-screen scenic portal on initial link load; segregated dual-tier authentication (Admin/Officer with Secret PIN vs Citizen with Phone/Email); Citizen registration modal with instant redirection to manual sign-in; role-based navigation shielding. |
| 1 | **Home & Overview** | `#view-home` | State disaster overview, real-time hazard matrix, quick access module launchers, recent alerts bulletin, and statewide hydrological metrics. |
| 2 | **GIS Command Centre** | `#view-gis` | High-precision Leaflet satellite basemap; **7-Pill Floating Map Dock** (`Focus`, `Tools`, `Legends`, `Layers`, `Telemetry`, `Details`, `Full`); Point-and-Click MERIT-Basins catchment delineator; Bounding-Box AI Snip Tool with Gemini 2.5 Flash; Statutory landmark protection shield (airports, dams, ports); Kerala-bounded OSM Nominatim search. |
| 3 | **Intervention Lab** | `#view-intervention` | Watershed conservation engineering (**Check Dams, Contour Bunding, Percolation Ponds, Riparian Afforestation, Staggered Trenches**); coupled physics simulation (peak runoff reduction %, groundwater recharge MCM, soil retention tons/ha); Civil Bill of Quantities (BoQ) and MGNREGS wage/material budgeting. |
| 4 | **Inundation Simulator** | `#view-inundation` | Hydrodynamic flood inundation simulation with variable precipitation sliders (50 mm/h to 300 mm/h); Digital Elevation Model (DEM) depression pooling across critical lowlands (**Kuttanad Polders, Aluva/Periyar Basin, Kole Wetlands**); animated surface water spread and breach propagation. |
| 5 | **Satellite Earth-Obs** | `#view-satellite` | Multi-spectral remote sensing aligned with **ISRO Bhuvan SRISHTI & DRISHTI**; spectral indices (**True Color RGB, NDVI Canopy, NDWI Water, NBR Scarp**); dynamic satellite image crop with NDVI false-color rendering; DRISHTI Mobile Terminal Asset Geotagger with compass azimuth dial and elevation MSL. |
| 6 | **Erosion & Landslides 3D** | `#view-landslides` | Western Ghats landslide scarps (Chooralmala, Meppadi, Pettimudi, Kavalappara); **Dual 2D Leaflet and 3D MapLibre Elevation Terrain Viewer**; real-time Taylor Infinite Slope Factor of Safety (FS) physics calculator; Revised Universal Soil Loss Equation (RUSLE/USLE) soil erosion calculator. |
| 7 | **Rainfall Runoff Simulator** | `#view-simulator` | Dynamic cloudburst simulation across Moderate (25 mm/h), High (60 mm/h), and Extreme (130 mm/h) storm scenarios; basin runoff accumulation in Million Cubic Meters (MCM); inundated surface footprint (hectares); peak flow velocity (m/s); Chart.js dual-wave hydrograph curves. |
| 8 | **Community Field Reports** | `#view-community` | Citizen participatory hazard reporting (landslides, floods, culvert blockages, river breaches); live GPS location pinning; client-side EXIF GPS extraction from uploaded disaster photos; public sanitized incident ledger with server-side email/phone redaction. |
| 9 | **Vulnerability Rankings** | `#view-ranking` | Composite Disaster Vulnerability Index (CDVI) ranking matrix for all **14 administrative districts of Kerala**; detailed breakdown of revenue villages, flood-prone villages, landslide-prone villages, mean slope, and drainage density. |
| 10 | **Admin Operations & Triage** | `#view-admin` | Authenticated command console for disaster management officials; live incident triage (*Under Review*, *Verified*, *Action Initiated*, *Resolved*); emergency team dispatch; live PostgreSQL database user ledger across Administrator, Officer, and Citizen tiers with multi-store sync telemetry. |
| 11 | **About & Scientific Provenance** | `#view-about` | Platform mission, institutional acknowledgments, scientific citations (KSDMA, GSI, NCESS, CWRDM, ISRO Bhuvan), and uniform **Team Roster & Core Members Showcase**. |

---

## 💾 7. Database Architecture & Multi-Storage Synchronization

Jal Taranga operates with a dual-layer storage strategy combining an enterprise **PostgreSQL 16 + PostGIS 3.5** spatial engine (`vellam_db`) with local, thread-safe JSON caches.

```
                  ┌─────────────────────────────────────────┐
                  │          FastAPI Data Layer             │
                  └──────────────┬──────────────────┬───────┘
                                 │                  │
        ┌────────────────────────▼────────┐ ┌───────▼─────────────────────────┐
        │  PostgreSQL 16 + PostGIS DB     │ │  Thread-Safe Local JSON Caches   │
        │  Database: vellam_db            │ │  (Real-Time Auto-Synchronized)   │
        ├─────────────────────────────────┤ ├──────────────────────────────────┤
        │ • officers                      │ │ • backend/app/data/citizens.json │
        │ • citizens                      │ │ • backend/app/data/users.json    │
        │ • administrators                │ │ • backend/app/data/districts.json│
        │ • citizen_reports (geom Point)  │ │ • backend/app/data/watersheds.json│
        │ • districts (geom Polygon)      │ │ • backend/app/data/srishti_assets│
        │ • river_basins (geom Polygon)   │ └──────────────────────────────────┘
        │ • users (Unified SQL View)      │
        └─────────────────────────────────┘
```

### PostgreSQL Tables in `vellam_db`
1. **`officers`**: Emergency officers, GIS analysts, hydrologists.
2. **`citizens`**: Registered citizens, community observers, field volunteers.
3. **`administrators`**: State Emergency Operations Center (SEOC) command personnel.
4. **`citizen_reports`**: Geotagged ground hazard incidents with PostGIS spatial geometry (`geom` Point).
5. **`districts`**: 14 Kerala administrative boundaries with PostGIS spatial geometry (`geom` Polygon) and vulnerability indices.
6. **`river_basins`**: 44 Kerala river catchments with PostGIS spatial geometry (`geom` Polygon) and hydrological parameters.
7. **`users` (SQL View)**: Permanent unified view joining `citizens`, `officers`, and `administrators` with a unified `tier` column.

### Transparent Fetch Proxy Interceptor
To eliminate CORS and network errors when opening the frontend from alternative origins (such as VS Code Live Server on `http://127.0.0.1:5500` or local `file://`), `frontend/js/app.js` features an automatic transparent proxy interceptor that routes all `/api/...` requests directly to `http://127.0.0.1:8000`.

---

## 📐 8. Mathematical & Scientific Formulations

### 1. Taylor Infinite Slope Stability Equation (Landslides)
Used in `backend/app/api/geospatial.py` to evaluate slope failure risk in the Western Ghats:
$$\text{FS} = \frac{c' + (\gamma_{\text{soil}} \cdot z - m \cdot \gamma_{\text{water}} \cdot z) \cos^2\beta \cdot \tan\phi'}{\gamma_{\text{soil}} \cdot z \cdot \sin\beta \cdot \cos\beta}$$

Where:
- $c' = c_{\text{soil}} + c_{\text{root}}$ (Effective cohesion: base soil cohesion + biological root anchoring).
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

---

## 📁 9. Project Directory Structure

```
d:/ppppr/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin.py            # Administrative incident moderation & user ledger
│   │   │   ├── auth.py             # Role authentication, session check & store telemetry
│   │   │   ├── geospatial.py       # Baseline GIS, DEM accumulation, slope stability, delineation
│   │   │   ├── intervention.py     # Watershed conservation simulation endpoints
│   │   │   ├── reports.py          # Citizen crowdsourced field telemetry endpoints
│   │   │   └── srishti.py          # ISRO Bhuvan SRISHTI/DRISHTI multi-spectral assets
│   │   ├── core/
│   │   │   ├── config.py           # Application settings & environment variables
│   │   │   ├── data_loader.py      # Spatial GeoJSON loader & in-memory fallbacks
│   │   │   ├── database.py         # PostgreSQL 16 + PostGIS connection pool
│   │   │   ├── security.py         # Timing-safe HMAC authentication & key hashing
│   │   │   └── user_store.py       # Multi-storage user management (Postgres + JSON sync)
│   │   ├── data/                   # Static GeoJSON and JSON fallback datasets
│   │   │   ├── citizens.json       # Auto-synced citizen credentials cache
│   │   │   ├── districts.json      # 14 Kerala districts & vulnerability metadata
│   │   │   ├── landmarks.json      # Statutory protected infrastructure coordinates
│   │   │   ├── srishti_assets.json # ISRO Bhuvan monitored watershed structures
│   │   │   ├── users.json          # Auto-synced all-tier credentials cache
│   │   │   └── watersheds.json     # 44 Kerala river basin boundaries & hydrology
│   │   ├── services/
│   │   │   ├── delineation.py      # MERIT-Basins & synthetic catchment delineation engine
│   │   │   ├── gemini.py           # Google Gemini 2.5 Flash multimodal remote sensing
│   │   │   └── hydrology.py        # 7-zone microterrain solver & SCS-CN calculator
│   │   └── main.py                 # FastAPI application entrypoint & static mounting
│   ├── tests/
│   │   ├── test_api.py             # Geospatial and simulation endpoint unit tests
│   │   ├── test_auth.py            # Role authentication, login, and registration tests
│   │   ├── test_delineation.py     # Catchment delineation validation tests
│   │   └── test_hydrology.py       # Soil mechanics & runoff equation verification tests
│   ├── Dockerfile                  # Container build specification
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── css/
│   │   └── style.css               # Custom styling, dark/light theme, auth typography
│   ├── images/                     # Logos, emblems, high-res Kerala backwaters background
│   │   ├── brand-emblem.png        # High-res platform brand emblem
│   │   ├── kerala_hero_banner.png  # Authentic panoramic Kerala backwaters background
│   │   └── kerala_govt_emblem.png  # State seal
│   ├── js/
│   │   └── app.js                  # Complete GIS interface, Leaflet maps, auth, proxy
│   └── index.html                  # Main single-page application & login portal
├── LEAN_ENTERPRISE_BLUEPRINT.md    # Architecture and lean scaling guide
├── PRESENTATION_GUIDE.md           # Demonstration and hackathon walkthrough
├── PROJECT_WALKTHROUGH.md          # Exhaustive data provenance and pipeline guide
├── README.md                       # Master platform guide & workflow documentation
└── output/                         # Export and generated GeoJSON files
```

---

## 🚀 10. Quick Start & Local Setup

### Prerequisites
- **Python 3.11** or **3.12**
- (Optional) **PostgreSQL 16 + PostGIS 3.5**
- (Optional) **Docker**

### 1. Clone & Setup Virtual Environment
```bash
# Clone repository
git clone https://github.com/your-org/vellam-gis.git
cd vellam-gis

# Create & activate virtual environment (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment (Optional `.env`)
Create a `.env` file in the root directory:
```env
ADMIN_SECRET_KEY=VIP@DUK
DATABASE_URL=postgresql://postgres:password@localhost:5432/vellam_db
GEMINI_API_KEY=your_gemini_api_key_here
HOST=127.0.0.1
PORT=8000
```
> *Note: If `DATABASE_URL` or `GEMINI_API_KEY` are not provided, Jal Taranga operates seamlessly using its built-in JSON fallback data loader and 7-zone microterrain hydrology solver.*

### 3. Run Automated Tests
```bash
pytest backend/tests/ -v
```

### 4. Launch Application
```bash
python backend/app/main.py
```
Open your browser:
- **Web Platform**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **System Health & Database Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🐳 11. Docker Deployment

```bash
# Build the Docker image
docker build -t vellam-gis:latest -f backend/Dockerfile .

# Run container
docker run -d   --name vellam-platform   -p 8000:8000   -e ADMIN_SECRET_KEY="VIP@DUK"   vellam-gis:latest

# Check health
curl http://localhost:8000/health
```

---

## 📡 12. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check, PostGIS database connection, and record counts |
| `GET` | `/` | Serves the single-page application |
| `GET` | `/api/auth/stores-status` | Telemetry on PostgreSQL connection and JSON cache sync |
| `POST` | `/api/auth/login` | Segregated login for Officers and Citizens |
| `POST` | `/api/auth/register-citizen` | Registers a new Citizen into PostgreSQL `citizens` & JSON cache |
| `GET` | `/api/kerala/baseline` | Baselines: 14 districts, 44 river basins, inundation depressions, landslide scarps |
| `POST` | `/api/watershed/ai-plan` | Evaluates bounding box, checks restricted zones, runs Gemini 2.5 / 7-zone solver |
| `POST` | `/api/dem/accumulation` | Computes rainfall accumulation volume, inundated hectares, and flow velocity |
| `GET` | `/api/intervention/basins` | Available river basins metadata for intervention planning |
| `POST` | `/api/intervention/simulate` | Simulates post-intervention hydrological outcomes (runoff, soil loss, recharge, cost) |
| `GET` | `/api/landslides/hazards` | Western Ghats high-precision landslide susceptibility zones and telemetry |
| `POST` | `/api/landslides/simulate-slope` | Real-time Taylor Infinite Slope Factor of Safety calculation |
| `GET` | `/api/watershed/delineate/status` | Readiness and local cache telemetry for MERIT-Basins |
| `POST` | `/api/watershed/delineate` | Dynamic point-and-click upstream watershed delineation |
| `POST` | `/api/watershed/delineate/download` | Triggers background download of South Asia MERIT dataset |
| `GET` | `/api/srishti/assets` | ISRO Bhuvan SRISHTI & DRISHTI geotagged watershed assets registry |
| `POST` | `/api/srishti/assets` | Geotag new field asset from DRISHTI mobile terminal |
| `GET` | `/api/srishti/satellite-crop` | Dynamic multi-spectral crop with NDVI false-color rendering |
| `GET` | `/api/srishti/analytics` | Cumulative watershed performance analytics under Bhuvan monitoring |
| `GET` | `/api/reports` | Public sanitized feed of citizen field reports (emails redacted) |
| `POST` | `/api/reports` | Citizen submission of geotagged disaster report |
| `POST` | `/api/admin/verify-key` | Validates administrator secret key (`VIP@DUK`) |
| `GET` | `/api/admin/reports` | Administrative ledger including full contact info and photos |
| `PATCH` | `/api/admin/reports/{id}/status` | Updates triage status of an incident report |
| `DELETE` | `/api/admin/reports/{id}` | Permanently removes an invalid incident report |
| `GET` | `/api/admin/users` | Live PostgreSQL database user ledger across all tiers |

---

## 🧪 13. Automated Test Suite & Verification

Jal Taranga features a robust, automated test suite built with **pytest** covering endpoints, role security, delineation, physics solvers, and spatial transformations:

```bash
# Run the complete test suite from the repository root
python -m pytest

# Or with verbose test output
python -m pytest -v
```

- **Current Status**: **45 passed, 0 failed (100% pass rate)**.
- **Coverage Areas**:
  - `backend/tests/test_api.py`: Baseline endpoints, health checks, district metadata, and store statuses.
  - `backend/tests/test_auth.py`: Role segregation, password hashing, HMAC secret verification, token expiration, and registration flows.
  - `backend/tests/test_delineation.py`: MERIT-Basins status checks, topological stream snapping, and synthetic Kerala catchment fallbacks.
  - `backend/tests/test_features_upgrade.py`: Dual-storage synchronization (`MultiStoreManager`), SRISHTI/DRISHTI asset registry, and EXIF GPS extraction.
  - `backend/tests/test_hydrology.py`: Taylor Infinite Slope equation, SCS Curve Number runoff accumulation, and USLE soil loss equations.

---

## 👥 14. Team & Credits

Developed with dedication by **VISIONQUEST**. Built for the resilience, safety, and water security of Kerala.

### Core Team Members
| Member | Role & Responsibilities |
|---|---|
| **Femin Johny** | **Team Leader & Project Lead** — Platform Architecture, Project Coordination & Full-Stack Systems |
| **Rajana Jyothirmayi** | **Core Team & Researcher** — Hydrological Modeling, Disaster Analysis & Literature Provenance |
| **Gayathry S R** | **Core Team & Researcher** — Multi-Spectral Earth Observation, Remote Sensing & Environmental Impact |
| **Priyadarsan G P** | **Core Team & Engineer** — Geotechnical Engineering, Taylor Slope Stability & USLE Formulation |
| **M.Aqeeb Baba** | **Core Team & Engineer** — Spatial GIS Pipelines, PostGIS Database Architecture & Backend REST APIs |
| **Bijay Thomas** | **Core Team & Developer** — Frontend UI/UX, Dynamic Leaflet Mapping, Chart.js & Integration |
