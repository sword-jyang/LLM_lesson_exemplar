#!/usr/bin/env python3
"""
Reusable geospatial harmonization utilities for URL-driven examples.

This module supports mixed raster/vector workflows where datasets are:
1. downloaded from URLs
2. extracted if needed
3. harmonized to a common CRS, extent, and resolution
4. saved to disk
5. visualized as aligned outputs

Supports WCS (Web Coverage Service) for efficient subsetting of large raster datasets.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
import shutil
import urllib.request
import urllib.parse
import zipfile
import io
import base64
import xml.etree.ElementTree as ET

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from rasterio import mask
from shapely.geometry import box

try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


BBox = tuple[float, float, float, float]

# Global color map discovered from source data (used by visualization functions)
DISCOVERED_COLOR_MAP: dict | None = None
# Global labels map: integer value -> short label string (e.g. 101 -> "GR1")
DISCOVERED_LABELS: dict | None = None

# Tokens that should always be rendered in ALL CAPS in display labels.
_KNOWN_ACRONYMS: set[str] = {
    "fbfm", "fbfm40", "fbfm13", "mtbs", "pr", "vpd",
    "rcp", "rcp45", "rcp85", "ccsm", "ccsm4",
    "dem", "ndvi", "nbr", "evi",
    "conus", "wms", "wcs", "crs", "cog", "stac", "naip",
}


def _format_layer_name(name: str) -> str:
    """Convert a snake_case layer name to a human-readable title.

    Tokens that are known acronyms (MTBS, FBFM40, PR, RCP85, …) are
    uppercased; all other tokens are title-cased.

    Examples
    --------
    >>> _format_layer_name("fbfm40_fuel_models")
    'FBFM40 Fuel Models'
    >>> _format_layer_name("pr_winter_rcp85_ccsm4")
    'PR Winter RCP85 CCSM4'
    >>> _format_layer_name("mtbs_burned_areas")
    'MTBS Burned Areas'
    """
    tokens = name.replace("_", " ").split()
    result = []
    for token in tokens:
        lower = token.lower()
        # Strip trailing digits to check the base (e.g. "rcp85" → base "rcp")
        base = lower.rstrip("0123456789")
        if lower in _KNOWN_ACRONYMS or base in _KNOWN_ACRONYMS:
            result.append(token.upper())
        else:
            result.append(token.title())
    return " ".join(result)


def _get_display_name(name: str, metadata: "VizMetadata | None") -> str:
    """Return display_name from metadata if available, else format the raw name."""
    if metadata and metadata.display_names and name in metadata.display_names:
        return metadata.display_names[name]
    return _format_layer_name(name)


def _get_description(name: str, metadata: "VizMetadata | None") -> str | None:
    """Return description subtitle from metadata if available."""
    if metadata and metadata.descriptions and name in metadata.descriptions:
        return metadata.descriptions[name]
    return None


@dataclass
class DatasetSpec:
    name: str
    url: str
    data_type: Literal["raster", "vector"]
    rasterize: bool = False
    burn_value: int = 1
    is_wcs: bool = False
    wcs_layer: str = None
    is_wms: bool = False
    wms_layer: str = None
    labels_url: str | None = None  # URL to a CSV with VALUE,LABEL columns for legend labels
    secondary_url: str | None = None  # Second OPeNDAP URL for derived variables (e.g. rhsmin for VPD)
    secondary_netcdf_variable: str | None = None  # Variable name in the secondary NetCDF
    netcdf_variable: str | None = None  # Variable name in primary NetCDF (e.g. "tasmax")
    netcdf_months: list[int] | None = None  # Months to average over, e.g. [12,1,2,3] for winter
    resampling_method: Literal["bilinear", "nearest", "cubic"] | None = None  # None = auto-detect from data_type
    display_name: str | None = None  # Human-readable label for visualization panels (falls back to name)
    description: str | None = None   # One-line subtitle shown below the panel title
    # STAC fields — set is_stac=True to discover and download via a STAC catalog
    is_stac: bool = False
    stac_collection: str | None = None   # e.g. "sentinel-2-l2a"
    stac_asset: str | None = None        # asset key to download, e.g. "B08" or "visual"
    stac_datetime: str | None = None     # ISO-8601 range, e.g. "2023-06-01/2023-08-31"
    stac_query: dict | None = None       # extra search filters, e.g. {"eo:cloud_cover": {"lt": 20}}


@dataclass
class ExampleWorkflow:
    name: str
    datasets: list[DatasetSpec]
    target_crs: str
    target_extent: BBox
    target_resolution: float
    output_dir: Path
    create_visualization: bool = True
    verbose: bool = True
    # Optional boundary clipping — when set, outputs are clipped to the actual
    # boundary polygon instead of the rectangular target_extent bounding box.
    # Accepts any of:
    #   - A shorthand string: "state:Utah", "county:Larimer:Colorado",
    #     "place:Boulder:CO" — resolved via Census TIGER shapefiles.
    #   - A file path (str or Path) to a GeoJSON / shapefile boundary file.
    #   - None (default) — rectangular bounding-box clipping only.
    # When clip_boundary is set and target_extent is not explicitly provided,
    # run_harmonization_example will auto-compute target_extent from the
    # boundary's bounding box in target_crs.
    clip_boundary: str | Path | None = None


@dataclass
class GridSpec:
    crs: str
    extent: BBox
    resolution: float
    width: int
    height: int
    transform: object
    # Shapely geometry for boundary clipping.  None = rectangular bbox only.
    clip_geometry: object | None = None


@dataclass
class VizMetadata:
    """Optional metadata passed to create_visualization for richer output."""
    title: str                              # e.g. "Colorado Fire Risk"
    crs: str                                # e.g. "EPSG:4326"
    resolution: float                       # in CRS units (degrees or meters)
    extent: BBox                            # (xmin, ymin, xmax, ymax)
    display_names: dict[str, str] | None = None  # dataset name → plain label
    descriptions: dict[str, str] | None = None   # dataset name → subtitle text
    summary: str | None = None               # paragraph summary for the bottom panel
    boundary_geometry: object | None = None  # Shapely geometry for boundary overlay



def _log(msg: str, verbose: bool) -> None:
    if verbose:
        print(msg)


def build_grid_spec(
    target_crs: str,
    target_extent: BBox,
    target_resolution: float,
    clip_geometry: object | None = None,
) -> GridSpec:
    xmin, ymin, xmax, ymax = target_extent
    width = int(round((xmax - xmin) / target_resolution))
    height = int(round((ymax - ymin) / target_resolution))
    transform = from_bounds(xmin, ymin, xmax, ymax, width, height)
    return GridSpec(
        crs=target_crs,
        extent=target_extent,
        resolution=target_resolution,
        width=width,
        height=height,
        transform=transform,
        clip_geometry=clip_geometry,
    )


def download_file(url: str, output_dir: Path, verbose: bool = True) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / Path(url).name

    if output_path.exists():
        _log(f"Using existing download: {output_path}", verbose)
        return output_path

    _log(f"Downloading: {url}", verbose)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response, open(output_path, "wb") as f:
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 256  # 256 KB chunks
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if verbose and total > 0:
                pct = downloaded * 100 // total
                mb = downloaded / 1_048_576
                total_mb = total / 1_048_576
                print(f"\r  {mb:.1f} / {total_mb:.1f} MB ({pct}%)", end="", flush=True)
        if verbose and total > 0:
            print()  # newline after progress

    return output_path


def download_arcgis_image_server(
    url: str,
    output_dir: Path,
    bbox: tuple[float, float, float, float],
    width: int,
    height: int,
    verbose: bool = True,
) -> Path:
    """Download raster from ArcGIS ImageServer REST API.
    
    Args:
        url: ImageServer REST endpoint
        output_dir: Directory to save output
        bbox: Bounding box (xmin, ymin, xmax, ymax) in EPSG:4326
        width: Output width in pixels
        height: Output height in pixels
        verbose: Print progress messages
        
    Returns:
        Path to downloaded TIFF file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "wildfire_hazard.tif"
    
    if output_path.exists():
        _log(f"Using existing download: {output_path}", verbose)
        return output_path
    
    xmin, ymin, xmax, ymax = bbox
    export_url = (
        f"{url}/exportImage"
        f"?bbox={xmin},{ymin},{xmax},{ymax}"
        f"&bboxSR=4326"
        f"&size={width},{height}"
        f"&format=tif"
        f"&imageSR=4326"
        f"&f=image"
    )
    
    _log(f"Downloading from ArcGIS ImageServer: {url}", verbose)
    request = urllib.request.Request(export_url, headers={"User-Agent": "Mozilla/5.0"})
    
    # Download to temp file first
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        tmp_path = tmp.name
        with urllib.request.urlopen(request) as response:
            shutil.copyfileobj(response, tmp)
    
    # Read the downloaded file and add geotransform
    xmin, ymin, xmax, ymax = bbox
    transform = from_bounds(xmin, ymin, xmax, ymax, width, height)
    
    with rasterio.open(tmp_path) as src:
        data = src.read()
        meta = src.meta.copy()
        meta.update({
            "crs": "EPSG:4326",
            "transform": transform,
            "height": height,
            "width": width,
        })
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(data)
    
    # Clean up temp file
    Path(tmp_path).unlink()
    
    return output_path


def download_wms_coverage(
    wms_url: str,
    layer: str,
    bbox: tuple[float, float, float, float],
    crs: str,
    output_dir: Path,
    output_filename: str,
    width: int = None,
    height: int = None,
    verbose: bool = True,
) -> Path:
    """Download raster coverage from a WMS (Web Map Service).
    
    Args:
        wms_url: Base WMS endpoint URL
        layer: Layer name to request
        bbox: Bounding box (xmin, ymin, xmax, ymax) in the specified CRS
        crs: CRS code (e.g., "EPSG:4326")
        output_dir: Directory to save output
        output_filename: Name for the output file
        width: Optional width in pixels (height calculated proportionally if not provided)
        height: Optional height in pixels (width calculated proportionally if not provided)
        verbose: Print progress messages
        
    Returns:
        Path to downloaded GeoTIFF file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    
    if output_path.exists():
        _log(f"Using existing WMS download: {output_path}", verbose)
        return output_path
    
    # Calculate dimensions if not provided
    if width is None and height is None:
        width = 1000
    elif width is None:
        xmin, ymin, xmax, ymax = bbox
        aspect = (xmax - xmin) / (ymax - ymin)
        width = int(height * aspect)
    elif height is None:
        xmin, ymin, xmax, ymax = bbox
        aspect = (xmax - xmin) / (ymax - ymin)
        height = int(width / aspect)
    
    # Build WMS GetMap request
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": layer,
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "crs": crs,
        "width": width,
        "height": height,
        "format": "image/geotiff",
    }
    
    query_string = urllib.parse.urlencode(params)
    request_url = f"{wms_url}?{query_string}"
    
    _log(f"Downloading WMS coverage: {layer}", verbose)
    _log(f"  URL: {request_url[:100]}...", verbose)
    
    try:
        request = urllib.request.Request(request_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=300) as response:
            with open(output_path, "wb") as f:
                shutil.copyfileobj(response, f)
        _log(f"  Downloaded {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)", verbose)
        return output_path
    except Exception as e:
        _log(f"WMS request failed: {e}", verbose)
        raise RuntimeError(f"Failed to download WMS coverage: {e}")


def download_wcs_coverage(
    wcs_url: str,
    layer: str,
    bbox: tuple[float, float, float, float],
    crs: str,
    output_dir: Path,
    output_filename: str,
    width: int = None,
    height: int = None,
    verbose: bool = True,
) -> Path:
    """Download raster coverage from a WCS (Web Coverage Service).
    
    Args:
        wcs_url: Base WCS endpoint URL
        layer: Layer name to request
        bbox: Bounding box (xmin, ymin, xmax, ymax) in the specified CRS
        crs: CRS code (e.g., "EPSG:4326")
        output_dir: Directory to save output
        output_filename: Name for the output file
        width: Optional width in pixels (height calculated proportionally if not provided)
        height: Optional height in pixels (width calculated proportionally if not provided)
        verbose: Print progress messages
        
    Returns:
        Path to downloaded GeoTIFF file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    
    if output_path.exists():
        _log(f"Using existing WCS download: {output_path}", verbose)
        return output_path
    
    # Parse CRS to get EPSG code
    epsg_code = crs.split(":")[-1] if ":" in crs else crs
    
    # Calculate dimensions if not provided
    if width is None and height is None:
        # Default to reasonable size
        width = 1000
    elif width is None:
        # Calculate width based on aspect ratio
        xmin, ymin, xmax, ymax = bbox
        aspect = (xmax - xmin) / (ymax - ymin)
        width = int(height * aspect)
    elif height is None:
        # Calculate height based on aspect ratio
        xmin, ymin, xmax, ymax = bbox
        aspect = (xmax - xmin) / (ymax - ymin)
        height = int(width / aspect)
    
    # Build WCS GetCoverage request
    params = {
        "service": "WCS",
        "version": "2.0.1",
        "request": "GetCoverage",
        "coverageid": layer,
        "format": "image/geotiff",
        "subset": f"Long({bbox[0]},{bbox[2]})",
        "subset": f"Lat({bbox[1]},{bbox[3]})",
        "scalesize": f"Long({width}),Lat({height})",
    }
    
    # For WCS 1.x.x style requests (more commonly supported)
    wcs_111_params = {
        "service": "WCS",
        "version": "1.1.1",
        "request": "GetCoverage",
        "coverage": layer,
        "format": "GeoTIFF",
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "crs": crs,
        "width": width,
        "height": height,
    }
    
    # Try WCS 1.1.1 request first (more widely supported)
    query_string = urllib.parse.urlencode(wcs_111_params)
    request_url = f"{wcs_url}?{query_string}"
    
    _log(f"Downloading WCS coverage: {layer}", verbose)
    _log(f"  URL: {request_url[:100]}...", verbose)
    
    try:
        request = urllib.request.Request(request_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=300) as response:
            with open(output_path, "wb") as f:
                shutil.copyfileobj(response, f)
        _log(f"  Downloaded {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)", verbose)
        return output_path
    except Exception as e:
        _log(f"WCS 1.1.1 request failed: {e}", verbose)
        # Try WCS 2.0.1 style request
        _log("Trying WCS 2.0.1 request...", verbose)
        params_201 = {
            "service": "WCS",
            "version": "2.0.1",
            "request": "GetCoverage",
            "coverageId": layer,
            "format": "image/geotiff",
        }
        query_string = urllib.parse.urlencode(params_201)
        request_url = f"{wcs_url}?{query_string}"
        
        try:
            request = urllib.request.Request(request_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=300) as response:
                with open(output_path, "wb") as f:
                    shutil.copyfileobj(response, f)
            _log(f"  Downloaded {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)", verbose)
            return output_path
        except Exception as e2:
            _log(f"WCS 2.0.1 request also failed: {e2}", verbose)
            raise RuntimeError(f"Failed to download WCS coverage: {e2}")


