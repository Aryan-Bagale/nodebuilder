"""
Registry system for managing available nodes and their sources.

This module provides a centralized registry that maps node names to their sources,
similar to how shadcn/ui manages component availability. It allows users to add
nodes by name without specifying repository details.

Key concepts:
- Registry: Centralized mapping of node names to their sources
- Bundled nodes: Nodes included with the package
- External nodes: Nodes fetched from GitHub repositories
- Node metadata: Description, category, and source information
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from importlib import resources


def _load_registry() -> Dict[str, Any]:
    """
    Load the node registry from the package.
    
    Returns:
        Dictionary containing node registry data
    """
    try:
        # Load registry from package resources
        registry_file = resources.files("nodebuilder").joinpath("registry.json")
        registry_data = json.loads(registry_file.read_text())
        return registry_data
    except Exception as e:
        print(f"Warning: Could not load registry: {e}")
        return {}


def get_available_nodes() -> Dict[str, Any]:
    """
    Get all available nodes from the registry.
    
    Returns:
        Dictionary mapping node names to their metadata
    """
    return _load_registry()


def get_node_info(node_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific node from the registry.
    
    Args:
        node_name: Name of the node to look up
        
    Returns:
        Node metadata dictionary or None if not found
    """
    registry = _load_registry()
    return registry.get(node_name)


def is_node_available(node_name: str) -> bool:
    """
    Check if a node is available in the registry.
    
    Args:
        node_name: Name of the node to check
        
    Returns:
        True if node is available, False otherwise
    """
    return node_name in _load_registry()


def get_nodes_by_category(category: str) -> Dict[str, Any]:
    """
    Get all nodes in a specific category.
    
    Args:
        category: Category to filter by (e.g., "text-processing", "vision")
        
    Returns:
        Dictionary of nodes in the specified category
    """
    registry = _load_registry()
    return {
        name: info for name, info in registry.items()
        if info.get("category") == category
    }


def list_available_nodes() -> None:
    """
    Display all available nodes in a formatted list.
    """
    registry = _load_registry()
    
    if not registry:
        print("No nodes available in registry.")
        return
    
    print("📦 Available Nodes:")
    print()
    
    # Group by category
    categories = {}
    for name, info in registry.items():
        category = info.get("category", "uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append((name, info))
    
    for category, nodes in categories.items():
        print(f"🔹 {category.replace('-', ' ').title()}:")
        for name, info in nodes:
            description = info.get("description", "No description")
            print(f"   🌐 {name}: {description}")
        print()


def search_nodes(query: str) -> Dict[str, Any]:
    """
    Search for nodes by name or description.
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary of matching nodes
    """
    registry = _load_registry()
    query_lower = query.lower()
    
    matches = {}
    for name, info in registry.items():
        # Search in name
        if query_lower in name.lower():
            matches[name] = info
            continue
            
        # Search in description
        description = info.get("description", "").lower()
        if query_lower in description:
            matches[name] = info
            continue
            
        # Search in category
        category = info.get("category", "").lower()
        if query_lower in category:
            matches[name] = info
    
    return matches
