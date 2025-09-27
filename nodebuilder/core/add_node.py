"""
Copy node templates bundled inside the package into the user's project.

This module handles copying pre-built node templates from the package's internal
templates directory to the user's local project directory. It's like copying
files from a template folder to your working directory.

Key concepts for beginners:
- importlib.resources: Modern way to access files bundled with Python packages
- Path objects: Cross-platform way to handle file paths
- Traversable: A special object that represents files/folders in packages
"""

from __future__ import annotations  # Allows using string annotations in older Python versions

from pathlib import Path  # Modern, cross-platform path handling
from importlib import resources  # Access files bundled with the package


def _get_template_root() -> resources.Traversable:
    """
    Get the root directory of bundled templates.
    
    This function finds where the template files are stored inside the package.
    Think of it like finding the "templates" folder inside the nodebuilder package.
    
    Returns:
        A Traversable object pointing to the templates directory
    """
    # Get the nodebuilder package
    pkg = resources.files("nodebuilder")
    # Navigate to the templates subdirectory
    tpl = pkg.joinpath("templates")
    return tpl


def _copy_traversable(src: resources.Traversable, dest_path: Path) -> None:
    """
    Recursively copy files and folders from package resources to local filesystem.
    
    This is like copying files from a ZIP archive to your computer.
    It handles both individual files and entire folder structures.
    
    Args:
        src: Source file/folder in the package
        dest_path: Destination path on the local filesystem
    """
    if src.is_file():
        # If it's a file, copy it directly
        # First, make sure the parent directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        # Read the file content as bytes
        data = src.read_bytes()
        # Write it to the destination
        dest_path.write_bytes(data)
    else:
        # If it's a directory, create it and copy its contents
        dest_path.mkdir(parents=True, exist_ok=True)
        # Recursively copy each item in the directory
        for child in src.iterdir():
            _copy_traversable(child, dest_path / child.name)


def add_node(name: str) -> None:
    """
    Copy a node template from the package to the user's project.
    
    This is the main function that users call. It takes a node name (like "summarizer")
    and copies the corresponding template files to the user's ./nodes/ directory.
    
    Args:
        name: Name of the node template to copy (e.g., "summarizer", "translator")
        
    Raises:
        FileNotFoundError: If the requested node template doesn't exist
        FileExistsError: If the target directory already exists
    """
    # Get the root of all templates
    tpl_root = _get_template_root()
    # Build the path to the specific node template
    node_tpl = tpl_root.joinpath("nodes").joinpath(name)
    
    # Check if the template exists
    if not node_tpl.exists():
        # Get list of available nodes for helpful error message
        available_nodes = [p.name for p in tpl_root.joinpath("nodes").iterdir() if p.is_dir()]
        raise FileNotFoundError(
            f"Template node '{name}' not found in package templates. "
            f"Available nodes: {available_nodes}"
        )

    # Define where to copy the template in the user's project
    target_dir = Path.cwd() / "nodes" / name
    
    # Check if the target already exists (prevent overwriting)
    if target_dir.exists():
        raise FileExistsError(
            f"Target directory {target_dir} already exists. "
            f"Remove it first or choose another node name."
        )

    # Copy the template files
    _copy_traversable(node_tpl, target_dir)
    print(f"Node '{name}' added to {target_dir}")