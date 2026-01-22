"""
Pytest configuration and fixtures.
"""

import sys
import os
from pathlib import Path

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "apps" / "api"))
sys.path.insert(0, str(project_root / "apps" / "worker"))
