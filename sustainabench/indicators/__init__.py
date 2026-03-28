from importlib import import_module
from pathlib import Path

from .base import INDICATORS, register_indicator

package_dir = Path(__file__).parent

for file in package_dir.glob("*.py"):
    if file.stem not in ("__init__", "base"):
        import_module(f"{__name__}.{file.stem}")
