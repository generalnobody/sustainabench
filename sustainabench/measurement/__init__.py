from importlib import import_module
from pathlib import Path

from .base import MEASUREMENTS, register_measurement

skip_if_missing = {
    "rapl_pypmt": "pypmt",
}

package_dir = Path(__file__).parent

# Import of all relevant measurements
for file in package_dir.rglob("*.py"):
    if file.stem in ("__init__", "base", "manager"):
        continue    
        
    if file.stem in skip_if_missing:
        dep = skip_if_missing[file.stem]
        try:
            import_module(dep)
        except ModuleNotFoundError:
            continue  # skip this file entirely

    rel_path = file.relative_to(package_dir)

    module_parts = rel_path.with_suffix("").parts
    module_name = ".".join(module_parts)

    import_module(f"{__name__}.{module_name}")
