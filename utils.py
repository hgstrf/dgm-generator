import laspy
import numpy as np
from collections import defaultdict
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import from_origin

def read_laz_file(path):
    las = laspy.read(path)
    return las.x, las.y, las.z, las.classification

def filter_by_class(x, y, z, classifications, selected_classes):
    mask = np.isin(classifications, list(selected_classes))
    return x[mask], y[mask], z[mask]

def compute_grid_extent(x, y, grid_size):
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    xi = np.arange(xmin, xmax, grid_size)
    yi = np.arange(ymin, ymax, grid_size)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    grid_shape = xi_grid.shape
    return xi, yi, xi_grid, yi_grid, grid_shape, xmin, ymax

def accumulate_z_values(x, y, z, grid_shape, xmin, ymax, grid_size):
    x_idx = ((x - xmin) / grid_size).astype(int)
    y_idx = ((ymax - y) / grid_size).astype(int)  # flip Y
    grid_z_values = defaultdict(list)
    for gx, gy, gz in zip(x_idx, y_idx, z):
        if 0 <= gy < grid_shape[0] and 0 <= gx < grid_shape[1]:
            grid_z_values[(gy, gx)].append(gz)
    return grid_z_values

def compute_median_grid(grid_z_values, grid_shape):
    z_avg = np.full(grid_shape, np.nan, dtype=float)
    for (gy, gx), z_list in grid_z_values.items():
        z_avg[gy, gx] = np.median(z_list)
    return z_avg

def interpolate_missing_cells(z_avg, xi_grid, yi_grid):
    mask = ~np.isnan(z_avg)
    return griddata(
        (xi_grid[mask], yi_grid[mask]),
        z_avg[mask],
        (xi_grid, yi_grid),
        method='nearest'
    )

def plot_grid(zi_interp, xi_grid, yi_grid, xmin, ymax):
    plt.figure(figsize=(10, 8))
    plt.imshow(
        zi_interp,
        extent=(xmin, xmin + xi_grid.shape[1] * (xi_grid[0, 1] - xi_grid[0, 0]),
                ymax - yi_grid.shape[0] * (yi_grid[1, 0] - yi_grid[0, 0]), ymax),
        origin='lower',
        cmap='terrain'
    )
    plt.colorbar(label='Height (Z)')
    plt.title("Interpolated DGM")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()

def save_geotiff(path, zi_interp, xmin, ymax, grid_size, crs):
    transform = from_origin(xmin, ymax, grid_size, grid_size)
    zi_flipped = np.flipud(zi_interp)
    with rasterio.open(
        path,
        'w',
        driver='GTiff',
        height=zi_flipped.shape[0],
        width=zi_flipped.shape[1],
        count=1,
        dtype=zi_flipped.dtype,
        crs=crs,
        transform=transform
    ) as dst:
        dst.write(zi_flipped, 1)