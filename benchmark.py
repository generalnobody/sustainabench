import typer

# Create the main typer app instance
app = typer.Typer(add_completion=False)

# # Subcommand 1: Greet
# @app.command()
# def greet(name: str, age: int = 30):
#     """Greet the user and optionally mention their age"""
#     print(f"Hello, {name}! You are {age} years old.")

# # Subcommand 2: Info (with multiple arguments)
# @app.command()
# def info(name: str, occupation: str, location: str):
#     """Provide some info about a person"""
#     print(f"{name} is a {occupation} from {location}.")


# Single-core cpu benchmark

# Multi-core cpu benchmark

# GPU benchmark

# CPU/GPU benchmark


# Have available benchmarks as shell/python scripts  in a single folder. This would allow for automatically getting available benchmarks and adding new ones modularly

# The main entry point of the script
def main():
    # Call the Typer app
    app()

# This ensures the script runs only when executed directly
if __name__ == "__main__":
    main()
