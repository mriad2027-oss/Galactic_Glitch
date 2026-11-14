# TerraTwin AI — Planetary Geospatial Data & Earth Analog Discovery Engine

TerraTwin AI is a full-stack planetary geospatial and machine-learning platform designed to discover, compare, and rank Earth analog environments for planetary regions across the **Moon** and **Mars** using **real observational remote-sensing datasets acquired directly from Kaggle**.

---

## 1. System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │            Existing Frontend (HTML5 / Three.js)         │
                    │      http://localhost:8080 (Planetary Globe & UI)      │
                    └──────────────────────────▲─────────────────────────────┘
                                               │ HTTP / JSON API
                    ┌──────────────────────────▼─────────────────────────────┐
                    │               FastAPI Backend (:8000)                  │
                    │       Routes: /planets, /datasets, /layers, /analogs   │
                    └──────────────────────────▲─────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               │                                                               │
┌──────────────▼────────────────┐                              ┌───────────────▼────────────────┐
│   ML Analog Discovery Engine   │                              │   Geospatial Processing Engine │
│  - Multi-metric KNN & Ranking │                              │  - Windowed Slope (Horn 1981)  │
│  - Feature scaling & attribution│                             │  - Surface Roughness (5x5 RMS) │
│  - Honest missing data handling│                             │  - Datum & CRS validation      │
└──────────────▲────────────────┘                              └───────────────▲────────────────┘
               │                                                               │
               └───────────────────────────────┬───────────────────────────────┘
                                               │ Real GeoTIFFs, HDF5, CSV
                    ┌──────────────────────────▼─────────────────────────────┐
                    │               data/ Directory Structure                │
                    │   data/moon/   |   data/mars/   |   data/earth/        │
                    │   data/manifests/ (download_log, registry, validation)  │
                    └──────────────────────────▲─────────────────────────────┘
                                               │ kagglehub download & SHA-256
                    ┌──────────────────────────┴─────────────────────────────┐
                    │               Kaggle Datasets Engine                    │
                    │      NASA LRO LOLA, HiRISE Jezero, M3, SRTM, MODIS      │
                    └────────────────────────────────────────────────────────┘