def download_stac_item(
    catalog_url: str,
    collection: str,
    asset_key: str,
    bbox: BBox,
    output_dir: Path,
    datetime: str | None = None,
    query: dict | None = None,
    verbose: bool = True,
) -> Path:
    """Search a STAC catalog and download the best-matching asset as a GeoTIFF.

    Selects the item with the lowest ``eo:cloud_cover`` among those returned by
    the search (falls back to the first item if the property is absent).  COG
    assets are streamed via GDAL's vsicurl so only the requested bbox is read.

    Args:
        catalog_url: Root STAC API URL, e.g.
            "https://planetarycomputer.microsoft.com/api/stac/v1"
        collection: STAC collection ID, e.g. "sentinel-2-l2a" or "landsat-c2-l2".
        asset_key: Asset key to download, e.g. "B08", "SR_B4", "visual".
        bbox: Bounding box (xmin, ymin, xmax, ymax) in EPSG:4326.
        output_dir: Directory to save the downloaded file.
        datetime: ISO-8601 date or range, e.g. "2023-06-01/2023-08-31".
        query: Extra STAC search filter properties,
            e.g. {"eo:cloud_cover": {"lt": 20}}.
        verbose: Print progress messages.

    Returns:
        Path to the downloaded GeoTIFF.
    """
    try:
        import pystac_client
    except ImportError:
        raise ImportError("pystac-client is required for STAC downloads: pip install pystac-client")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{collection}_{asset_key}.tif"

    if output_path.exists():
        _log(f"Using existing STAC download: {output_path.name}", verbose)
        return output_path

    _log(f"Searching STAC catalog: {catalog_url}", verbose)
    _log(f"  collection={collection}  asset={asset_key}  datetime={datetime}", verbose)

    client = pystac_client.Client.open(catalog_url)
    search = client.search(
        collections=[collection],
        bbox=list(bbox),
        datetime=datetime,
        query=query or {},
        max_items=50,
    )
    items = list(search.items())
    if not items:
        raise FileNotFoundError(
            f"No STAC items found for collection={collection!r} bbox={bbox} datetime={datetime!r}"
        )

    # Pick the least cloudy item
    def _cloud_cover(item):
        return item.properties.get("eo:cloud_cover", 0) or 0

    best = min(items, key=_cloud_cover)
    _log(f"  Selected item: {best.id}  cloud_cover={_cloud_cover(best):.1f}%", verbose)

    if asset_key not in best.assets:
        available = list(best.assets.keys())
        raise KeyError(
            f"Asset {asset_key!r} not found in item {best.id!r}. "
            f"Available assets: {available}"
        )

    asset_href = best.assets[asset_key].href
    _log(f"  Downloading asset: {asset_href}", verbose)

    # Stream via rasterio (works for COGs without downloading the full file)
    with rasterio.open(asset_href) as src:
        data = src.read()
        meta = src.meta.copy()
        meta.update({"driver": "GTiff"})
        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(data)

    _log(f"  Saved {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)", verbose)
    return output_path


def extract_archive_if_needed(path: Path, output_dir: Path, verbose: bool = True) -> Path:
    if path.suffix.lower() != ".zip":
        return path.parent

    extract_dir = output_dir / path.stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    if any(extract_dir.iterdir()):
        _log(f"Using existing extraction: {extract_dir}", verbose)
        return extract_dir

    _log(f"Extracting: {path.name}", verbose)
    with zipfile.ZipFile(path, "r") as zf:
        zf.extractall(extract_dir)

    return extract_dir


def discover_dataset_file(dataset_dir: Path, data_type: str) -> Path:
    if data_type == "raster":
        candidates = (
            list(dataset_dir.rglob("*.tif"))
            + list(dataset_dir.rglob("*.tiff"))
            + list(dataset_dir.rglob("*.img"))
        )
    else:
        candidates = (
            list(dataset_dir.rglob("*.geojson"))
            + list(dataset_dir.rglob("*.shp"))
        )

    if not candidates:
        raise FileNotFoundError(f"No {data_type} dataset found in {dataset_dir}")

    return candidates[0]


# Known color table URLs for common datasets
COLOR_TABLE_URLS = {
    "fbfm40": "https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM40.csv",
    "fbfm13": "https://landfire.gov/sites/default/files/CSV/2024/LF2024_FBFM13.csv",
    "evc": "https://landfire.gov/sites/default/files/CSV/2024/LF2024_EVC.csv",
    "evh": "https://landfire.gov/sites/default/files/CSV/2024/LF2024_EVH.csv",
}


def discover_color_map(dataset_dir: Path, dataset_name: str = "") -> dict | None:
    """Discover and parse color map file from the dataset directory.
    
    Looks for common color map file formats:
    - .clr (ESRI color map files)
    - .txt (text-based color maps)
    - .csv (comma-separated color tables like Landfire)
    - .qml (QGIS style files)
    
    Also tries to download from known URLs for Landfire datasets.
    
    Args:
        dataset_dir: Directory to search for color map files
        dataset_name: Optional name of the dataset to help find color table URLs
        
    Returns:
        Dict mapping category values to RGB colors, or None if not found
    """
    # Look for .clr files (ESRI color map format)
    clr_files = list(dataset_dir.rglob("*.clr"))
    if clr_files:
        return _parse_esri_color_map(clr_files[0])
    
    # Look for .txt files that might be color maps
    txt_files = list(dataset_dir.rglob("*.txt"))
    for txt_file in txt_files:
        # Check if it looks like a color map file
        try:
            with open(txt_file, 'r') as f:
                first_lines = [f.readline() for _ in range(5)]
            # ESRI color maps often have category values as first column
            if any(line.strip().split()[:3] for line in first_lines if line.strip()):
                result = _parse_text_color_map(txt_file)
                if result:
                    return result
        except Exception:
            continue
    
    # Look for CSV files that might be color tables (e.g., Landfire)
    csv_files = list(dataset_dir.rglob("*.csv"))
    for csv_file in csv_files:
        result = _parse_csv_color_map(csv_file)
        if result:
            return result
    
    # Try to download from known URLs based on dataset name
    name_lower = dataset_name.lower()
    for key, url in COLOR_TABLE_URLS.items():
        if key in name_lower:
            _log(f"Attempting to download color table from {url}", True)
            try:
                # Download to a temp file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                    tmp_path = tmp.name
                    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(request) as response:
                        shutil.copyfileobj(response, tmp)
                    result = _parse_csv_color_map(Path(tmp_path))
                    Path(tmp_path).unlink()
                    if result:
                        return result
            except Exception as e:
                _log(f"Could not download color table: {e}", True)
                continue
    
    return None


