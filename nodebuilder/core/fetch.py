"""
Fetch nodes from external repositories (GitHub, etc.).

This module handles downloading and validating nodes from external sources.
It's like downloading a ZIP file from GitHub and extracting specific files from it.

Key concepts for beginners:
- GitHub API: How to download repository files as ZIP archives
- ZIP handling: Working with compressed files
- URL parsing: Breaking down web addresses into components
- JSON validation: Checking if downloaded files have the right structure
"""

from __future__ import annotations  # Allows using string annotations in older Python versions

import json  # For reading/writing JSON files (like manifests)
import tempfile  # For creating temporary files during download
import zipfile  # For extracting ZIP archives
from pathlib import Path  # Modern path handling
from urllib.parse import urlparse  # For parsing URLs
from urllib.request import urlopen  # For downloading files

import requests  # Popular library for making HTTP requests


def _parse_repo_url(repo: str) -> tuple[str, str]:
    """
    Parse repository URL or owner/repo format.
    
    This function takes either a full GitHub URL or a simple "owner/repo" format
    and extracts the owner and repository name.
    
    Examples:
        - "owner/repo" -> ("owner", "repo")
        - "https://github.com/owner/repo" -> ("owner", "repo")
    
    Args:
        repo: Repository URL or owner/repo format
        
    Returns:
        Tuple of (owner, repo_name)
        
    Raises:
        ValueError: If repo format is invalid
    """
    # Check if it's the simple "owner/repo" format
    if "/" in repo and not repo.startswith(("http://", "https://")):
        # Format: owner/repo
        parts = repo.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repo format: {repo}. Use 'owner/repo' or full URL")
        return parts[0], parts[1]
    
    # Parse full URL
    parsed = urlparse(repo)
    # Check if it's a GitHub URL
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError(f"Only GitHub repositories are supported. Got: {parsed.netloc}")
    
    # Extract owner and repo from URL path
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {repo}")
    
    return path_parts[0], path_parts[1]


def _download_repo_zip(owner: str, repo: str, branch: str = "main") -> bytes:
    """
    Download repository as ZIP file from GitHub.
    
    GitHub provides a special URL format to download entire repositories as ZIP files.
    This is much faster than downloading individual files.
    
    Args:
        owner: Repository owner (GitHub username)
        repo: Repository name
        branch: Branch to download (default: main)
        
    Returns:
        ZIP file content as bytes
        
    Raises:
        requests.RequestException: If download fails (network error, 404, etc.)
    """
    # GitHub's ZIP download URL format
    url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    
    # Download the ZIP file
    response = requests.get(url, timeout=30)
    # Raise an exception if the download failed (404, 500, etc.)
    response.raise_for_status()
    
    # Return the raw ZIP file content
    return response.content


