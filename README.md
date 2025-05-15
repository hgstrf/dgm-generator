# DSM/DGM Generator from LAZ Files

Generate a DSM/DGM from point cloud data in LAZ format using Python.

---

## Features

- Configurable point class filtering
- Computes gridded median surface
- Interpolates missing cells
- Saves output as GeoTIFF with proper CRS
- Optional surface visualization via Matplotlib (might be slow, not recommended for large files)

---

## Installation

Install required Python packages:

```
pip install -r requirements.txt
```

---

## Usage

```
python generate_dsm.py \
  --input ./input/your_file.laz \
  --output ./output \
  --classes 2,6 \
  --grid-size 1 \
  --crs EPSG:4326 \
  --plot
```

### Arguments

| Argument       | Description                                      |
|----------------|--------------------------------------------------|
| `--input`      | Path to input `.laz` file                        |
| `--output`     | Directory to save output GeoTIFF (default: `./output`) |
| `--classes`    | Comma-separated class IDs (e.g., `2,6`) or `all` |
| `--grid-size`  | Grid cell size in meters (default: `1.0`)        |
| `--crs`        | Output CRS, e.g., `EPSG:4326`                    |
| `--plot`       | Add this flag to display the resulting DGM plot  |

---

## Example

```
python generate_dsm.py \
  --input ./input/example.laz \
  --classes 2 \
  --grid-size 0.5 \
  --crs EPSG:4326 \
  --plot
```

---

## Notes

- This tool uses the **median** Z value per grid cell to create a smoother ground model.
- Interpolation is performed using **nearest-neighbor** for speed and simplicity.
- Ensure the input `.laz` coordinates match the specified CRS.

---

## License

MIT License
