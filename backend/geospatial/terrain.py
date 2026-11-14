"""
TerraTwin AI - Planetary Terrain Feature Engineering
Computes planetary-datum-aware Slope (degrees) and Surface Roughness (m RMS)
using windowed/chunked processing safe for 16GB RAM machines.
"""

import numpy as np
from scipy.ndimage import uniform_filter

PLANETARY_RADII = {
    "earth": 6371000.0,  # meters
    "moon": 1737400.0,   # meters
    "mars": 3389500.0    # meters
}

def compute_terrain_derivatives_block(
    dem_block: np.ndarray,
    dx: float,
    dy: float,
    nodata_val: float = None,
    roughness_window: int = 5
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute slope (degrees) and surface roughness RMS (meters) for a 2D elevation block.
    Uses Horn's method for slope with Sobel filters and neighborhood residual standard deviation for roughness.
    
    Args:
        dem_block: 2D numpy array of elevation in meters
        dx: cell width in meters
        dy: cell height in meters
        nodata_val: nodata value to mask
        roughness_window: odd integer window size for roughness computation
        
    Returns:
        (slope_deg, roughness_rms): both 2D float32 arrays
    """
    dem = dem_block.astype(np.float64)
    valid_mask = np.ones_like(dem, dtype=bool)
    if nodata_val is not None:
        valid_mask &= (dem != nodata_val) & ~np.isnan(dem)

    # Gradient computation using 3x3 kernels (Horn's method)
    # Pad borders with edge values to keep dimensions identical
    padded = np.pad(dem, 1, mode='edge')
    
    # dz/dx: horizontal gradient
    # z[r-1, c+1] + 2*z[r, c+1] + z[r+1, c+1] - (z[r-1, c-1] + 2*z[r, c-1] + z[r+1, c-1]) / (8*dx)
    dz_dx = (
        (padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:]) -
        (padded[:-2, :-2] + 2 * padded[1:-1, :-2] + padded[2:, :-2])
    ) / (8.0 * max(dx, 1e-6))

    # dz/dy: vertical gradient
    # (z[r+1, c-1] + 2*z[r+1, c] + z[r+1, c+1]) - (z[r-1, c-1] + 2*z[r-1, c] + z[r-1, c+1]) / (8*dy)
    dz_dy = (
        (padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]) -
        (padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:])
    ) / (8.0 * max(dy, 1e-6))

    grad_sq = dz_dx**2 + dz_dy**2
    slope_rad = np.arctan(np.sqrt(grad_sq))
    slope_deg = np.degrees(slope_rad).astype(np.float32)

    # Surface Roughness: Local standard deviation (RMS of residual elevation) in neighborhood
    # roughness = sqrt(E[x^2] - (E[x])^2)
    mean_dem = uniform_filter(dem, size=roughness_window, mode='reflect')
    mean_dem_sq = uniform_filter(dem**2, size=roughness_window, mode='reflect')
    variance = np.maximum(mean_dem_sq - (mean_dem**2), 0.0)
    roughness_rms = np.sqrt(variance).astype(np.float32)

    # Mask nodata regions
    if nodata_val is not None:
        slope_deg[~valid_mask] = -9999.0
        roughness_rms[~valid_mask] = -9999.0

    return slope_deg, roughness_rms