def _extract_node_from_zip(zip_content: bytes, node_name: str) -> dict[str, bytes]:
    """
    Extract a specific node from repository ZIP.
    
    This function opens the downloaded ZIP file, finds the specific node directory,
    and extracts all files from that node into a dictionary.
    
    Args:
        zip_content: ZIP file content as bytes
        node_name: Name of the node to extract (e.g., "summarizer")
        
    Returns:
        Dictionary mapping file paths to file contents
        
    Raises:
        ValueError: If node not found or invalid repository structure
    """
    # Use a temporary directory to work with the ZIP file
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "repo.zip"
        zip_path.write_bytes(zip_content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Find the root directory (GitHub adds branch name to zip)
            # e.g., "repo-main/" or "repo-master/"
            root_dirs = [name for name in zip_file.namelist() 
                        if name.endswith('/') and name.count('/') == 1]
            if not root_dirs:
                raise ValueError("Invalid repository structure")
            
            root_dir = root_dirs[0]
            
            # Look for nodes directory
            nodes_dir = f"{root_dir}nodes/"
            node_files = [name for name in zip_file.namelist() 
                         if name.startswith(nodes_dir) and name != nodes_dir]
            
            if not node_files:
                raise ValueError(f"No nodes directory found in repository")
            
            # Find the specific node directory
            target_node_dir = f"{nodes_dir}{node_name}/"
            node_files = [name for name in zip_file.namelist() 
                         if name.startswith(target_node_dir)]
            
            if not node_files:
                # Build a helpful error message with available nodes
                available_nodes = set()
                for name in zip_file.namelist():
                    if name.startswith(nodes_dir) and name != nodes_dir:
                        parts = name[len(nodes_dir):].split('/')
                        if parts[0]:
                            available_nodes.add(parts[0])
                
                raise ValueError(f"Node '{node_name}' not found. Available nodes: {sorted(available_nodes)}")
            
            # Extract all files from the node directory
            node_data = {}
            for file_path in node_files:
                if not file_path.endswith('/'):  # Skip directories
                    # Get the relative path within the node directory
                    relative_path = file_path[len(target_node_dir):]
                    # Read the file content
                    node_data[relative_path] = zip_file.read(file_path)
            
            return node_data


def _validate_node_structure(node_data: dict[str, bytes]) -> None:
    """
    Validate that the node has required structure.
    
    This function checks that the downloaded node has all the required files
    and that the manifest.json file is valid.
    
    Args:
        node_data: Dictionary of node files (filename -> content)
        
    Raises:
        ValueError: If node structure is invalid
    """
    # Check for required files
    if "manifest.json" not in node_data:
        raise ValueError("Node must have a manifest.json file")
    
    if "node.py" not in node_data:
        raise ValueError("Node must have a node.py file")
    
    # Validate manifest.json structure
    try:
        manifest = json.loads(node_data["manifest.json"].decode('utf-8'))
        required_fields = ["name", "description", "inputs", "outputs"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Manifest missing required field: {field}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid manifest.json: {e}")


def fetch_node(repo: str, node_name: str, branch: str = "main") -> None:
    """
    Fetch a node from an external repository.
    
    This is the main function that users call to download nodes from GitHub.
    It handles the entire process: parsing the repo URL, downloading, extracting,
    validating, and saving the node to the local project.
    
    Args:
        repo: Repository URL or owner/repo format (e.g., "owner/repo" or "https://github.com/owner/repo")
        node_name: Name of the node to fetch (e.g., "summarizer")
        branch: Branch to fetch from (default: main)
        
    Raises:
        ValueError: If repo format is invalid or node not found
        requests.RequestException: If download fails
        FileExistsError: If target directory already exists
    """
    print(f"Fetching node '{node_name}' from {repo}...")
    
    # Step 1: Parse the repository URL to get owner and repo name
    owner, repo_name = _parse_repo_url(repo)
    print(f"Repository: {owner}/{repo_name}")
    
    # Step 2: Download the repository as a ZIP file
    print("Downloading repository...")
    zip_content = _download_repo_zip(owner, repo_name, branch)
    
    # Step 3: Extract the specific node from the ZIP
    print(f"Extracting node '{node_name}'...")
    node_data = _extract_node_from_zip(zip_content, node_name)
    
    # Step 4: Validate that the node has the correct structure
    print("Validating node structure...")
    _validate_node_structure(node_data)
    
    # Step 5: Save the node to the local project
    target_dir = Path.cwd() / "nodes" / node_name
    if target_dir.exists():
        raise FileExistsError(
            f"Node '{node_name}' already exists at {target_dir}. "
            f"Remove it first or choose another name."
        )
    
    # Create the target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Write all files to the target directory
    for file_path, content in node_data.items():
        file_path = target_dir / file_path
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Write the file content
        file_path.write_bytes(content)
    
    print(f"✅ Node '{node_name}' successfully fetched to {target_dir}")
    
    # Step 6: Show information about the fetched node
    manifest_path = target_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    print(f"📋 {manifest['name']}: {manifest['description']}")
    print(f"🔧 Inputs: {list(manifest['inputs'].keys())}")
    print(f"📤 Outputs: {list(manifest['outputs'].keys())}")
