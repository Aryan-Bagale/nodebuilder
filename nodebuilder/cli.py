"""
NodeBuilder CLI — shadcn-style node templates

Simple CLI to add LangGraph nodes to your project, just like shadcn/ui.
"""

import json
import requests
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List

import typer


def load_registry() -> Dict[str, Any]:
    """Load the registry from GitHub repository."""
    try:
        # Fetch registry from GitHub
        url = "https://raw.githubusercontent.com/Aryan-Bagale/nodebuilder/main/registry.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to load registry: {e}")
        return {}


def get_available_components() -> List[Dict[str, Any]]:
    """Get list of available components from registry."""
    registry = load_registry()
    return registry.get("registry", [])


def add_component(name: str) -> None:
    """Add a component to the project."""
    components = get_available_components()
    
    # Find the component
    component = None
    for comp in components:
        if comp["name"] == name:
            component = comp
            break
    
    if not component:
        print(f"❌ Component '{name}' not found.")
        print("\nAvailable components:")
        for comp in components:
            print(f"  • {comp['name']}: {comp['description']}")
        return
    
    # Create components directory if it doesn't exist
    components_dir = Path.cwd() / "components"
    components_dir.mkdir(exist_ok=True)
    
    # Create component directory
    component_dir = components_dir / name
    if component_dir.exists():
        print(f"❌ Component '{name}' already exists.")
        return
    
    component_dir.mkdir()
    
    # Write component files
    for file_info in component["files"]:
        file_path = component_dir / file_info["name"]
        file_path.write_text(file_info["content"])
    
    print(f"✅ Added {name} component to {component_dir}")


def list_components() -> None:
    """List all available components."""
    components = get_available_components()
    
    if not components:
        print("No components available.")
        return
    
    print("Available components:")
    for comp in components:
        print(f"  • {comp['name']}: {comp['description']}")


# Create the CLI app
app = typer.Typer(help="NodeBuilder CLI — shadcn-style node templates")


@app.command("add")
def add_command(
    name: str = typer.Argument(..., help="Component name to add"),
):
    """
    Add a component to your project.
    
    Example:
        nodebuilder add summarizer
    """
    add_component(name)


@app.command("list")
def list_command():
    """
    List all available components.
    
    Example:
        nodebuilder list
    """
    list_components()


if __name__ == "__main__":
    app()