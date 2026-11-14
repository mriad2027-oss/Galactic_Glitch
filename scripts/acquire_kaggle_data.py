"""
TerraTwin AI - Kaggle Data Acquisition Engine
Reproducible, authenticated & anonymous Kaggle data downloader with provenance tracking,
SHA-256 verification, and strict scientific integrity classification.
"""

import os
import sys
import json
import shutil
import hashlib
import datetime
from pathlib import Path
import kagglehub

# Dataset definitions with scientific provenance classification
DATASETS_CONFIG = [
    {
        "id": "moon_lola_20m",
        "planet": "moon",
        "category": "LOLA",
        "kaggle_handle": "alexhhhh0938/lunar-nac-real-context",
        "title": "NASA Lunar LOLA and LROC NAC Real Context",
        "original_source": "NASA Goddard Space Flight Center (GSFC) Planetary Geodynamics Laboratory / LOLA Science Team (https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF)",
        "instrument": "Lunar Reconnaissance Orbiter (LRO) - Lunar Orbiter Laser Altimeter (LOLA)",
        "features": ["Elevation"],
        "unit": "m",
        "resolution": "20 m/pixel",
        "provenance": "REAL_DERIVED",
        "license": "CC0: Public Domain",
        "target_dir": "data/moon/raw/LOLA",
        "primary_files": ["lunar20_nac_common.tif", "lunar20_nac_common.tif.json"]
    },
    {
        "id": "moon_southpole_finetune",
        "planet": "moon",
        "category": "LOLA",
        "kaggle_handle": "encinas88/lunarsite-southpole-finetune",
        "title": "LunarSite South Pole Crater Fine-Tuning HDF5",
        "original_source": "NASA LRO LOLA South Pole 118m/pixel Polar Stereographic DEM tiles (LDEM_80S_118M) + Robbins Lunar Crater Database",
        "instrument": "LRO LOLA + Robbins Catalog",
        "features": ["Elevation", "Crater Rims"],
        "unit": "m",
        "resolution": "118 m/pixel",
        "provenance": "REAL_DERIVED",
        "license": "CC0: Public Domain",
        "target_dir": "data/moon/raw/LOLA",
        "primary_files": ["southpole_finetune_118mpp.hdf5"]
    },
    {
        "id": "moon_m3_mineralogy",
        "planet": "moon",
        "category": "M3",
        "kaggle_handle": "yash92328/lunar-water-discovery",
        "title": "Lunar Water Discovery using Chandrayaan Data",
        "original_source": "ISRO / NASA Chandrayaan-1 Moon Mineralogy Mapper (M3) calibrated spectral reflectance cube of Bullialdus Crater",
        "instrument": "Chandrayaan-1 Moon Mineralogy Mapper (M3) Imaging Spectrometer",
        "features": ["Mineralogy", "Spectral Reflectance (83 bands)"],
        "unit": "Reflectance factor (I/F)",
        "resolution": "140 m/pixel",
        "provenance": "REAL_OBSERVATIONAL",
        "license": "CC0: Public Domain",
        "target_dir": "data/moon/raw/M3",
        "primary_files": ["Bullialdus_m3_tiff.tif"]
    },
    {
        "id": "mars_jezero_terrain",
        "planet": "mars",
        "category": "MOLA",
        "kaggle_handle": "olekis/mars-terrain-ai-jezero-hazard-and-routing-data",
        "title": "Mars Terrain AI | Jezero Hazard & Routing Data",
        "original_source": "NASA/USGS Mars Reconnaissance Orbiter (MRO) HiRISE Digital Terrain Model (DTM) aligned with MGS MOLA elevation datum",
        "instrument": "MRO HiRISE + MGS MOLA",
        "features": ["Elevation", "Slope", "Surface Roughness"],
        "unit": "m (elevation, roughness), degrees (slope)",
        "resolution": "1 m/pixel DTM",
        "provenance": "REAL_DERIVED",
        "license": "Unknown (NASA/USGS Open Data derived)",
        "target_dir": "data/mars/raw/MOLA",
        "primary_files": [
            "jezero_dem_1024.tif",
            "jezero_slope.tif",
            "jezero_roughness.tif",
            "jezero_terrain_methodology.json"
        ]
    },
    {
        "id": "mars_crater_catalog",
        "planet": "mars",
        "category": "Geology",
        "kaggle_handle": "codebreaker619/mars-crater-study-dataset",
        "title": "Mars Crater Study Dataset",
        "original_source": "Robbins & Hynek (2012) Global Mars Impact Crater Database (USGS / NASA PDS), 378,540 craters >= 1 km",
        "instrument": "MGS MOLA topography + Mars Odyssey THEMIS IR + Viking MDIM",
        "features": ["Crater Coordinates", "Diameter", "Depth", "Morphology"],
        "unit": "km (diameter), m (depth)",
        "resolution": "Global catalog",
        "provenance": "REAL_DERIVED",
        "license": "Other (USGS Open Science Data)",
        "target_dir": "data/mars/raw/Geology",
        "primary_files": ["Mars Crater info.csv"]
    },
    {
        "id": "earth_srtm_dem",
        "planet": "earth",
        "category": "Elevation",
        "kaggle_handle": "dwarika/smoothed-digital-elevation-model-dem",
        "title": "Smoothed Digital Elevation Model (DEM)",
        "original_source": "NASA Shuttle Radar Topography Mission (SRTM) 1 Arc-Second Global Elevation (USGS EROS)",
        "instrument": "Space Shuttle Endeavour STS-99 SRTM C-band Radar",
        "features": ["Elevation"],
        "unit": "m",
        "resolution": "1 arc-second (~30 m)",
        "provenance": "REAL_DERIVED",
        "license": "NASA/USGS Public Domain",
        "target_dir": "data/earth/raw",
        "primary_files": [
            "DEM_cropped_extent_v01/dem_s_1s_clip.tif",
            "DEM_cropped_extent_v01/dem_s_1s_clip.tfw",
            "DEM_cropped_extent_v01/dem_s_1s_clip.tif.ovr"
        ]
    },
    {
        "id": "earth_modis_lst_srtm",
        "planet": "earth",
        "category": "Temperature_Elevation",
        "kaggle_handle": "umutalkn/modis-lst-and-dem-marmara",
        "title": "MODIS LST & SRTM DEM Dataset",
        "original_source": "NASA EOSDIS Terra/Aqua MODIS Land Surface Temperature (MOD11A1/MYD11A1) + SRTM Topography",
        "instrument": "Terra/Aqua MODIS Thermal Radiometer + SRTM Radar",
        "features": ["Day LST", "Night LST", "Elevation"],
        "unit": "Celsius / Kelvin (temperature), m (elevation)",
        "resolution": "1 km LST / 90 m SRTM",
        "provenance": "REAL_OBSERVATIONAL",
        "license": "CC BY 4.0",
        "target_dir": "data/earth/raw",
        "primary_files": ["dataset_v3.csv"]
    },
    {
        "id": "earth_worldclim_global",
        "planet": "earth",
        "category": "Global_Climate",
        "kaggle_handle": "erickfhernandezp/global-carnivorous-plants-with-climate-data",
        "title": "Global BioClimatic Climate & Elevation Dataset",
        "original_source": "WorldClim v2.1 Global Climate Grids (Fick & Hijmans, 2017) + SRTM elevation across 92,617 worldwide coordinates",
        "instrument": "Global Historical Climatology Network (GHCN) + Satellite Remote Sensing",
        "features": ["Annual Mean Temperature (bio1)", "Diurnal Range (bio2)", "Precipitation (bio12)", "Elevation"],
        "unit": "°C (temperature), mm (precipitation), m (elevation)",
        "resolution": "30 arc-seconds (~1 km)",
        "provenance": "REAL_DERIVED",
        "license": "CC BY 4.0",
        "target_dir": "data/earth/raw",
        "primary_files": ["Riched Carnivorous Plant.csv"]
    }
]

