"""
pytest configuration.

Sets PROJ_DATA before any geo library is imported so that rasterio and pyproj
use the same PROJ database. In environments where the pip-installed pyproj
differs from the system PROJ (common on JupyterHub / conda-forge), the system
proj.db can be outdated, causing "EPSG code unknown" errors. Setting PROJ_DATA
early points both libraries at pyproj's bundled database.

CI (fresh ubuntu install) is unaffected — this only matters locally.
"""

import os
import sys
from pathlib import Path

# ── Must happen before any rasterio / pyproj import ──────────────────────────
def _find_proj_data() -> str | None:
    """Find the most up-to-date bundled PROJ data directory (prefer rasterio's)."""
    for base in sys.path:
        # rasterio wheels bundle their own proj_data — prefer this
        for rel in ("rasterio/proj_data", "pyogrio/proj_data",
                    "pyproj/proj_dir/share/proj"):
            candidate = Path(base) / rel
            if (candidate / "proj.db").exists():
                return str(candidate)
    return None

_proj_data = _find_proj_data()
if _proj_data:
    os.environ["PROJ_DATA"] = _proj_data
    os.environ["PROJ_LIB"] = _proj_data

# ── Ensure repo root is on sys.path ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