```

---

## 2. Real Kaggle Datasets Acquired & Validated

All datasets were downloaded via `kagglehub` and cryptographically verified with SHA-256 checksums into the `data/` directory.

| Planet | Kaggle Dataset Identifier | Original Scientific Source | Files & Sizes | Provenance | License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Moon** | `alexhhhh0938/lunar-nac-real-context` | NASA Goddard Space Flight Center (GSFC) LOLA 20mpp Polar Stereographic DEM (`LDEM_80S_20MPP_ADJ.TIF`) | `lunar20_nac_common.tif` (25.4 MB) | `REAL_DERIVED` | CC0: Public Domain |
| **Moon** | `encinas88/lunarsite-southpole-finetune` | NASA LRO LOLA 118m/pixel South Pole DEM + Robbins Lunar Crater Rims | `southpole_finetune_118mpp.hdf5` (10.9 MB) | `REAL_DERIVED` | CC0: Public Domain |
| **Moon** | `yash92328/lunar-water-discovery` | ISRO/NASA Chandrayaan-1 Moon Mineralogy Mapper (M3) calibrated 83-band spectral cube of Bullialdus Crater | `Bullialdus_m3_tiff.tif` (46.3 MB) | `REAL_OBSERVATIONAL` | CC0: Public Domain |
| **Mars** | `olekis/mars-terrain-ai-jezero-hazard-and-routing-data` | NASA/USGS MRO HiRISE DTM aligned with MGS MOLA elevation datum | `jezero_dem_1024.tif` (2.2 MB), `jezero_slope.tif` (3.7 MB), `jezero_roughness.tif` (3.7 MB) | `REAL_DERIVED` | NASA/USGS Open Data |
| **Mars** | `codebreaker619/mars-crater-study-dataset` | Robbins & Hynek (2012) Global Mars Impact Crater Database (378,540 craters $\ge 1\text{ km}$) | `Mars Crater info.csv` (16.8 MB) | `REAL_DERIVED` | USGS Open Science Data |
| **Earth** | `dwarika/smoothed-digital-elevation-model-dem` | NASA Shuttle Radar Topography Mission (SRTM) 1 Arc-Second Global DEM | `dem_s_1s_clip.tif` (13.6 MB) | `REAL_DERIVED` | NASA/USGS Public Domain |
| **Earth** | `umutalkn/modis-lst-and-dem-marmara` | NASA Terra/Aqua MODIS Day/Night Land Surface Temperature + SRTM | `dataset_v3.csv` (4.2 MB) | `REAL_OBSERVATIONAL` | CC BY 4.0 |
| **Earth** | `erickfhernandezp/global-carnivorous-plants-with-climate-data` | WorldClim v2.1 Global Climate Grids + SRTM Elevation across 92,617 points | `Riched Carnivorous Plant.csv` (34.6 MB) | `REAL_DERIVED` | CC BY 4.0 |

### Scientific Honesty: Datasets Unavailable on Kaggle
In accordance with scientific integrity guidelines, missing datasets are **honestly declared as unavailable** and are **never substituted with synthetic or invented mathematical formulas**:
- **LRO Diviner Surface Temperature**: No full calibrated numerical temperature raster is hosted on Kaggle (`UNAVAILABLE_ON_KAGGLE`).
- **LRO LEND Neutron Flux / Hydrogen**: No calibrated neutron count raster is hosted on Kaggle (`UNAVAILABLE_ON_KAGGLE`).
- **LRO CRaTER Radiation**: No calibrated dose rate map is hosted on Kaggle (`UNAVAILABLE_ON_KAGGLE`).
- **LOLA/LROC Polar PSR Mask**: No standalone global PSR raster mask is hosted on Kaggle (`UNAVAILABLE_ON_KAGGLE`).

---

## 3. Geospatial Processing & Derived Products

Processed rasters are generated using memory-safe windowed processing (using `rasterio`, `scipy.ndimage`, and `numpy`):
- **Elevation**: Scaled and calibrated to planetary geodetic datums (Moon: 1737.4 km reference sphere; Mars: MOLA equipotential surface; Earth: WGS84/EGM96).
- **Slope (degrees)**: Computed via Horn's finite-difference method with edge halo preservation:
  $$\text{Slope} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180^\circ}{\pi}$$
- **Surface Roughness (m RMS)**: Root-Mean-Square residual standard deviation within a local neighborhood window:
  $$\text{Roughness} = \sqrt{\overline{z^2} - (\bar{z})^2}$$

All outputs are saved as deflate-compressed, 256x256 tiled GeoTIFFs:
- `data/moon/processed/moon_lola_elevation.tif` (range: -2028.9 m to +5660.5 m)
- `data/moon/processed/moon_lola_slope.tif` (range: 0.00° to 46.89°)
- `data/moon/processed/moon_lola_roughness.tif` (range: 0.15 m to 20.14 m RMS)
- `data/mars/processed/mars_jezero_elevation.tif` (range: -2592.7 m to -2558.1 m)
- `data/mars/processed/mars_jezero_slope.tif` (range: 0.00° to 36.09°)
- `data/mars/processed/mars_jezero_roughness.tif` (range: 0.00 m to 0.83 m RMS)
- `data/earth/processed/earth_srtm_elevation.tif` (range: -4.9 m to 1233.9 m)
- `data/earth/processed/earth_srtm_slope.tif` (range: 0.00° to 84.18°)
- `data/earth/processed/earth_srtm_roughness.tif` (range: 0.00 m to 4898.5 m RMS)

---

## 4. Machine Learning Analog Discovery Engine

The ML engine (`backend/ml/engine.py`):
1. **Dynamic Comparability**: Re-normalizes weights strictly across available, scientifically comparable physical metrics.
2. **Missing Feature Handling**: When a feature is missing (e.g. Diviner temperature on the Moon), it is transparently excluded from the distance metric and marked with `missing: true`. Missing values are **never treated as zero**.
3. **Similarity Metric**:
   $$d(\mathbf{x}, \mathbf{y}) = \sqrt{\sum_{k \in \text{valid}} w_k \left(\frac{x_k - y_k}{\sigma_k}\right)^2}, \quad S = \exp(-2.2 \times d) \in (0, 1]$$
4. **Ranking & Attribution**: Returns top-ranked Earth locations (e.g., Haughton Impact Crater, Taylor Valley, Atacama, Australian Channel Country, Lonar Crater) with full feature contribution breakdowns and physical values.

---

## 5. API Endpoints

The FastAPI backend (`http://localhost:8000`) provides:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health, validated dataset count, engine version |
| `GET` | `/api/v1/planets` | Planet catalog, radii, roles, connected datasets |
| `GET` | `/api/v1/planets/{planet}/datasets` | Registered real Kaggle datasets and file provenance |
| `GET` | `/api/v1/planets/{planet}/layers` | Available raster layers with real/unavailable status |
| `POST` | `/api/v1/regions` | Save selected planetary region and extract physical features |
| `GET` | `/api/v1/regions/{region_id}` | Retrieve saved region by ID |
| `POST` | `/api/v1/analogs/search` | **Core ML endpoint**: Takes `{planet, lat, lon, features}`, returns ranked Earth analogs |
| `POST` | `/api/v1/analysis` | Background analysis job submission |
| `GET` | `/api/v1/analysis/{analysis_id}` | Retrieve results of background analysis job |

---

## 6. Execution Instructions

### A. Prerequisites
Python 3.10+ (tested on Python 3.14.2) with pip.

Install dependencies:
```bash
python -m pip install fastapi uvicorn rasterio scipy numpy pandas kagglehub h5py requests
```

### B. Download & Verify Real Kaggle Data
Run the reproducible Kaggle acquisition engine:
```bash
python scripts/acquire_kaggle_data.py
```
*(Supports optional Kaggle API tokens via environment variables `KAGGLE_USERNAME` and `KAGGLE_KEY`, or anonymous public download via kagglehub).*

### C. Run Geospatial Processing & Validation
Generate derived terrain layers (slope, roughness) and validate raster integrity:
```bash
python -m backend.geospatial.processor
```

### D. Launch Full Application (Recommended: One Command)
You can launch both the FastAPI backend and the frontend together with automatic browser launch and clean Ctrl+C shutdown:
```bash
python run_app.py
```

Or start them manually in separate terminals:
```bash
# Terminal 1: Backend
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
python -m http.server 8080
```
Open **`http://localhost:8080`** in any web browser.

### E. Run End-to-End Test Suite
To verify the entire pipeline (Kaggle acquisition -> Checksums -> Processing -> ML Engine -> FastAPI -> Frontend):
```bash
python -m tests.test_end_to_end
```