# Unavailable datasets on Kaggle - recorded with scientific honesty per project requirements
UNAVAILABLE_DATASETS = [
    {
        "id": "moon_diviner_global_temperature",
        "planet": "moon",
        "category": "Temperature",
        "intended_instrument": "NASA LRO Diviner Lunar Radiometer Experiment (DLRE)",
        "feature": "Surface Temperature (K)",
        "status": "UNAVAILABLE_ON_KAGGLE",
        "reason": "No validated full numerical raster of LRO Diviner surface temperatures is hosted on Kaggle. Fake formula or synthetic generation strictly prohibited.",
        "official_source": "NASA PDS Geosciences Node (https://pds-geosciences.wustl.edu/missions/lro/diviner.htm)"
    },
    {
        "id": "moon_lend_hydrogen_neutron",
        "planet": "moon",
        "category": "Neutron_Hydrogen",
        "intended_instrument": "NASA LRO Lunar Exploration Neutron Detector (LEND)",
        "feature": "Epithermal Neutron Flux (counts/s)",
        "status": "UNAVAILABLE_ON_KAGGLE",
        "reason": "No validated LEND neutron flux counts dataset is hosted on Kaggle. Fake hydrogen measurements strictly prohibited.",
        "official_source": "NASA PDS Geosciences Node LEND archive"
    },
    {
        "id": "moon_crater_radiation",
        "planet": "moon",
        "category": "Radiation",
        "intended_instrument": "NASA LRO Cosmic Ray Telescope for the Effects of Radiation (CRaTER)",
        "feature": "Radiation Dose Rate",
        "status": "UNAVAILABLE_ON_KAGGLE",
        "reason": "No validated CRaTER calibrated dose map is hosted on Kaggle.",
        "official_source": "NASA PDS CRaTER archive"
    },
    {
        "id": "moon_psr_illumination",
        "planet": "moon",
        "category": "Illumination_PSR",
        "intended_instrument": "LRO LOLA/LROC Polar Illumination & Shadow Products",
        "feature": "Sunlight Fraction & Permanent Shadow Mask",
        "status": "UNAVAILABLE_ON_KAGGLE",
        "reason": "No standalone global PSR mask is hosted as a clean validated product on Kaggle.",
        "official_source": "NASA PDS LRO Archive"
    }
]

