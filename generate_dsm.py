import argparse
import logging
import os
import numpy as np
from pathlib import Path
from utils import (
    read_laz_file,
    filter_by_class,
    compute_grid_extent,
    accumulate_z_values,
    compute_median_grid,
    interpolate_missing_cells,
    plot_grid,
    save_geotiff
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a DGM from LAZ files.")
    parser.add_argument("--input", required=True, help="Path to the input LAZ file")
    parser.add_argument("--output", default="./output", help="Directory to save the output GeoTIFF")
    parser.add_argument("--classes", default="all", help="Class IDs to include, comma-separated, or 'all'")
    parser.add_argument("--grid-size", type=float, default=1.0, help="Grid size in meters")
    parser.add_argument("--crs", default="EPSG:4326", help="Coordinate Reference System (e.g. EPSG:4326)")
    parser.add_argument("--plot", action="store_true", help="Show a plot of the interpolated surface")
    return parser.parse_args()

def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info(f"Reading file: {input_path}")
    x, y, z, classifications = read_laz_file(input_path)

    if args.classes.lower() != "all":
        try:
            selected_classes = set(int(cls.strip()) for cls in args.classes.split(","))
            x, y, z = filter_by_class(x, y, z, classifications, selected_classes)
            class_str = "cls" + "_".join(str(cls) for cls in sorted(selected_classes))
        except ValueError:
            raise ValueError("Invalid class input: use comma-separated integers or 'all'.")
    else:
        class_str = "all"

    logging.info("Creating grid...")
    xi, yi, xi_grid, yi_grid, grid_shape, xmin, ymax = compute_grid_extent(x, y, args.grid_size)

    logging.info("Accumulating Z values...")
    grid_z_values = accumulate_z_values(x, y, z, xi_grid.shape, xmin, ymax, args.grid_size)

    logging.info("Computing median heights...")
    z_avg = compute_median_grid(grid_z_values, xi_grid.shape)

    logging.info("Interpolating missing grid cells...")
    zi_interp = interpolate_missing_cells(z_avg, xi_grid, yi_grid)

    if args.plot:
        plot_grid(zi_interp, xi_grid, yi_grid, xmin, ymax)

    filename = f"{input_path.stem}_{args.grid_size:.2f}m_{class_str}.tif"
    output_path = output_dir / filename

    logging.info(f"Saving GeoTIFF to {output_path}")
    zi_interp_flipped = np.flipud(zi_interp)
    save_geotiff(output_path, zi_interp_flipped, xmin, ymax, args.grid_size, args.crs)

    logging.info("Done.")

if __name__ == "__main__":
    main()
