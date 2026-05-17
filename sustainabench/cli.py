import typer
import importlib
import pkgutil
import sustainabench.commands as commands

# Start typer instance
app = typer.Typer(help="SustainaBench benchmarking framework", add_completion=False)

# Auto-register commands from commands folder
for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
    module = importlib.import_module(f"{commands.__name__}.{module_name}")
    
    if hasattr(module, "app"):
        app.add_typer(module.app, name=module_name)

    if not hasattr(module, "app"):
        raise ValueError(f"{module_name} has no 'app'")

# Run the app
if __name__ == "__main__":
    app()