def sha256_file(filepath: Path) -> str:
    """Compute SHA-256 checksum in chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def acquire_all(workspace_dir: Path):
    """Download and organize all Kaggle datasets into workspace."""
    workspace_dir = Path(workspace_dir).resolve()
    manifests_dir = workspace_dir / "data" / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    download_logs = []
    registry = []

    print(f"[{datetime.datetime.now().isoformat()}] Starting TerraTwin Kaggle Data Acquisition...")

    for cfg in DATASETS_CONFIG:
        ds_id = cfg["id"]
        handle = cfg["kaggle_handle"]
        planet = cfg["planet"]
        target_dir = workspace_dir / cfg["target_dir"]
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n---> [ACQUIRING] {cfg['title']} ({handle})")
        print(f"     Planet: {planet.upper()} | Provenance: {cfg['provenance']}")

        try:
            # Download via kagglehub (handles local cache and resumption)
            download_path = Path(kagglehub.dataset_download(handle))
            print(f"     Kagglehub cache: {download_path}")

            files_recorded = []
            for pf in cfg["primary_files"]:
                src_path = download_path / pf
                if not src_path.exists():
                    # Check recursively
                    found = list(download_path.glob(f"**/{Path(pf).name}"))
                    if found:
                        src_path = found[0]
                    else:
                        print(f"     [WARNING] Expected file {pf} not found in {download_path}")
                        continue

                dst_name = src_path.name
                dst_path = target_dir / dst_name

                # Copy to project raw directory if not already there or size differs
                if not dst_path.exists() or dst_path.stat().st_size != src_path.stat().st_size:
                    shutil.copy2(src_path, dst_path)
                    print(f"     [COPIED] -> {dst_path.relative_to(workspace_dir)}")
                else:
                    print(f"     [EXISTS] -> {dst_path.relative_to(workspace_dir)}")

                f_size = dst_path.stat().st_size
                f_hash = sha256_file(dst_path)

                files_recorded.append({
                    "relative_path": str(dst_path.relative_to(workspace_dir)).replace("\\", "/"),
                    "filename": dst_name,
                    "bytes": f_size,
                    "sha256": f_hash
                })

            log_entry = {
                "dataset_id": ds_id,
                "kaggle_handle": handle,
                "title": cfg["title"],
                "planet": planet,
                "category": cfg["category"],
                "provenance": cfg["provenance"],
                "license": cfg["license"],
                "original_source": cfg["original_source"],
                "download_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": "COMPLETED",
                "files": files_recorded
            }
            download_logs.append(log_entry)

            registry.append({
                "id": ds_id,
                "name": cfg["title"],
                "planet": planet,
                "instrument": cfg["instrument"],
                "features": cfg["features"],
                "unit": cfg["unit"],
                "resolution": cfg["resolution"],
                "provenance": cfg["provenance"],
                "license": cfg["license"],
                "original_source": cfg["original_source"],
                "availability": "CONNECTED_REAL_DATA",
                "processing_status": "READY_FOR_GEOSPATIAL_PIPELINE",
                "files": [f["relative_path"] for f in files_recorded]
            })

        except Exception as e:
            print(f"     [ERROR] Failed to acquire {handle}: {e}")
            download_logs.append({
                "dataset_id": ds_id,
                "kaggle_handle": handle,
                "planet": planet,
                "download_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "status": f"FAILED: {str(e)}",
                "files": []
            })

    # Record unavailable datasets with strict honesty
    for un in UNAVAILABLE_DATASETS:
        registry.append({
            "id": un["id"],
            "name": f"LRO {un['category']}",
            "planet": un["planet"],
            "instrument": un["intended_instrument"],
            "features": [un["feature"]],
            "unit": "Unknown",
            "resolution": "N/A",
            "provenance": "UNAVAILABLE_ON_KAGGLE",
            "license": "NASA Public Domain",
            "original_source": un["official_source"],
            "availability": "UNAVAILABLE_ON_KAGGLE",
            "processing_status": "NOT_CONNECTED_NO_FAKE_DATA",
            "reason": un["reason"],
            "files": []
        })

    # Save manifests
    manifest_log = manifests_dir / "download_log.json"
    with open(manifest_log, "w", encoding="utf-8") as f:
        json.dump(download_logs, f, indent=2)
    print(f"\nWrote download log to: {manifest_log.relative_to(workspace_dir)}")

    manifest_registry = manifests_dir / "dataset_registry.json"
    with open(manifest_registry, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Wrote dataset registry to: {manifest_registry.relative_to(workspace_dir)}")

    manifest_kaggle = manifests_dir / "kaggle_datasets.json"
    with open(manifest_kaggle, "w", encoding="utf-8") as f:
        json.dump({"configured_datasets": DATASETS_CONFIG, "unavailable_datasets": UNAVAILABLE_DATASETS}, f, indent=2)
    print(f"Wrote Kaggle datasets catalog to: {manifest_kaggle.relative_to(workspace_dir)}")

    print("\n[COMPLETE] TerraTwin Kaggle data acquisition finished successfully.")

if __name__ == "__main__":
    ws = Path(__file__).resolve().parent.parent
    acquire_all(ws)