def _parse_esri_color_map(clr_path: Path) -> dict:
    """Parse ESRI .clr color map file.
    
    Format: category R G B
    """
    color_map = {}
    try:
        with open(clr_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        category = int(parts[0])
                        r = int(parts[1])
                        g = int(parts[2])
                        b = int(parts[3])
                        color_map[category] = (r, g, b)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Warning: Could not parse color map {clr_path}: {e}")
        return None
    
    return color_map if color_map else None


def _parse_text_color_map(txt_path: Path) -> dict | None:
    """Parse text-based color map file.
    
    Attempts to parse common formats.
    """
    color_map = {}
    try:
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        # Try to parse as category R G B
                        category = int(parts[0])
                        r = int(parts[1])
                        g = int(parts[2])
                        b = int(parts[3])
                        color_map[category] = (r, g, b)
                    except ValueError:
                        continue
    except Exception:
        return None
    
    return color_map if color_map else None


def _parse_csv_color_map(csv_path: Path) -> dict | None:
    """Parse CSV-based color map file (e.g., Landfire color tables).
    
    Expected format: VALUE,FBFM40,R,G,B,RED,GREEN,BLUE
    or similar with VALUE and R, G, B columns.
    """
    color_map = {}
    try:
        import csv
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if not row:
                    continue
                # First non-empty row is the header
                if header is None:
                    header = [col.strip().upper() for col in row]
                    # Look for VALUE and R, G, B columns
                    if 'VALUE' not in header or 'R' not in header:
                        return None
                    continue
                
                # Skip rows that don't have enough columns
                if len(row) < len(header):
                    continue
                
                try:
                    # Find column indices
                    value_idx = header.index('VALUE')
                    r_idx = header.index('R')
                    g_idx = header.index('G')
                    b_idx = header.index('B')
                    
                    # Parse values
                    value = int(row[value_idx])
                    r = int(row[r_idx])
                    g = int(row[g_idx])
                    b = int(row[b_idx])
                    
                    # Skip NoData values
                    if value < 0 or value == -9999:
                        continue
                    
                    color_map[value] = (r, g, b)
                except (ValueError, IndexError):
                    continue
    except Exception as e:
        print(f"Warning: Could not parse CSV color map {csv_path}: {e}")
        return None
    
    return color_map if color_map else None


def _fetch_jja_subset(url: str, variable: str, xmin: float, xmax: float, ymin: float, ymax: float):
    """Open a MACAv2 OPeNDAP URL, subset to bbox and JJA months, and download.

    Uses chunks so xarray only fetches the selected slice, not the full CONUS dataset.
    Intended to be called in a thread alongside a sibling fetch.
    """
    import xarray as xr
    ds = xr.open_dataset(url, engine="netcdf4", chunks={"time": 12})
    arr = ds[variable].sel(
        lon=slice(xmin + 360, xmax + 360),  # MACAv2 uses 0–360 longitude
        lat=slice(ymin, ymax),
    )
    jja = arr.sel(time=arr.time.dt.month.isin([6, 7, 8]))
    result = jja.compute()
    ds.close()
    return result


def compute_vpd_geotiff(
    tasmax_url: str,
    rhsmin_url: str,
    bbox: BBox,
    output_path: Path,
    tasmax_var: str = "air_temperature",
    rhsmin_var: str = "relative_humidity",
    verbose: bool = True,
) -> Path:
    """Download MACAv2 tasmax + rhsmin via OPeNDAP, compute JJA mean VPD, save as GeoTIFF.

    Both variables are fetched in parallel. Only the Colorado bbox and JJA months are
    downloaded (not the full CONUS dataset).

    VPD (kPa) = es(Tmax) * (1 - RHmin / 100)
    where es(T) = 0.6108 * exp(17.27 * T_c / (T_c + 237.3))  [Buck equation, T in Celsius]

    Args:
        tasmax_url: OPeNDAP URL for MACAv2 tasmax variable
        rhsmin_url: OPeNDAP URL for MACAv2 rhsmin variable
        bbox: Bounding box (xmin, ymin, xmax, ymax) in EPSG:4326 to subset before downloading
        output_path: Path to save the output GeoTIFF
        tasmax_var: Variable name inside the tasmax NetCDF file
        rhsmin_var: Variable name inside the rhsmin NetCDF file
        verbose: Print progress messages

    Returns:
        Path to the output GeoTIFF
    """
    from concurrent.futures import ThreadPoolExecutor

    xmin, ymin, xmax, ymax = bbox

    _log("Fetching MACAv2 tasmax + rhsmin in parallel (JJA, Colorado bbox)...", verbose)
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_tmax = pool.submit(_fetch_jja_subset, tasmax_url, tasmax_var, xmin, xmax, ymin, ymax)
        f_rh   = pool.submit(_fetch_jja_subset, rhsmin_url, rhsmin_var, xmin, xmax, ymin, ymax)
        tmax_jja = f_tmax.result()
        rh_jja   = f_rh.result()

    # Filter to JJA (June=6, July=7, August=8) — peak fire season
    _log("Computing JJA mean VPD across 2006-2099...", verbose)

    # Convert tasmax from Kelvin to Celsius
    tmax_c = tmax_jja - 273.15

    # Saturation vapor pressure [kPa] via Buck equation
    es = 0.6108 * np.exp(17.27 * tmax_c / (tmax_c + 237.3))

    # VPD [kPa]
    vpd = es * (1.0 - rh_jja / 100.0)

    # Mean over all JJA time steps
    vpd_mean = vpd.mean(dim="time").compute()

    values = vpd_mean.values.astype("float32")  # shape: (lat, lon)

    # Build transform — MACAv2 lats are ascending, rasterio needs top-left origin
    lons = (vpd_mean.coords["lon"].values - 360.0)  # convert back to -180..180
    lats = vpd_mean.coords["lat"].values
    lon_res = float(lons[1] - lons[0])
    lat_res = float(lats[1] - lats[0])
    transform = rasterio.transform.from_origin(
        lons[0] - lon_res / 2,
        lats[-1] + abs(lat_res) / 2,
        lon_res,
        abs(lat_res),
    )
    # Flip so north is up (rasterio convention: row 0 = northernmost)
    values = np.flipud(values)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path, "w",
        driver="GTiff",
        height=values.shape[0],
        width=values.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(values, 1)

    _log(
        f"  VPD GeoTIFF saved: {output_path.name} "
        f"({values.shape[1]}x{values.shape[0]} pixels, ~4 km native resolution)",
        verbose,
    )
    ds_tmax.close()
    ds_rh.close()
    return output_path


def fetch_netcdf_seasonal_geotiff(
    url: str,
    variable: str,
    bbox: BBox,
    output_path: Path,
    months: list[int] | None = None,
    verbose: bool = True,
) -> Path:
    """Download a single MACAv2 variable via OPeNDAP, compute seasonal mean, save as GeoTIFF.

    Use this when the desired variable is pre-computed in the catalog (e.g. ``vpd``,
    ``tasmax``, ``pr``).  For derived quantities that require two inputs use
    ``compute_vpd_geotiff`` instead.

    Args:
        url: OPeNDAP URL for the NetCDF dataset.
        variable: Variable name inside the file (e.g. ``"vpd"``, ``"pr"``).
        bbox: Bounding box (xmin, ymin, xmax, ymax) in EPSG:4326.
        output_path: Path to save the output GeoTIFF.
        months: List of month numbers to average over, e.g. ``[12, 1, 2, 3]`` for
            winter or ``[6, 7, 8]`` for summer.  Defaults to all months (annual mean).
        verbose: Print progress messages.

    Returns:
        Path to the output GeoTIFF.
    """
    import xarray as xr
    season_label = f"months={months}" if months else "annual"
    _log(f"Fetching {variable} via OPeNDAP ({season_label}, bbox subset)...", verbose)
    xmin, ymin, xmax, ymax = bbox

    ds = xr.open_dataset(url, engine="netcdf4", chunks={"time": 12})
    arr = ds[variable].sel(
        lon=slice(xmin + 360, xmax + 360),
        lat=slice(ymin, ymax),
    )
    if months:
        arr = arr.sel(time=arr.time.dt.month.isin(months))
    data = arr.compute()
    ds.close()

    values = data.mean(dim="time").values.astype("float32")

    lons = data.coords["lon"].values - 360.0  # convert 0–360 → −180–180
    lats = data.coords["lat"].values
    lon_res = float(lons[1] - lons[0])
    lat_res = float(lats[1] - lats[0])
    transform = rasterio.transform.from_origin(
        lons[0] - lon_res / 2,
        lats[-1] + abs(lat_res) / 2,
        lon_res,
        abs(lat_res),
    )
    values = np.flipud(values)  # row 0 = northernmost

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        output_path, "w",
        driver="GTiff",
        height=values.shape[0],
        width=values.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(values, 1)

    _log(
        f"  Saved {output_path.name} "
        f"({values.shape[1]}x{values.shape[0]} pixels, ~4 km native resolution)",
        verbose,
    )
    return output_path


def resolve_clip_boundary(
    clip_boundary: str | Path,
    target_crs: str,
    verbose: bool = True,
) -> tuple[object, BBox]:
    """Resolve a ``clip_boundary`` specifier to a Shapely geometry and bbox.

    Accepts:
      - ``"state:Utah"`` / ``"county:Larimer:Colorado"`` / ``"place:Boulder:CO"``
        — resolved via Census TIGER shapefiles (uses ``scripts/region_extent``).
      - A file path (str or Path) to a GeoJSON or shapefile boundary file.

    Returns
    -------
    (geometry, bbox)
        *geometry* is a Shapely geometry (Multi)Polygon in *target_crs*.
        *bbox* is ``(xmin, ymin, xmax, ymax)`` — the tight bounding box of that
        geometry in *target_crs*.
    """
    clip_str = str(clip_boundary)

    # Shorthand strings: "state:Utah", "county:Larimer:Colorado", "place:Boulder:CO"
    if clip_str.startswith(("state:", "county:", "place:")):
        parts = clip_str.split(":")
        kind = parts[0]
        if kind == "state" and len(parts) == 2:
            name, state_arg = parts[1], None
        elif kind in ("county", "place") and len(parts) == 3:
            name, state_arg = parts[1], parts[2]
        else:
            raise ValueError(
                f"Invalid clip_boundary shorthand: {clip_str!r}. "
                f"Expected 'state:<name>', 'county:<name>:<state>', or 'place:<name>:<state>'."
            )

        # Import the programmatic API from region_extent
        import importlib.util, sys as _sys
        spec = importlib.util.spec_from_file_location(
            "region_extent",
            Path(__file__).resolve().parent.parent / "scripts" / "region_extent.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        _log(f"Resolving clip boundary: {clip_str} (CRS={target_crs})", verbose)
        gdf = mod.resolve_boundary(kind, name, state=state_arg, target_crs=target_crs)
    else:
        # File path
        boundary_path = Path(clip_str)
        if not boundary_path.exists():
            raise FileNotFoundError(f"Clip boundary file not found: {boundary_path}")
        _log(f"Loading clip boundary from file: {boundary_path}", verbose)
        gdf = gpd.read_file(boundary_path)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        gdf = gdf.to_crs(target_crs)

    # Dissolve to a single geometry (union of all features)
    geom = gdf.geometry.union_all()
    xmin, ymin, xmax, ymax = gdf.total_bounds

    # Round bbox appropriately for the CRS (cast to plain float for clean repr)
    if gdf.crs.is_geographic:
        bbox = (round(float(xmin), 4), round(float(ymin), 4), round(float(xmax), 4), round(float(ymax), 4))
    else:
        bbox = (round(float(xmin), 1), round(float(ymin), 1), round(float(xmax), 1), round(float(ymax), 1))

    _log(f"  Boundary bbox in {target_crs}: {bbox}", verbose)
    return geom, bbox


def harmonize_raster(
    input_path: Path,
    grid: GridSpec,
    output_path: Path,
    resampling_method: str | None = None,
    verbose: bool = True,
) -> Path:
    """Harmonize raster to target grid, clipping to extent first for efficiency.

    When ``grid.clip_geometry`` is set (a Shapely polygon), pixels outside the
    boundary are set to nodata after reprojection — producing output that
    follows the actual boundary shape, not just a rectangular bounding box.

    Args:
        input_path: Source raster file.
        grid: Target grid (CRS, extent, resolution, optional clip_geometry).
        output_path: Where to write the harmonized GeoTIFF.
        resampling_method: One of "bilinear", "nearest", or "cubic".
            Use "nearest" for categorical data (land cover, fuel models) to avoid
            interpolating between class codes.  Use "bilinear" or "cubic" for
            continuous data (temperature, VPD, elevation).  None defaults to
            "bilinear".
        verbose: Print progress messages.
    """
    _log(f"Harmonizing raster: {input_path.name}", verbose)

    with rasterio.open(input_path) as src:
        xmin, ymin, xmax, ymax = grid.extent
        
        # Define target bounds in target CRS
        target_bounds = box(xmin, ymin, xmax, ymax)
        
        # If source CRS differs, transform bounds
        if src.crs != grid.crs:
            from rasterio.warp import transform_bounds
            left, bottom, right, top = transform_bounds(
                grid.crs, src.crs, xmin, ymin, xmax, ymax
            )
            src_bounds = box(left, bottom, right, top)
        else:
            src_bounds = target_bounds
        
        # Try to clip source data to bounds before reprojecting
        try:
            out_image, out_transform = mask.mask(
                src, [src_bounds], crop=True, all_touched=True
            )
            
            if out_image.shape[1] == 0 or out_image.shape[2] == 0:
                # Clipping resulted in empty data, use full source
                _log(f"  Clipping resulted in empty data, using full source", verbose)
                out_image = src.read()
                out_transform = src.transform
        except (ValueError, Exception) as e:
            # Clipping failed (e.g., bounds don't overlap or WMS axis order issue), use full source
            _log(f"  Clipping failed: {e}, using full source", verbose)
            out_image = src.read()
            out_transform = src.transform
        
        # Choose resampling algorithm.
        # Categorical data (integer dtype, e.g. fuel model codes) must use nearest-
        # neighbour to avoid interpolating between class codes.  Continuous data
        # (float) defaults to bilinear.
        _resampling_map = {
            "bilinear": Resampling.bilinear,
            "nearest": Resampling.nearest,
            "cubic": Resampling.cubic,
        }
        if resampling_method is not None:
            chosen = _resampling_map.get(resampling_method, Resampling.bilinear)
        elif np.issubdtype(out_image.dtype, np.integer):
            chosen = Resampling.nearest
            _log(f"  Integer dtype detected — using nearest-neighbour resampling", verbose)
        else:
            chosen = Resampling.bilinear

        # Determine nodata value.  Pixels outside the source extent are filled with
        # this value after reprojection.  Preserving the source nodata prevents 0
        # (a valid class code in many datasets) from silently masking real data.
        src_nodata = src.nodata
        if src_nodata is None:
            src_nodata = 0 if np.issubdtype(out_image.dtype, np.integer) else np.nan

        # Now reproject the clipped data to target grid
        dst = np.full(
            (out_image.shape[0], grid.height, grid.width),
            fill_value=src_nodata,
            dtype=out_image.dtype,
        )

        reproject(
            source=out_image,
            destination=dst,
            src_transform=out_transform,
            src_crs=src.crs,
            dst_transform=grid.transform,
            dst_crs=grid.crs,
            resampling=chosen,
            src_nodata=src_nodata,
            dst_nodata=src_nodata,
        )

        meta = src.meta.copy()
        meta.update(
            {
                "driver": "GTiff",
                "height": grid.height,
                "width": grid.width,
                "transform": grid.transform,
                "crs": grid.crs,
                "nodata": src_nodata,
            }
        )

    # Apply boundary clipping if a clip geometry is provided.
    # This masks pixels outside the actual boundary polygon to nodata,
    # so the output follows the real boundary shape, not just its bbox.
    if grid.clip_geometry is not None:
        from shapely.geometry import mapping
        _log("  Applying boundary clip (masking pixels outside boundary to nodata)", verbose)
        clip_shapes = [mapping(grid.clip_geometry)]
        for band_idx in range(dst.shape[0]):
            band = dst[band_idx]
            # Build a binary mask: 1 inside boundary, 0 outside
            clip_mask = rasterize(
                [(grid.clip_geometry, 1)],
                out_shape=(grid.height, grid.width),
                transform=grid.transform,
                fill=0,
                all_touched=True,
                dtype="uint8",
            )
            band[clip_mask == 0] = src_nodata
            dst[band_idx] = band

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_path, "w", **meta) as dst_file:
        dst_file.write(dst)

    return output_path


def rasterize_vector_to_grid(
    input_path: Path,
    grid: GridSpec,
    output_path: Path,
    burn_value: int = 1,
    verbose: bool = True,
) -> Path:
    _log(f"Rasterizing vector: {input_path.name}", verbose)

    gdf = gpd.read_file(input_path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    if str(gdf.crs) != grid.crs:
        gdf = gdf.to_crs(grid.crs)

    # Clip to boundary polygon if available, otherwise use rectangular extent
    if grid.clip_geometry is not None:
        _log("  Clipping vector to boundary polygon", verbose)
        gdf.geometry = gdf.geometry.make_valid()
        gdf = gpd.clip(gdf, grid.clip_geometry)
    else:
        xmin, ymin, xmax, ymax = grid.extent
        clip_geom = box(xmin, ymin, xmax, ymax)
        gdf = gdf[gdf.intersects(clip_geom)].copy()

    shapes = [(geom, burn_value) for geom in gdf.geometry if geom is not None and not geom.is_empty]
    burned = rasterize(
        shapes=shapes,
        out_shape=(grid.height, grid.width),
        transform=grid.transform,
        fill=0,
        all_touched=True,
        dtype="uint8",
    )

    meta = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": 1,
        "dtype": "uint8",
        "crs": grid.crs,
        "transform": grid.transform,
        "nodata": 0,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(burned, 1)

    return output_path


def harmonize_vector(
    input_path: Path,
    grid: GridSpec,
    output_path: Path,
    verbose: bool = True,
) -> Path:
    """Harmonize vector to target CRS and clip to target extent or boundary.

    When ``grid.clip_geometry`` is set, features are clipped to the actual
    boundary polygon (e.g. a state outline) rather than just the rectangular
    bounding box.

    Args:
        input_path: Path to input vector file
        grid: Target grid specification (with optional clip_geometry)
        output_path: Path to save harmonized vector
        verbose: Print progress messages

    Returns:
        Path to harmonized vector file
    """
    _log(f"Harmonizing vector: {input_path.name}", verbose)

    gdf = gpd.read_file(input_path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    # Reproject to target CRS if needed
    if str(gdf.crs) != grid.crs:
        gdf = gdf.to_crs(grid.crs)

    # Clip to boundary polygon if available, otherwise use rectangular extent
    if grid.clip_geometry is not None:
        _log("  Clipping vector to boundary polygon", verbose)
        gdf.geometry = gdf.geometry.make_valid()
        gdf = gpd.clip(gdf, grid.clip_geometry)
    else:
        xmin, ymin, xmax, ymax = grid.extent
        clip_geom = box(xmin, ymin, xmax, ymax)
        gdf = gdf[gdf.intersects(clip_geom)].copy()

    # Save harmonized vector
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")

    _log(f"  Saved harmonized vector: {output_path.name} ({len(gdf)} features)", verbose)

    return output_path


def _create_binary_mask(data: np.ndarray) -> np.ndarray:
    """Create a mask for binary data (0s and 1s), returning only 1s as visible."""
    unique_vals = np.unique(data)
    if len(unique_vals) <= 2 and all(v in [0, 1, data.dtype.type(0), data.dtype.type(1)] for v in unique_vals):
        return np.ma.masked_equal(data, 0)
    return data


# Filename contract — the website build hook (hooks.py) and docs/workflows/<name>.md
# template both expect these exact filenames. Do NOT change them or the workflow's
# image silently fails to appear on the site. Pass output_dir to the public APIs;
# the filenames are constructed internally so callers can't accidentally diverge.
HARMONIZED_VIZ_PNG = "harmonized_visualization.png"
HARMONIZED_VIZ_HTML = "harmonized_visualization.html"


def create_visualization(
    outputs: list[tuple[str, Path]],
    output_dir: Path,
    verbose: bool = True,
    *,
    metadata: VizMetadata | None = None,
) -> Path | None:
    """Create a static PNG visualization with subplots for each layer.

    The filename is hardcoded to ``harmonized_visualization.png`` (see
    HARMONIZED_VIZ_PNG above). Pass the project's ``output_dir``; the function
    writes the PNG inside it.

    Parameters
    ----------
    metadata : VizMetadata, optional
        When provided, adds a title, scale bars, unit labels, and a summary
        footer to the PNG. Backwards compatible — omit for legacy behavior.
    """
    output_path = output_dir / HARMONIZED_VIZ_PNG
    try:
        return _create_visualization_impl(outputs, output_path, verbose, metadata=metadata)
    except Exception as e:
        _log(f"Error creating visualization: {e}", verbose)
        import traceback
        traceback.print_exc()
        return None


def _load_color_map_from_output_dir(output_path: Path) -> None:
    """Load DISCOVERED_COLOR_MAP and DISCOVERED_LABELS from saved JSON files if not already set."""
    import json
    import src.geospatial_harmonizer as _self
    if _self.DISCOVERED_COLOR_MAP is None:
        for json_path in output_path.parent.glob("*_color_map.json"):
            with open(json_path) as f:
                color_map_json = json.load(f)
            _self.DISCOVERED_COLOR_MAP = {int(k): tuple(v) for k, v in color_map_json.items()}
            break
    if _self.DISCOVERED_LABELS is None:
        for json_path in output_path.parent.glob("*_labels.json"):
            with open(json_path) as f:
                labels_json = json.load(f)
            _self.DISCOVERED_LABELS = {int(k): v for k, v in labels_json.items()}
            break


def _create_visualization_impl(
    outputs: list[tuple[str, Path]],
    output_path: Path,
    verbose: bool = True,
    *,
    metadata: VizMetadata | None = None,
) -> Path:
    """Internal implementation of PNG visualization creation."""
    _log("Creating static PNG visualization...", verbose)
    _load_color_map_from_output_dir(output_path)

    from matplotlib.gridspec import GridSpec
    from matplotlib.patches import FancyBboxPatch, Patch

    _LETTER_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    n = len(outputs)
    # Use 2-column layout for 4 datasets, otherwise cap at 3
    cols = 2 if n == 4 else min(3, n)
    rows = (n + cols - 1) // cols

    # Layout: per-layer panels in a grid, composite + summary in the bottom row
    # Use a 10-column grid so the bottom row can split 5:5 (map left, info right)
    fig = plt.figure(figsize=(8 * cols, 6 * rows + 6))
    gs = GridSpec(rows + 1, 10, figure=fig, hspace=0.5, wspace=0.4,
                  height_ratios=[6] * rows + [6])
    # Per-layer panels: map to the 10-column grid based on actual cols
    _col_map = {
        2: [(0, 5), (5, 10)],
        3: [(0, 3), (3, 7), (7, 10)],
    }
    _spans = _col_map.get(cols, [(i * (10 // cols), (i + 1) * (10 // cols)) for i in range(cols)])
    axes = []
    for i in range(n):
        r, c = i // cols, i % cols
        s0, s1 = _spans[c]
        axes.append(fig.add_subplot(gs[r, s0:s1]))
    for i in range(n, rows * cols):
        r, c = i // cols, i % cols
        s0, s1 = _spans[c]
        fig.add_subplot(gs[r, s0:s1]).set_visible(False)
    # Bottom row: composite map (left 5 cols) + info panel (right 5 cols)
    ax_composite = fig.add_subplot(gs[rows, 0:5])
    ax_info = fig.add_subplot(gs[rows, 5:10])

    # Overall title + subtitle
    if metadata:
        fig.suptitle(metadata.title, fontsize=22, fontweight='bold', y=0.98)
        fig.subplots_adjust(top=0.93)

    # Determine CRS string for scale bars (from metadata or from first raster)
    _scale_crs = metadata.crs if metadata else None
    _scale_extent = metadata.extent if metadata else None
    _boundary = metadata.boundary_geometry if metadata else None

    def _add_panel_frame(ax):
        """Draw a rounded border around a panel."""
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('#444444')
            spine.set_linewidth(1.5)

    def _add_letter_label(ax, letter):
        """Add a circled letter label (A, B, C...) in the upper-left corner."""
        ax.text(0.03, 0.95, letter, transform=ax.transAxes,
                fontsize=13, fontweight='bold', va='top', ha='left',
                bbox=dict(boxstyle='circle,pad=0.3', facecolor='white',
                          edgecolor='#333333', linewidth=1.5),
                zorder=100)

    for i, (name, path) in enumerate(outputs):
        _log(f"  Processing layer {i+1}/{len(outputs)}: {name}", verbose)
        ax = axes[i]
        display = _get_display_name(name, metadata)
        layer_bounds = None

        # Handle vector files
        if path.suffix.lower() in ['.geojson', '.json', '.shp']:
            style = _get_vector_style(name)
            gdf = gpd.read_file(path)
            gdf.plot(ax=ax, color=style["color"], edgecolor='black',
                    linewidth=0.5, alpha=style["fillOpacity"])

            # Legend for vector panel
            legend_patch = Patch(facecolor=style["color"], edgecolor='black',
                                alpha=style["fillOpacity"], label=display)
            ax.legend(handles=[legend_patch], loc='upper left',
                      bbox_to_anchor=(1.01, 1), borderaxespad=0,
                      fontsize=10, framealpha=0.95, edgecolor='#cccccc')

            desc = _get_description(name, metadata)
            title_str = f"{display}\n{desc}" if desc else display
            ax.set_title(title_str, fontsize=14, fontweight='bold', pad=8,
                         linespacing=1.6)
            if desc:
                # Make subtitle lighter
                ax.title.set_fontsize(12)
            ax.axis("off")

            # Boundary overlay
            if _boundary is not None:
                try:
                    _add_boundary_overlay(ax, _boundary, data_shape=None,
                                          extent=gdf.total_bounds)
                except Exception:
                    pass

            # Scale bar + frame + letter
            tb = gdf.total_bounds
            layer_bounds = (tb[0], tb[1], tb[2], tb[3])
            crs_for_bar = _scale_crs or (gdf.crs.to_string() if gdf.crs else None)
            if layer_bounds and crs_for_bar:
                _add_scale_bar(ax, layer_bounds, crs_for_bar)
            _add_panel_frame(ax)
            _add_letter_label(ax, _LETTER_LABELS[i])
            continue

        # Handle raster files
        with rasterio.open(path) as src:
            data = src.read(1)
            bnds = src.bounds
            layer_bounds = (bnds.left, bnds.bottom, bnds.right, bnds.top)
            if _scale_crs is None:
                _scale_crs = src.crs.to_string() if src.crs else None

        # imshow extent in [left, right, bottom, top] — renders in geo-coordinates
        raster_extent = [bnds.left, bnds.right, bnds.bottom, bnds.top]

        style = _get_layer_style(name, data, i)

        if style["solid_color"] is not None:
            rgba_image = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.float32)
            r, g, b, a = style["solid_color"]
            rgba_image[:, :, 0] = r
            rgba_image[:, :, 1] = g
            rgba_image[:, :, 2] = b
            rgba_image[:, :, 3] = (data == 1).astype(float) * style["alpha"]
            ax.imshow(rgba_image, origin='upper', extent=raster_extent, aspect='equal')

            legend_elements = [Patch(facecolor=(r, g, b, a), label=display)]
            ax.legend(handles=legend_elements, loc='upper left',
                      bbox_to_anchor=(1.01, 1), borderaxespad=0,
                      fontsize=10, framealpha=0.95, edgecolor='#cccccc')
        else:
            import matplotlib.cm as cm
            from matplotlib.colors import BoundaryNorm, ListedColormap

            vmin = style["vmin"] if style["vmin"] is not None else np.nanmin(data)
            vmax = style["vmax"] if style["vmax"] is not None else np.nanmax(data)
            unique_vals = np.unique(data[data > 0])
            is_categorical = len(unique_vals) > 20
            masked_data = np.ma.masked_equal(data, 0)

            if is_categorical and "fbfm" in name.lower():
                import src.geospatial_harmonizer as _self
                labels_map = _self.DISCOVERED_LABELS or {}
                all_cats = sorted([int(v) for v in unique_vals.tolist()])
                if "color_map" in style and style["color_map"]:
                    color_map = style["color_map"]
                    colors = [(color_map[c][0]/255, color_map[c][1]/255, color_map[c][2]/255)
                              if c in color_map else (0.7, 0.7, 0.7)
                              for c in all_cats]
                    cmap = ListedColormap(colors)
                    color_bounds = [c - 0.5 for c in all_cats] + [all_cats[-1] + 0.5]
                    norm = BoundaryNorm(color_bounds, cmap.N)
                    im = ax.imshow(masked_data, cmap=cmap, norm=norm, alpha=style["alpha"],
                                   extent=raster_extent, aspect='equal')
                    named_cats = [c for c in all_cats if labels_map.get(c, str(c)) != str(c) and c in color_map]
                    legend_handles = [
                        Patch(facecolor=(color_map[c][0]/255, color_map[c][1]/255, color_map[c][2]/255),
                              label=labels_map[c])
                        for c in named_cats
                    ]
                else:
                    n_colors = len(all_cats)
                    cmap = cm.get_cmap("nipy_spectral", n_colors)
                    color_bounds = [c - 0.5 for c in all_cats] + [all_cats[-1] + 0.5]
                    norm = BoundaryNorm(color_bounds, cmap.N)
                    im = ax.imshow(masked_data, cmap=cmap, norm=norm, alpha=style["alpha"],
                                   extent=raster_extent, aspect='equal')
                    named_cats = [c for c in all_cats if labels_map.get(c, str(c)) != str(c)]
                    legend_handles = [
                        Patch(facecolor=cmap(norm(c)), label=labels_map[c])
                        for c in named_cats
                    ]
                ax.legend(
                    handles=legend_handles,
                    loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0,
                    fontsize=10, ncol=2, frameon=True, edgecolor='#cccccc',
                    title='Fuel Model', title_fontsize=10,
                    handlelength=1, handleheight=1, handletextpad=0.4, columnspacing=0.5,
                )
            else:
                cmap = cm.get_cmap(style["colormap"])
                masked_data = np.ma.masked_equal(data, 0)
                im = ax.imshow(masked_data, cmap=cmap, vmin=vmin, vmax=vmax, alpha=style["alpha"],
                               extent=raster_extent, aspect='equal')
                cb = plt.colorbar(im, ax=ax, shrink=0.6, aspect=20)
                units = style.get("units", "")
                if units:
                    cb.set_label(units, fontsize=10)
                # High/Low labels on colorbar
                cb.ax.text(0.5, 1.02, "High", transform=cb.ax.transAxes,
                           ha='center', va='bottom', fontsize=10, fontweight='bold')
                cb.ax.text(0.5, -0.02, "Low", transform=cb.ax.transAxes,
                           ha='center', va='top', fontsize=10, fontweight='bold')

        # Boundary overlay — now in geo-coordinates (same space as imshow extent)
        if _boundary is not None:
            try:
                _add_boundary_overlay(ax, _boundary, extent=raster_extent)
            except Exception:
                pass

        desc = _get_description(name, metadata)
        title_str = f"{display}\n{desc}" if desc else display
        ax.set_title(title_str, fontsize=14, fontweight='bold', pad=8,
                     linespacing=1.6)
        ax.axis("off")

        # Scale bar + frame + letter
        if layer_bounds and _scale_crs:
            _add_scale_bar(ax, layer_bounds, _scale_crs)
        _add_panel_frame(ax)
        _add_letter_label(ax, _LETTER_LABELS[i])

    # ── Composite overlay panel ──────────────────────────────────────────
    import matplotlib.cm as cm
    from matplotlib.colors import BoundaryNorm, ListedColormap

    img_extent = None
    composite_legend_handles = []

    for i, (layer_name, path) in enumerate(outputs):
        label = _get_display_name(layer_name, metadata)
        if path.suffix.lower() in ['.geojson', '.json', '.shp']:
            style = _get_vector_style(layer_name)
            gdf = gpd.read_file(path)
            gdf.plot(ax=ax_composite, color=style["color"], edgecolor='black',
                     linewidth=0.5, alpha=style["fillOpacity"], zorder=i + 2)
            composite_legend_handles.append(
                Patch(facecolor=style["color"], alpha=style["fillOpacity"], label=label)
            )
        else:
            with rasterio.open(path) as src:
                data = src.read(1)
                bnds = src.bounds
                img_extent = [bnds.left, bnds.right, bnds.bottom, bnds.top]

            style = _get_layer_style(layer_name, data, i)

            if style["solid_color"] is not None:
                r, g, b, a = style["solid_color"]
                rgba_img = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.float32)
                rgba_img[:, :, 0] = r
                rgba_img[:, :, 1] = g
                rgba_img[:, :, 2] = b
                rgba_img[:, :, 3] = (data == 1).astype(float) * style["alpha"]
                ax_composite.imshow(rgba_img, extent=img_extent, aspect='equal',
                                    origin='upper', zorder=i + 1)
                composite_legend_handles.append(Patch(facecolor=(r, g, b), alpha=a, label=label))
            else:
                vmin = style["vmin"] if style["vmin"] is not None else np.nanmin(data)
                vmax = style["vmax"] if style["vmax"] is not None else np.nanmax(data)
                masked_data = np.ma.masked_equal(data, 0)
                unique_vals = np.unique(data[data > 0])

                if (len(unique_vals) > 20 and "fbfm" in layer_name.lower()
                        and "color_map" in style and style["color_map"]):
                    import src.geospatial_harmonizer as _self
                    all_cats = sorted([int(v) for v in unique_vals.tolist()])
                    color_map = style["color_map"]
                    colors = [
                        (color_map[c][0] / 255, color_map[c][1] / 255, color_map[c][2] / 255)
                        if c in color_map else (0.7, 0.7, 0.7)
                        for c in all_cats
                    ]
                    cmap = ListedColormap(colors)
                    color_bounds = [c - 0.5 for c in all_cats] + [all_cats[-1] + 0.5]
                    norm = BoundaryNorm(color_bounds, cmap.N)
                    ax_composite.imshow(masked_data, cmap=cmap, norm=norm, extent=img_extent,
                                        aspect='equal', origin='upper',
                                        alpha=style["alpha"], zorder=i + 1)
                    mid = all_cats[len(all_cats) // 2]
                    mid_color = (
                        (color_map[mid][0] / 255, color_map[mid][1] / 255, color_map[mid][2] / 255)
                        if mid in color_map else (0.5, 0.5, 0.5)
                    )
                    # Simplified legend entry for categorical data
                    composite_legend_handles.append(
                        Patch(facecolor='#8B9D4B', alpha=0.8,
                              label=f"{label}")
                    )
                else:
                    cmap_obj = cm.get_cmap(style["colormap"])
                    ax_composite.imshow(masked_data, cmap=cmap_obj, vmin=vmin, vmax=vmax,
                                        extent=img_extent, aspect='equal', origin='upper',
                                        alpha=style["alpha"], zorder=i + 1)
                    # Two-tone legend: show Low and High ends of colormap
                    units = style.get("units", "")
                    legend_label = f"{label} ({units})" if units else label
                    composite_legend_handles.append(
                        Patch(facecolor=cmap_obj(0.2), alpha=style["alpha"],
                              label=f"  {legend_label} \u2014 Low")
                    )
                    composite_legend_handles.append(
                        Patch(facecolor=cmap_obj(0.8), alpha=style["alpha"],
                              label=f"  {legend_label} \u2014 High")
                    )

    # Boundary overlay on composite
    if _boundary is not None and img_extent is not None:
        try:
            _add_boundary_overlay(ax_composite, _boundary, extent=img_extent)
        except Exception:
            pass

    composite_title = metadata.title if metadata else "Combined View"
    ax_composite.set_title(
        f"{composite_title} \u2014 All Layers",
        fontsize=14, fontweight='bold', pad=8,
    )
    ax_composite.axis("off")

    # Scale bar + north arrow + frame + letter on composite
    composite_bounds = _scale_extent or (img_extent and (img_extent[0], img_extent[2], img_extent[1], img_extent[3]))
    if composite_bounds and _scale_crs:
        _add_scale_bar(ax_composite, composite_bounds, _scale_crs)
    _add_north_arrow(ax_composite)
    _add_panel_frame(ax_composite)
    _add_letter_label(ax_composite, _LETTER_LABELS[n])

    # ── Info panel: legend + summary (right side of bottom row) ─────────
    ax_info.axis("off")
    _add_panel_frame(ax_info)

    if composite_legend_handles:
        ax_info.legend(
            handles=composite_legend_handles,
            loc='upper left',
            bbox_to_anchor=(0.05, 0.95),
            fontsize=10,
            frameon=True,
            edgecolor='#cccccc',
            fancybox=True,
            title="Map Layers",
            title_fontsize=12,
        )

    # Summary text
    if metadata and metadata.summary:
        import textwrap
        wrapped = "\n".join(textwrap.wrap(metadata.summary, width=45))
        ax_info.text(
            0.05, 0.35, "Summary",
            transform=ax_info.transAxes,
            fontsize=14, fontweight='bold', va='top', ha='left',
        )
        ax_info.text(
            0.05, 0.28, wrapped,
            transform=ax_info.transAxes,
            fontsize=11, va='top', ha='left',
            linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f8f8',
                      edgecolor='#dddddd', linewidth=0.8),
        )

    # Footer with CRS/resolution info
    if metadata:
        crs = metadata.crs
        res = metadata.resolution
        if res < 1:
            res_label = f"{res}\u00b0"
        else:
            res_label = f"{res:.0f} m"
        footer = (
            f"Harmonized to {crs}  \u00b7  {res_label} resolution  \u00b7  "
            f"{len(outputs)} layer{'s' if len(outputs) != 1 else ''}"
        )
        fig.text(0.5, 0.005, footer, ha='center', va='bottom',
                 fontsize=11, color='#555555', style='italic')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def _is_binary_data(data: np.ndarray) -> bool:
    """Check if data is binary (only contains 0 and 1)."""
    unique_vals = np.unique(data)
    if len(unique_vals) <= 2:
        # Check if values are 0 and 1 (or similar)
        non_zero_vals = [v for v in unique_vals if v != 0 and v != 0.0]
        if len(non_zero_vals) == 1 and non_zero_vals[0] == 1:
            return True
    return False


def _get_layer_style(name: str, data: np.ndarray, index: int) -> dict:
    """Get color scheme and styling for a layer based on its name and data type.
    
    Returns a dict with:
    - colormap: matplotlib colormap name
    - solid_color: RGB tuple for binary data (0-1 range)
    - alpha: transparency
    - vmin, vmax: for colormap normalization
    """
    name_lower = name.lower()
    is_binary = _is_binary_data(data)
    
    # Define distinct color schemes for different dataset types
    if is_binary:
        # Binary data - use solid colors
        if "burn" in name_lower or "mtbs" in name_lower or "fire" in name_lower:
            # Burned areas - use red
            return {
                "colormap": None,
                "solid_color": (1.0, 0.0, 0.0, 1.0),  # Red
                "alpha": 0.8,
                "vmin": None,
                "vmax": None,
            }
        elif "building" in name_lower or "footprint" in name_lower:
            # Buildings - use purple/blue
            return {
                "colormap": None,
                "solid_color": (0.4, 0.2, 0.8, 1.0),  # Purple
                "alpha": 0.8,
                "vmin": None,
                "vmax": None,
            }
        else:
            # Default binary - use red
            return {
                "colormap": None,
                "solid_color": (1.0, 0.0, 0.0, 1.0),  # Red
                "alpha": 0.8,
                "vmin": None,
                "vmax": None,
            }
    else:
        # Continuous/categorical data - use distinct colormaps
        if "fbfm" in name_lower or "fuel" in name_lower:
            # Fuel models - check if we have a discovered color map from source
            if DISCOVERED_COLOR_MAP:
                return {
                    "colormap": None,  # Will use custom color map
                    "color_map": DISCOVERED_COLOR_MAP,
                    "solid_color": None,
                    "alpha": 0.7,
                    "vmin": min(DISCOVERED_COLOR_MAP.keys()),
                    "vmax": max(DISCOVERED_COLOR_MAP.keys()),
                }
            else:
                # Fallback to default colormap
                return {
                    "colormap": "nipy_spectral",  # Good for many categories
                    "color_map": None,
                    "solid_color": None,
                    "alpha": 0.7,
                "vmin": np.nanmin(data),
                "vmax": np.nanmax(data),
            }
        elif "elevation" in name_lower or "dem" in name_lower:
            return {
                "colormap": "terrain",
                "solid_color": None,
                "alpha": 0.7,
                "vmin": np.nanmin(data),
                "vmax": np.nanmax(data),
                "units": "m",
            }
        elif (
            "pr" in name_lower.split("_")
            or "precip" in name_lower
            or "precipitation" in name_lower
            or name_lower.startswith("pr_")
            or "_pr_" in name_lower
        ):
            # Precipitation — Blues colormap, units in mm day⁻¹
            return {
                "colormap": "Blues",
                "solid_color": None,
                "alpha": 0.8,
                "vmin": np.nanmin(data[data > 0]) if np.any(data > 0) else 0,
                "vmax": np.nanmax(data),
                "units": "mm day\u207b\u00b9",
            }
        elif "vpd" in name_lower or "vapor" in name_lower:
            return {
                "colormap": "plasma",
                "solid_color": None,
                "alpha": 0.7,
                "vmin": np.nanmin(data),
                "vmax": np.nanmax(data),
                "units": "kPa",
            }
        elif "temp" in name_lower or "tasmax" in name_lower or "tasmin" in name_lower:
            return {
                "colormap": "RdYlBu_r",
                "solid_color": None,
                "alpha": 0.7,
                "vmin": np.nanmin(data),
                "vmax": np.nanmax(data),
                "units": "°C",
            }
        else:
            # Default continuous - use viridis
            return {
                "colormap": "viridis",
                "solid_color": None,
                "alpha": 0.7,
                "vmin": np.nanmin(data),
                "vmax": np.nanmax(data),
            }


def _get_vector_style(name: str) -> dict:
    """Get color scheme and styling for a vector layer based on its name.
    
    Returns a dict with:
    - color: Hex color string for the layer
    - weight: Line weight for boundaries
    - fillOpacity: Fill opacity for polygons
    """
    name_lower = name.lower()
    
    if "burn" in name_lower or "mtbs" in name_lower or "fire" in name_lower:
        # Burned areas - use red
        return {
            "color": "#FF0000",
            "weight": 2,
            "fillOpacity": 0.5,
        }
    elif "building" in name_lower or "footprint" in name_lower:
        # Buildings - use purple/blue
        return {
            "color": "#6600CC",
            "weight": 1,
            "fillOpacity": 0.7,
        }
    else:
        # Default - use blue
        return {
            "color": "#3186cc",
            "weight": 2,
            "fillOpacity": 0.5,
        }


def _compute_scale_info(bounds: tuple, crs_str: str) -> tuple[float, float]:
    """Return (map_width_m, meters_per_crs_unit) for a given extent and CRS."""
    import math
    import pyproj

    xmin, ymin, xmax, ymax = bounds
    crs = pyproj.CRS(crs_str)
    if crs.is_geographic:
        mid_lat = (ymin + ymax) / 2
        meters_per_unit = 111_320 * math.cos(math.radians(mid_lat))
    else:
        meters_per_unit = 1.0
    return (xmax - xmin) * meters_per_unit, meters_per_unit


def _add_scale_bar(ax, bounds: tuple, crs_str: str) -> None:
    """Draw a numbered scale bar in the lower-right corner of *ax*.

    Style: ``0 ── 25 ── 50 ── 75 ── 100 km`` with alternating black/white
    segments for readability.
    """
    map_width_m, _ = _compute_scale_info(bounds, crs_str)

    # Choose a "nice" total bar length ≈ 20% of map width
    nice_lengths_m = [
        100, 200, 500, 1_000, 2_000, 5_000, 10_000, 25_000,
        50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000,
    ]
    target = map_width_m * 0.2
    bar_m = min(nice_lengths_m, key=lambda x: abs(x - target))
    bar_frac = bar_m / map_width_m

    n_segments = 4
    seg_frac = bar_frac / n_segments

    if bar_m >= 1_000:
        unit = "km"
        divisor = 1_000
    else:
        unit = "m"
        divisor = 1

    # Position: lower-right
    x_left = 0.95 - bar_frac
    y_pos = 0.05
    bar_h = 0.012

    for s in range(n_segments):
        x0 = x_left + s * seg_frac
        x1 = x0 + seg_frac
        color = 'black' if s % 2 == 0 else 'white'
        ax.fill_between(
            [x0, x1], y_pos - bar_h, y_pos + bar_h,
            transform=ax.transAxes, color=color, edgecolor='black',
            linewidth=0.5, clip_on=False, zorder=99,
        )

    # Tick labels: 0 and total
    for val, x in [(0, x_left), (bar_m / divisor, x_left + bar_frac)]:
        ax.text(x, y_pos - bar_h - 0.015, f"{val:.0f}",
                transform=ax.transAxes, ha='center', va='top',
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                          edgecolor='none', alpha=0.7))
    # Unit label
    ax.text(x_left + bar_frac + 0.015, y_pos, unit,
            transform=ax.transAxes, ha='left', va='center',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                      edgecolor='none', alpha=0.7))


def _add_north_arrow(ax, x: float = 0.05, y: float = 0.12) -> None:
    """Draw a north arrow at (x, y) in axes-fraction coordinates."""
    ax.annotate(
        'N', xy=(x, y), xytext=(x, y - 0.07),
        transform=ax.transAxes, ha='center', va='center',
        fontsize=10, fontweight='bold',
        arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
    )


def _add_boundary_overlay(ax, geometry, data_shape: tuple | None = None,
                          extent: tuple | None = None,
                          raster_bounds: tuple | None = None) -> None:
    """Overlay a boundary polygon outline on an axes.

    For panels with a geo-extent (composite, vector), the boundary is drawn
    in data coordinates. For raster panels (imshow without extent), the
    boundary is rasterized to pixel coordinates using *raster_bounds*.
    """
    if geometry is None:
        return

    if extent is not None:
        # Data coordinates — draw directly
        xs, ys = geometry.exterior.coords.xy
        ax.plot(xs, ys, color='#333333', linewidth=1.2, linestyle='-',
                zorder=50, alpha=0.8)
        for interior in geometry.interiors:
            xs, ys = interior.coords.xy
            ax.plot(xs, ys, color='#333333', linewidth=0.8, linestyle='-',
                    zorder=50, alpha=0.8)
    elif data_shape is not None:
        # Pixel coordinates — rasterize boundary using the raster's own
        # bounds so the mask aligns exactly with imshow output.
        from rasterio.features import rasterize as _rasterize
        from rasterio.transform import from_bounds
        h, w = data_shape
        if raster_bounds is not None:
            bx0, by0, bx1, by1 = raster_bounds
        else:
            bx0, by0, bx1, by1 = geometry.bounds
        tf = from_bounds(bx0, by0, bx1, by1, w, h)
        mask = _rasterize([(geometry, 1)], out_shape=(h, w), transform=tf,
                          fill=0, dtype='uint8')
        ax.contour(mask, levels=[0.5], colors=['#333333'], linewidths=[1.2],
                   origin='upper', zorder=50, alpha=0.8)


def create_interactive_visualization(
    outputs: list[tuple[str, Path]],
    target_extent: tuple[float, float, float, float],
    output_dir: Path | None = None,
    verbose: bool = True
) -> folium.Map | None:
    """Create an interactive folium map visualization.

    Args:
        outputs: List of (name, path) tuples for each harmonized layer
        target_extent: Bounding box (xmin, xmax, ymin, ymax) for the map view
        output_dir: Optional directory in which to save the HTML map. If
            provided, the map is written to ``<output_dir>/harmonized_visualization.html``
            (filename is hardcoded — see HARMONIZED_VIZ_HTML). If None, the
            map is returned for inline display (e.g. in a Jupyter notebook).
        verbose: Print progress messages

    Returns:
        folium.Map object, or None if creation failed
    """
    if not FOLIUM_AVAILABLE:
        _log("Folium not available, skipping interactive visualization", verbose)
        return None

    output_path = (output_dir / HARMONIZED_VIZ_HTML) if output_dir is not None else None
    try:
        return _create_interactive_visualization_impl(outputs, target_extent, output_path, verbose)
    except Exception as e:
        _log(f"Error creating interactive visualization: {e}", verbose)
        import traceback
        traceback.print_exc()
        return None


def _create_interactive_visualization_impl(
    outputs: list[tuple[str, Path]],
    target_extent: tuple[float, float, float, float],
    output_path: Path | None = None,
    verbose: bool = True
) -> folium.Map:
    """Internal implementation of interactive visualization creation."""
    _log("Creating interactive HTML visualization (this may take several minutes for large layers)...", verbose)
    _load_color_map_from_output_dir(output_path)

    xmin, ymin, xmax, ymax = target_extent
    center_lat = (ymin + ymax) / 2
    center_lon = (xmin + xmax) / 2
    
    # Create base map with clean styling (CartoDB positron is clean and doesn't compete with data)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles=None  # We'll add our own base layer
    )
    
    # Add CartoDB positron base layer (clean, light background)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="CartoDB Positron",
        max_zoom=19
    ).add_to(m)
    
    # Track layer JS variable names for per-layer opacity sliders.
    # Each entry: (display_name, js_var_name, layer_type, fill_opacity)
    _opacity_layers: list[tuple[str, str, str, float]] = []

    # Add each layer - handle raster and vector differently
    for i, (name, path) in enumerate(outputs):
        _log(f"  Processing layer {i+1}/{len(outputs)}: {name}", verbose)
        # Check if this is a vector file (GeoJSON)
        if path.suffix.lower() == '.geojson' or path.suffix.lower() == '.json':
            # Handle vector data as GeoJSON layer
            _log(f"  Adding vector layer: {name}", verbose)

            # Get styling for this layer
            style = _get_vector_style(name)

            # Read the GeoJSON
            gdf = gpd.read_file(path)

            # Convert datetime columns to strings to avoid JSON serialization issues
            for col in gdf.columns:
                if hasattr(gdf[col].dtype, 'kind') and gdf[col].dtype.kind == 'M':
                    gdf[col] = gdf[col].astype(str)

            # Auto-simplify large layers so they embed in HTML without crashing the browser.
            # Tolerance is ~0.1% of the shorter bbox dimension (~100 m for a state-scale map).
            size_mb = path.stat().st_size / 1024 / 1024
            if size_mb > 50:
                xmin, ymin, xmax, ymax = target_extent
                tol = min(xmax - xmin, ymax - ymin) * 0.001
                _log(
                    f"  Large vector ({size_mb:.0f} MB) — simplifying geometry (this is the slowest step)...",
                    verbose,
                )
                gdf = gpd.GeoDataFrame(
                    gdf.drop(columns=[c for c in gdf.columns if c != "geometry"], errors="ignore"),
                    geometry=gdf.geometry.simplify(tol, preserve_topology=True),
                    crs=gdf.crs,
                )
                # Snap to 0.0001° grid (~11 m) to further reduce JSON size
                gdf = gdf.set_precision(0.0001)
                simplified_mb = len(gdf.to_json()) / 1024 / 1024
                _log(f"  Simplified to ~{simplified_mb:.0f} MB", verbose)

            geojson_str = gdf.to_json()
            geojson_layer = folium.GeoJson(
                geojson_str,
                name=_format_layer_name(name),
                style_function=lambda x, color=style["color"], weight=style["weight"], fill_opacity=style["fillOpacity"]: {
                    'fillColor': color,
                    'color': color,
                    'weight': weight,
                    'fillOpacity': fill_opacity,
                },
                tooltip=_format_layer_name(name),
            )
            geojson_layer.add_to(m)
            _opacity_layers.append((_format_layer_name(name), geojson_layer.get_name(), 'vector', style["fillOpacity"]))
        else:
            # Handle raster data as image overlay
            _log(f"  Adding raster layer: {name}", verbose)
            with rasterio.open(path) as src:
                data = src.read(1)
                # Use target extent for bounds to ensure full coverage
                bounds = (xmin, ymin, xmax, ymax)

                # Get styling for this layer
                style = _get_layer_style(name, data, i)

                # Build RGBA array directly with PIL — much smaller than matplotlib figure
                from PIL import Image as PILImage
                h, w = data.shape
                rgba = np.zeros((h, w, 4), dtype=np.uint8)
                alpha_val = int(style["alpha"] * 255)

                if style["solid_color"] is not None:
                    r, g, b, _ = style["solid_color"]
                    mask_px = data == 1
                    rgba[mask_px, 0] = int(r * 255)
                    rgba[mask_px, 1] = int(g * 255)
                    rgba[mask_px, 2] = int(b * 255)
                    rgba[mask_px, 3] = alpha_val
                else:
                    import matplotlib.cm as cm
                    from matplotlib.colors import BoundaryNorm, ListedColormap, Normalize

                    vmin = style["vmin"] if style["vmin"] is not None else float(np.nanmin(data[data > 0]))
                    vmax = style["vmax"] if style["vmax"] is not None else float(np.nanmax(data))
                    unique_vals = np.unique(data[data > 0])
                    is_categorical = len(unique_vals) > 20

                    if is_categorical and "fbfm" in name.lower() and style.get("color_map"):
                        color_map = style["color_map"]
                        # Paint all non-zero pixels light grey first (catches unlabeled artifact codes)
                        artifact_px = (data > 0) & ~np.isin(data, list(color_map.keys()))
                        rgba[artifact_px, 0] = 180
                        rgba[artifact_px, 1] = 180
                        rgba[artifact_px, 2] = 180
                        rgba[artifact_px, 3] = alpha_val
                        # Then paint known categories with their proper colors
                        for cat_val, color in color_map.items():
                            px = data == cat_val
                            rgba[px, 0] = color[0]
                            rgba[px, 1] = color[1]
                            rgba[px, 2] = color[2]
                            rgba[px, 3] = alpha_val
                    else:
                        if is_categorical and "fbfm" in name.lower():
                            n_colors = len(unique_vals)
                            cmap = cm.get_cmap("nipy_spectral", n_colors)
                            norm = BoundaryNorm(
                                np.linspace(vmin - 0.5, vmax + 0.5, n_colors + 1), n_colors
                            )
                        else:
                            cmap = cm.get_cmap(style["colormap"])
                            norm = Normalize(vmin=vmin, vmax=vmax)

                        valid = data > 0
                        normed = norm(data[valid].astype(float))
                        colored = cmap(normed)  # (N, 4) float 0-1
                        rgba[valid, 0] = (colored[:, 0] * 255).astype(np.uint8)
                        rgba[valid, 1] = (colored[:, 1] * 255).astype(np.uint8)
                        rgba[valid, 2] = (colored[:, 2] * 255).astype(np.uint8)
                        rgba[valid, 3] = alpha_val

                # Downsample to max 800px on the long side for web display
                max_dim = 800
                if max(h, w) > max_dim:
                    scale = max_dim / max(h, w)
                    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
                    img = PILImage.fromarray(rgba, mode='RGBA').resize(
                        (new_w, new_h), PILImage.LANCZOS
                    )
                else:
                    img = PILImage.fromarray(rgba, mode='RGBA')

                buf = io.BytesIO()
                img.save(buf, format='PNG', optimize=True)
                buf.seek(0)

                # Encode to base64
                img_base64 = base64.b64encode(buf.getvalue()).decode('ascii')
                
                # Create image overlay with proper lat/lon bounds using target extent
                # opacity=1.0 because alpha is already baked into the RGBA pixel data
                overlay = folium.raster_layers.ImageOverlay(
                    image=f"data:image/png;base64,{img_base64}",
                    bounds=[[bounds[1], bounds[0]], [bounds[3], bounds[2]]],
                    name=_format_layer_name(name),
                    opacity=1.0,
                    interactive=True,
                    zindex=i + 10  # Above base maps
                )
                overlay.add_to(m)
                _opacity_layers.append((_format_layer_name(name), overlay.get_name(), 'raster', style["alpha"]))

    # Add a rectangle to show the target extent
    folium.Rectangle(
        bounds=[[ymin, xmin], [ymax, xmax]],
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
        fill_opacity=0.1,
        name="Target Extent"
    ).add_to(m)
    
    # Add fullscreen option
    folium.plugins.Fullscreen().add_to(m)
    
    # Add mouse position display
    folium.plugins.MousePosition().add_to(m)
    
    # Add a legend as a custom HTML element
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 210px;
                max-height: calc(100vh - 120px); overflow-y: auto;
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color:white; padding: 10px;
                border-radius: 5px;
                ">
    <b>Legend</b><br>
    '''
    
    for i, (name, path) in enumerate(outputs):
        # Check if this is a vector file
        if path.suffix.lower() == '.geojson' or path.suffix.lower() == '.json':
            style = _get_vector_style(name)
            legend_html += f'<div style="display:flex;align-items:center;margin:3px 0;"><i style="background:{style["color"]};width:12px;height:12px;display:inline-block;margin-right:5px;flex-shrink:0;"></i> {_format_layer_name(name)}</div>'
        else:
            with rasterio.open(path) as src:
                data = src.read(1)
            style = _get_layer_style(name, data, i)

            if style["solid_color"] is not None:
                # Binary data - show solid color
                r, g, b, a = style["solid_color"]
                hex_color = '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
                legend_html += f'<div style="display:flex;align-items:center;margin:3px 0;"><i style="background:{hex_color};width:12px;height:12px;display:inline-block;margin-right:5px;flex-shrink:0;"></i> {_format_layer_name(name)}</div>'
            else:
                import src.geospatial_harmonizer as _self
                # Only use the layer's own color_map — not the global DISCOVERED_LABELS,
                # which persists from prior layers (e.g. FBFM40) and would incorrectly
                # cause continuous layers (e.g. precipitation) to render as categorical.
                color_map = style.get("color_map") or {}
                label_title = _format_layer_name(name)

                if color_map:
                    # Categorical data with a per-value color map — show labeled swatches
                    labels_map = _self.DISCOVERED_LABELS or {}
                    unique_present = sorted(np.unique(data[np.isfinite(data) & (data > 0)]).tolist())
                    named_present = [v for v in unique_present if v in color_map or labels_map.get(v, str(v)) != str(v)]
                    legend_html += f'<div style="margin:4px 0 2px;font-weight:bold;">{label_title}</div>'
                    legend_html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:11px;">'
                    for v in named_present:
                        label = labels_map.get(v, str(v))
                        if v in color_map:
                            r_c, g_c, b_c = color_map[v][0], color_map[v][1], color_map[v][2]
                            bg = f"rgb({r_c},{g_c},{b_c})"
                        else:
                            bg = "#aaa"
                        legend_html += (
                            f'<div style="display:flex;align-items:center;gap:4px;">'
                            f'<i style="background:{bg};width:12px;height:12px;display:inline-block;flex-shrink:0;border-radius:2px;"></i>'
                            f'{label}</div>'
                        )
                    legend_html += '</div>'
                else:
                    # Continuous data — show a gradient bar with min/max labels
                    vmin = style.get("vmin") if style.get("vmin") is not None else np.nanmin(data)
                    vmax = style.get("vmax") if style.get("vmax") is not None else np.nanmax(data)
                    units = style.get("units", "")
                    cmap_name = style.get("colormap", "viridis")
                    # Approximate CSS gradient stops for common colormaps
                    gradients = {
                        "viridis":    "linear-gradient(to right, #440154, #31688e, #35b779, #fde725)",
                        "terrain":    "linear-gradient(to right, #333399, #66b266, #d2a679, #ffffff)",
                        "plasma":     "linear-gradient(to right, #0d0887, #7e03a8, #cc4778, #f89540, #f0f921)",
                        "Blues":      "linear-gradient(to right, #f7fbff, #9ecae1, #4292c6, #084594)",
                        "RdYlBu_r":  "linear-gradient(to right, #313695, #74add1, #ffffbf, #f46d43, #a50026)",
                    }
                    gradient = gradients.get(cmap_name, gradients["viridis"])
                    units_str = f" ({units})" if units else ""
                    legend_html += f'''
                    <div style="margin:4px 0 2px;font-weight:bold;">{label_title}{units_str}</div>
                    <div style="background:{gradient};height:12px;width:100%;border-radius:2px;margin-bottom:2px;"></div>
                    <div style="display:flex;justify-content:space-between;font-size:10px;">
                        <span>{vmin:.2f}</span><span>{vmax:.2f}</span>
                    </div>'''
    
    legend_html += '</div>'

    # Add the legend to the map
    m.get_root().html.add_child(folium.Element(legend_html))

    # --- Per-layer toggle + opacity control panel ---
    # Each layer gets a checkbox (show/hide) and, while checked, an opacity slider.
    # Uses each layer's Leaflet JS variable name (from folium's get_name()).
    opacity_html = '''
    <div style="position:fixed; top:80px; right:10px; z-index:9999;
                background:white; padding:10px 12px; border:2px solid grey;
                border-radius:5px; font-size:12px; min-width:200px;
                box-shadow:2px 2px 6px rgba(0,0,0,0.2);">
      <b>Data Layers</b>
    '''
    for display_name, js_name, layer_type, init_fill_opacity in _opacity_layers:
        if layer_type == 'vector':
            # Apply opacity to both stroke and fill; preserve original fillOpacity ratio.
            # Two variants: one uses `sl.value` (checkbox context), one uses `this.value` (slider context).
            apply_from_slider = (
                f"var op=this.value/100;"
                f"{js_name}.setStyle({{opacity:op,fillOpacity:op*{init_fill_opacity}}});"
            )
            apply_from_chk = (
                f"var op=sl.value/100;"
                f"{js_name}.setStyle({{opacity:op,fillOpacity:op*{init_fill_opacity}}});"
            )
            hide_layer = f"{js_name}.setStyle({{opacity:0,fillOpacity:0}});"
        else:
            apply_from_slider = f"{js_name}.setOpacity(this.value/100);"
            apply_from_chk   = f"{js_name}.setOpacity(sl.value/100);"
            hide_layer       = f"{js_name}.setOpacity(0);"

        # Checkbox onchange: show/hide the slider row and apply opacity or zero.
        on_chk = (
            f"var sl=document.getElementById('{js_name}_sl');"
            f"var row=document.getElementById('{js_name}_row');"
            f"row.style.display=this.checked?'flex':'none';"
            f"if(this.checked){{{apply_from_chk}}}else{{{hide_layer}}}"
        )
        # Slider oninput: only apply if the checkbox is checked; always update label.
        on_sl = (
            f"if(document.getElementById('{js_name}_chk').checked){{{apply_from_slider}}}"
            f"document.getElementById('{js_name}_lbl').textContent=this.value+'%';"
        )
        opacity_html += f'''
      <div style="margin:6px 0 2px;">
        <div style="display:flex;align-items:center;gap:6px;">
          <input type="checkbox" id="{js_name}_chk" checked style="cursor:pointer;"
                 onchange="{on_chk}">
          <label for="{js_name}_chk" style="flex:1;cursor:pointer;">{display_name}</label>
        </div>
        <div id="{js_name}_row" style="display:flex;align-items:center;gap:6px;padding-left:20px;margin-top:3px;">
          <input type="range" id="{js_name}_sl" min="0" max="100" value="100"
                 style="flex:1;cursor:pointer;" oninput="{on_sl}">
          <span id="{js_name}_lbl" style="width:30px;text-align:right;font-size:11px;">100%</span>
        </div>
      </div>'''
    opacity_html += '\n    </div>'
    m.get_root().html.add_child(folium.Element(opacity_html))

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path))
        _log(f"Interactive visualization saved to: {output_path}", verbose)

    return m


def run_harmonization_example(workflow: ExampleWorkflow) -> tuple[list[Path], folium.Map | None]:
    # Reset module-level color map state so workflows don't bleed into each other
    # when multiple ExampleWorkflows run in the same process (e.g. in a notebook).
    import src.geospatial_harmonizer as _self
    _self.DISCOVERED_COLOR_MAP = None
    _self.DISCOVERED_LABELS = None

    # Resolve clip boundary if provided
    clip_geom = None
    if workflow.clip_boundary is not None:
        clip_geom, boundary_bbox = resolve_clip_boundary(
            workflow.clip_boundary,
            workflow.target_crs,
            verbose=workflow.verbose,
        )
        # If target_extent wasn't explicitly set (all zeros or a sentinel),
        # auto-compute from the boundary bbox.  In practice, users who set
        # clip_boundary should also set target_extent to the boundary's bbox
        # (region_extent.py prints both), but this is a safety net.
        if workflow.target_extent == (0, 0, 0, 0):
            workflow.target_extent = boundary_bbox
            _log(f"Auto-computed target_extent from boundary: {boundary_bbox}", workflow.verbose)

    grid = build_grid_spec(
        target_crs=workflow.target_crs,
        target_extent=workflow.target_extent,
        target_resolution=workflow.target_resolution,
        clip_geometry=clip_geom,
    )

    # Several download functions (OPeNDAP, STAC, ArcGIS ImageServer) require
    # a bbox in EPSG:4326.  When target_crs is anything else (projected CRS,
    # NAD83, etc.) we transform the extent to geographic coordinates.
    # Use rasterio.crs.CRS for comparison so "EPSG:4326", "epsg:4326",
    # "+proj=longlat +datum=WGS84", etc. all match correctly.
    from rasterio.crs import CRS as _CRS
    from rasterio.warp import transform_bounds
    _target_crs_obj = _CRS.from_user_input(workflow.target_crs)
    _wgs84 = _CRS.from_epsg(4326)
    if _target_crs_obj == _wgs84:
        download_bbox = workflow.target_extent
    else:
        xmin4326, ymin4326, xmax4326, ymax4326 = transform_bounds(
            _target_crs_obj, _wgs84, *workflow.target_extent
        )
        download_bbox: BBox = (
            round(xmin4326, 4), round(ymin4326, 4),
            round(xmax4326, 4), round(ymax4326, 4),
        )
        _log(f"Download bbox (EPSG:4326): {download_bbox}", workflow.verbose)

    workflow.output_dir.mkdir(parents=True, exist_ok=True)
    output_files: list[Path] = []
    viz_inputs: list[tuple[str, Path]] = []
    
    # Global color map discovered from source data
    global_color_map: dict | None = None

    with TemporaryDirectory(prefix=f"{workflow.name}_") as tmp:
        tmp_dir = Path(tmp)

        for _ds_idx, dataset in enumerate(workflow.datasets, 1):
            _log(f"\n[{_ds_idx}/{len(workflow.datasets)}] {dataset.display_name or _format_layer_name(dataset.name)}", workflow.verbose)
            dataset_dir = tmp_dir / dataset.name
            dataset_dir.mkdir(parents=True, exist_ok=True)

            # Check if output already exists BEFORE downloading
            if dataset.data_type == "vector" and not dataset.rasterize:
                output_path = workflow.output_dir / f"harmonized_{dataset.name}.geojson"
            else:
                output_path = workflow.output_dir / f"harmonized_{dataset.name}.tif"
            
            if output_path.exists():
                _log(f"Using existing harmonized file: {output_path.name}", workflow.verbose)
                output_files.append(output_path)
                viz_inputs.append((dataset.name, output_path))
                # Try to load color map from saved file if not already discovered
                if global_color_map is None and dataset.data_type == "raster":
                    color_map_path = workflow.output_dir / f"{dataset.name}_color_map.json"
                    if color_map_path.exists():
                        import json
                        with open(color_map_path) as f:
                            color_map_json = json.load(f)
                            # Convert string keys back to int and lists to tuples
                            color_map = {int(k): tuple(v) for k, v in color_map_json.items()}
                            global_color_map = color_map
                            # Update module-level global for visualization functions
                            import src.geospatial_harmonizer
                            src.geospatial_harmonizer.DISCOVERED_COLOR_MAP = color_map
                            _log(f"Loaded color map with {len(color_map)} categories from file", workflow.verbose)
                # Try to load labels from saved file
                labels_path = workflow.output_dir / f"{dataset.name}_labels.json"
                if labels_path.exists():
                    import json, src.geospatial_harmonizer
                    with open(labels_path) as f:
                        labels_json = json.load(f)
                    src.geospatial_harmonizer.DISCOVERED_LABELS = {int(k): v for k, v in labels_json.items()}
                    _log(f"Loaded {len(labels_json)} labels from file", workflow.verbose)
                continue

            # Check if this is a STAC-sourced dataset
            if dataset.is_stac:
                source_file = download_stac_item(
                    catalog_url=dataset.url,
                    collection=dataset.stac_collection,
                    asset_key=dataset.stac_asset,
                    bbox=download_bbox,  # STAC search requires EPSG:4326
                    output_dir=dataset_dir,
                    datetime=dataset.stac_datetime,
                    query=dataset.stac_query,
                    verbose=workflow.verbose,
                )
            # Single-variable NetCDF via OPeNDAP (e.g. pre-computed VPD, tasmax, pr)
            elif dataset.netcdf_variable and not dataset.secondary_url:
                nc_path = dataset_dir / f"{dataset.name}_native.tif"
                source_file = fetch_netcdf_seasonal_geotiff(
                    url=dataset.url,
                    variable=dataset.netcdf_variable,
                    bbox=download_bbox,  # OPeNDAP coords are geographic
                    output_path=nc_path,
                    months=dataset.netcdf_months,
                    verbose=workflow.verbose,
                )
            # Check if this is a derived climate variable (e.g. VPD from tasmax + rhsmin)
            elif dataset.netcdf_variable and dataset.secondary_url and dataset.secondary_netcdf_variable:
                vpd_path = dataset_dir / f"{dataset.name}_vpd_native.tif"
                source_file = compute_vpd_geotiff(
                    tasmax_url=dataset.url,
                    rhsmin_url=dataset.secondary_url,
                    bbox=download_bbox,  # OPeNDAP coords are geographic
                    output_path=vpd_path,
                    tasmax_var=dataset.netcdf_variable,
                    rhsmin_var=dataset.secondary_netcdf_variable,
                    verbose=workflow.verbose,
                )
            # Check if URL is a WMS endpoint
            elif dataset.is_wms and dataset.data_type == "raster":
                # WMS accepts bbox in the workflow's CRS (passed explicitly)
                source_file = download_wms_coverage(
                    wms_url=dataset.url,
                    layer=dataset.wms_layer,
                    bbox=workflow.target_extent,
                    crs=workflow.target_crs,
                    output_dir=dataset_dir,
                    output_filename=f"{dataset.name}.tif",
                    width=grid.width,
                    height=grid.height,
                    verbose=workflow.verbose,
                )
            # Check if URL is a WCS endpoint
            elif dataset.is_wcs and dataset.data_type == "raster":
                # WCS accepts bbox in the workflow's CRS (passed explicitly)
                source_file = download_wcs_coverage(
                    wcs_url=dataset.url,
                    layer=dataset.wcs_layer,
                    bbox=workflow.target_extent,
                    crs=workflow.target_crs,
                    output_dir=dataset_dir,
                    output_filename=f"{dataset.name}.tif",
                    width=grid.width,
                    height=grid.height,
                    verbose=workflow.verbose,
                )
            # Check if URL is an ArcGIS ImageServer endpoint
            elif "ImageServer" in dataset.url and dataset.data_type == "raster":
                # ImageServer hardcodes bboxSR=4326, needs geographic coords
                source_file = download_arcgis_image_server(
                    dataset.url,
                    dataset_dir,
                    bbox=download_bbox,
                    width=grid.width,
                    height=grid.height,
                    verbose=workflow.verbose,
                )
            else:
                # Standard download + extract workflow
                downloaded = download_file(dataset.url, dataset_dir, workflow.verbose)
                extracted_dir = extract_archive_if_needed(downloaded, dataset_dir, workflow.verbose)
                source_file = discover_dataset_file(extracted_dir, dataset.data_type)
                
                # Try to discover color map from extracted data
                if global_color_map is None and dataset.data_type == "raster":
                    color_map = discover_color_map(extracted_dir, dataset.name)
                    if color_map:
                        global_color_map = color_map
                        # Update module-level global for visualization functions
                        import src.geospatial_harmonizer
                        src.geospatial_harmonizer.DISCOVERED_COLOR_MAP = color_map
                        _log(f"Discovered color map with {len(color_map)} categories", workflow.verbose)
                        # Save color map to output directory for reference
                        color_map_path = workflow.output_dir / f"{dataset.name}_color_map.json"
                        # Rename old color_map.json if it exists
                        old_color_map_path = workflow.output_dir / "color_map.json"
                        if old_color_map_path.exists():
                            old_color_map_path.rename(color_map_path)
                        import json
                        # Convert tuples to lists for JSON serialization
                        color_map_json = {str(k): list(v) for k, v in color_map.items()}
                        with open(color_map_path, 'w') as f:
                            json.dump(color_map_json, f)
                        _log(f"Saved color map to {color_map_path.name}", workflow.verbose)

            # Download and cache labels CSV if provided
            if dataset.labels_url:
                import json as _json
                labels_path = workflow.output_dir / f"{dataset.name}_labels.json"
                if not labels_path.exists():
                    _log(f"Downloading labels from {dataset.labels_url}", workflow.verbose)
                    try:
                        with urllib.request.urlopen(dataset.labels_url) as resp:
                            csv_text = resp.read().decode("utf-8")
                        labels: dict[str, str] = {}
                        for line in csv_text.splitlines():
                            parts = line.strip().split(",")
                            if len(parts) >= 2:
                                try:
                                    int(parts[0])  # skip non-numeric rows (header / nodata)
                                    labels[parts[0]] = parts[1]
                                except ValueError:
                                    pass
                        with open(labels_path, "w") as f:
                            _json.dump(labels, f)
                        _log(f"Saved {len(labels)} labels to {labels_path.name}", workflow.verbose)
                    except Exception as e:
                        _log(f"Could not download labels: {e}", workflow.verbose)

            # Determine output path based on data type
            if dataset.data_type == "vector" and not dataset.rasterize:
                output_path = workflow.output_dir / f"harmonized_{dataset.name}.geojson"
            else:
                output_path = workflow.output_dir / f"harmonized_{dataset.name}.tif"

            if dataset.data_type == "raster":
                # If downloaded from ImageServer, it's already at target resolution
                # Still need to ensure CRS matches
                harmonize_raster(
                    source_file, grid, output_path,
                    resampling_method=dataset.resampling_method,
                    verbose=workflow.verbose,
                )
            elif dataset.data_type == "vector" and dataset.rasterize:
                rasterize_vector_to_grid(
                    source_file,
                    grid,
                    output_path,
                    burn_value=dataset.burn_value,
                    verbose=workflow.verbose,
                )
            elif dataset.data_type == "vector" and not dataset.rasterize:
                # Keep vector as vector - reproject and clip to extent
                harmonize_vector(
                    source_file,
                    grid,
                    output_path,
                    verbose=workflow.verbose,
                )
            else:
                raise NotImplementedError(
                    f"Unsupported data type: {dataset.data_type}"
                )

            output_files.append(output_path)
            viz_inputs.append((dataset.name, output_path))

    interactive_map = None
    if workflow.create_visualization and output_files:
        _log(f"\nGenerating visualizations ({len(output_files)} layers)...", workflow.verbose)
        # Filenames are hardcoded inside create_visualization /
        # create_interactive_visualization (see HARMONIZED_VIZ_PNG / _HTML)
        # so the website build hook can find them.
        _d_names = {ds.name: ds.display_name for ds in workflow.datasets
                    if ds.display_name is not None} or None
        _d_descs = {ds.name: ds.description for ds in workflow.datasets
                    if ds.description is not None} or None
        # Auto-generate a summary from metadata
        _title = _format_layer_name(workflow.name)
        _res = workflow.target_resolution
        _res_label = f"{_res}\u00b0" if _res < 1 else f"{_res:.0f} m"
        _layer_list = ", ".join(
            ds.display_name or _format_layer_name(ds.name)
            for ds in workflow.datasets
        )
        _auto_summary = (
            f"This visualization harmonizes {len(workflow.datasets)} geospatial "
            f"datasets to a common grid ({workflow.target_crs}, {_res_label} "
            f"resolution). Layers include: {_layer_list}."
        )
        viz_meta = VizMetadata(
            title=_title,
            crs=workflow.target_crs,
            resolution=workflow.target_resolution,
            extent=workflow.target_extent,
            display_names=_d_names,
            descriptions=_d_descs,
            summary=_auto_summary,
            boundary_geometry=clip_geom,
        )
        create_visualization(viz_inputs, workflow.output_dir, workflow.verbose,
                             metadata=viz_meta)
        interactive_map = create_interactive_visualization(
            viz_inputs,
            workflow.target_extent,
            output_dir=workflow.output_dir,
            verbose=workflow.verbose,
        )

    _print_post_run_checklist(workflow.name, workflow.verbose)
    return output_files, interactive_map


def _print_post_run_checklist(project_name: str, verbose: bool) -> None:
    """Print a checklist of required follow-up actions after a workflow runs.

    AGENTS.md mandates several housekeeping steps (catalog updates, doc page,
    PROMPT_ACTION_LOG entry) that no automated test enforces. Printing them
    at end-of-run gives a weak LLM agent a final, unmissable nudge — even if
    they ignored the same instructions in AGENTS.md.
    """
    if not verbose:
        return
    print()
    print("─" * 72)
    print("✅ Harmonization complete. Required follow-up before declaring done:")
    print(f"   [ ] Append a new entry to PROMPT_ACTION_LOG.md (project: {project_name!r})")
    print(f"   [ ] Add any newly used dataset URLs to data_catalog.yml")
    print(f"   [ ] Create docs/workflows/{project_name}.md from the AGENTS.md template")
    print("─" * 72)