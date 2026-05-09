from importlib import import_module
from pathlib import Path
from .base import WORKLOADS, register_workload

# auto-import all workload modules
package_dir = Path(__file__).parent

# Import of all relevant workloads
for file in package_dir.rglob("*.py"):
    if file.stem in ("__init__", "base"):
        continue    
        
    rel_path = file.relative_to(package_dir)

    module_parts = rel_path.with_suffix("").parts
    module_name = ".".join(module_parts)

    import_module(f"{__name__}.{module_name}")
