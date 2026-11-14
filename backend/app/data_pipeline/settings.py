"""
FlameLens - NASA PSI Data Pipeline
Central configuration and settings.
"""

import os
from pathlib import Path


# =====================================================
# 1. NASA CONFIGURATION
# =====================================================

NASA_BASE_URL = "https://psi.nasa.gov"

NASA_SEARCH_URL = (
    f"{NASA_BASE_URL}/physci/repo/search"
    "?q=combustion"
    "&data_source=psi"
    "&data_type=investigation"
)


# =====================================================
# 2. PROJECT PATHS
# =====================================================

# Project structure:
# flamelens/
#   backend/
#     app/
#       data_pipeline/
#         settings.py

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_ROOT = Path(
    os.getenv(
        "FLAMELENS_DATA_ROOT",
        str(PROJECT_ROOT / "nasa_psi_data")
    )
)

DOWNLOAD_ROOT = DATA_ROOT / "downloads"

REPORT_ROOT = DATA_ROOT / "reports"

LOG_ROOT = DATA_ROOT / "logs"

INVENTORY_PATH = DATA_ROOT / "inventory.json"


# =====================================================
# 3. DOWNLOAD CONFIGURATION
# =====================================================

# Maximum storage per investigation
PER_INVESTIGATION_LIMIT_MB = 500

# Allowed automatic Raw Data overrun
RAW_AUTO_OVERRUN_MB = 5


# =====================================================
# 4. TIMEOUT CONFIGURATION
# =====================================================

# Navigation timeout: 5 minutes
NAV_TIMEOUT_MS = 300_000

# Waiting for investigation page elements
PAGE_READY_TIMEOUT_MS = 300_000

# General element timeout
ELEMENT_TIMEOUT_MS = 90_000

# Download timeout: 3 minutes
DOWNLOAD_TIMEOUT_MS = 180_000

# Wait after expanding folders
TREE_SETTLE_MS = 2_000


# =====================================================
# 5. RETRY CONFIGURATION
# =====================================================

MAX_NETWORK_RETRIES = 3

MAX_DOWNLOAD_RETRIES = 3

RETRY_BASE_SECONDS = 2

MAX_TREE_ACTIONS = 5_000

MAX_SEARCH_PAGES = 100


# =====================================================
# 6. BROWSER CONFIGURATION
# =====================================================

BROWSER_NAME = "chromium"

HEADLESS = True


# =====================================================
# 7. FILE CONFIGURATION
# =====================================================

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
    ".svg",
}


# =====================================================
# 8. DIRECTORY INITIALIZATION
# =====================================================

def initialize_directories():
    """
    Create required data directories if they do not exist.
    """

    directories = [
        DATA_ROOT,
        DOWNLOAD_ROOT,
        REPORT_ROOT,
        LOG_ROOT,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )