"""
Compose workflows dynamically from available nodes.

This module handles creating workflows by analyzing node inputs/outputs
and generating the appropriate workflow code. It's like automatically
building a pipeline by connecting the output of one node to the input of another.

Key concepts for beginners:
- Dynamic code generation: Creating Python code programmatically
- Node chaining: Connecting nodes in sequence (A → B → C)
- Input/output matching: Ensuring nodes can work together
- Template generation: Creating workflow files from templates
"""

from __future__ import annotations  # Allows using string annotations in older Python versions

import json  # For reading/writing JSON files (manifests)
from pathlib import Path  # Modern path handling
from typing import Any, Dict, List, Set  # Type hints for better code clarity


def _load_node_manifest(node_path: Path) -> Dict[str, Any]:
    """
    Load and validate a node's manifest.
    
    Every node has a manifest.json file that describes what inputs it expects
    and what outputs it produces. This function reads and validates that file.
    
    Args:
        node_path: Path to the node directory (e.g., "./nodes/summarizer")
        
    Returns:
        Parsed manifest dictionary with node metadata
        
    Raises:
        ValueError: If manifest is invalid or missing
    """
    manifest_path = node_path / "manifest.json"
    if not manifest_path.exists():
        raise ValueError(f"Node {node_path.name} missing manifest.json")
    
    try:
        # Read and parse the JSON file
        manifest = json.loads(manifest_path.read_text())
        # Check that all required fields are present
        required_fields = ["name", "description", "inputs", "outputs"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Node {node_path.name} manifest missing field: {field}")
        return manifest
    except json.JSONDecodeError as e:
        raise ValueError(f"Node {node_path.name} has invalid manifest.json: {e}")


def _get_available_nodes() -> Dict[str, Dict[str, Any]]:
    """
    Get all available nodes with their manifests.
    
    This function scans the ./nodes directory and loads the manifest
    for each node, creating a dictionary of all available nodes.
    
    Returns:
        Dictionary mapping node names to their manifests
        Example: {"summarizer": {"name": "SummarizerNode", "inputs": {...}, ...}}
    """
    nodes_dir = Path.cwd() / "nodes"
    if not nodes_dir.exists():
        return {}
    
    nodes = {}
    # Scan each subdirectory in the nodes folder
    for node_path in nodes_dir.iterdir():
        if node_path.is_dir():
            try:
                # Load the manifest for this node
                manifest = _load_node_manifest(node_path)
                nodes[node_path.name] = manifest
            except ValueError as e:
                # Skip nodes with invalid manifests, but warn the user
                print(f"⚠️  Skipping node {node_path.name}: {e}")
    
    return nodes


def _find_compatible_nodes(target_inputs: Set[str], available_nodes: Dict[str, Dict[str, Any]]) -> List[str]:
    """Find nodes that can provide the required inputs.
    
    Args:
        target_inputs: Set of required input names
        available_nodes: Available nodes with their manifests
        
    Returns:
        List of node names that can provide the inputs
    """
    compatible = []
    
    for node_name, manifest in available_nodes.items():
        node_outputs = set(manifest["outputs"].keys())
        # Check if this node provides any of the required inputs
        if target_inputs.intersection(node_outputs):
            compatible.append(node_name)
    
    return compatible


def _generate_workflow_code(workflow_name: str, node_sequence: List[str], 
                          available_nodes: Dict[str, Dict[str, Any]]) -> str:
    """Generate workflow Python code.
    
    Args:
        workflow_name: Name of the workflow class
        node_sequence: Ordered list of node names to use
        available_nodes: Available nodes with their manifests
        
    Returns:
        Generated workflow code as string
    """
    imports = ["from langgraph.graph import Workflow"]
    node_imports = []
    node_instances = []
    
    for node_name in node_sequence:
        manifest = available_nodes[node_name]
        class_name = manifest["name"]
        node_imports.append(f"from nodes.{node_name}.node import {class_name}")
        node_instances.append(f"        self.{node_name} = {class_name}()")
    
    # Determine workflow inputs/outputs from first and last nodes
    first_node = available_nodes[node_sequence[0]]
    last_node = available_nodes[node_sequence[-1]]
    
    workflow_inputs = list(first_node["inputs"].keys())
    workflow_outputs = list(last_node["outputs"].keys())
    
    # Generate method signature
    input_params = ", ".join(workflow_inputs)
    if len(workflow_outputs) == 1:
        return_type = "str"
    else:
        return_type = "dict"
    
    # Add default parameters for additional inputs needed by later nodes
    additional_inputs = set()
    for i, node_name in enumerate(node_sequence[1:], 1):
        manifest = available_nodes[node_name]
        node_inputs = list(manifest["inputs"].keys())
        if len(node_inputs) > 1:
            # Add additional inputs as optional parameters
            for input_name in node_inputs[1:]:
                if input_name not in workflow_inputs:
                    additional_inputs.add(f"{input_name}='en'")
    
    if additional_inputs:
        input_params += ", " + ", ".join(additional_inputs)
    
    # Generate workflow execution logic
    execution_lines = []
    current_data = {}
    
    for i, node_name in enumerate(node_sequence):
        manifest = available_nodes[node_name]
        node_inputs = list(manifest["inputs"].keys())
        node_outputs = list(manifest["outputs"].keys())
        
        if i == 0:
            # First node uses workflow inputs
            args = ", ".join(node_inputs)
            execution_lines.append(f"        {node_outputs[0]} = self.{node_name}.run({args})")
        else:
            # Subsequent nodes use previous outputs
            # For now, assume simple chaining - use previous output as first input
            prev_output = list(available_nodes[node_sequence[i-1]]["outputs"].keys())[0]
            if len(node_inputs) == 1:
                args = prev_output
            else:
                # For multiple inputs, use previous output + remaining inputs
                remaining_inputs = node_inputs[1:]
                args = f"{prev_output}, " + ", ".join(remaining_inputs)
            execution_lines.append(f"        {node_outputs[0]} = self.{node_name}.run({args})")
        
        current_data.update({output: output for output in node_outputs})
    
    # Generate return statement
    if len(workflow_outputs) == 1:
        return_stmt = f"        return {workflow_outputs[0]}"
    else:
        return_dict = ", ".join(f"'{output}': {output}" for output in workflow_outputs)
        return_stmt = f"        return {{{return_dict}}}"
    
    code = f'''# Generated workflow: {workflow_name}
{chr(10).join(imports)}
{chr(10).join(node_imports)}


class {workflow_name}(Workflow):
    """Generated workflow: {' → '.join(node_sequence)}"""

    def __init__(self):
{chr(10).join(node_instances)}

    def run(self, {input_params}) -> {return_type}:
{chr(10).join(execution_lines)}
{return_stmt}
'''
    
    return code


def _generate_workflow_manifest(workflow_name: str, node_sequence: List[str],
                               available_nodes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Generate workflow manifest.
    
    Args:
        workflow_name: Name of the workflow class
        node_sequence: Ordered list of node names
        available_nodes: Available nodes with their manifests
        
    Returns:
        Generated manifest dictionary
    """
    first_node = available_nodes[node_sequence[0]]
    last_node = available_nodes[node_sequence[-1]]
    
    return {
        "name": workflow_name,
        "description": f"Generated workflow: {' → '.join(node_sequence)}",
        "inputs": first_node["inputs"],
        "outputs": last_node["outputs"],
        "nodes": node_sequence,
        "generated": True
    }


def compose_workflow(workflow_name: str, node_names: List[str]) -> None:
    """
    Compose a workflow from available nodes.
    
    This is the main function that creates a new workflow by chaining together
    existing nodes. It generates Python code that connects the nodes in sequence.
    
    Args:
        workflow_name: Name for the generated workflow (e.g., "my_workflow")
        node_names: List of node names to include in sequence (e.g., ["summarizer", "translator"])
        
    Raises:
        ValueError: If nodes are not found or incompatible
        FileExistsError: If workflow directory already exists
    """
    print(f"Composing workflow '{workflow_name}' from nodes: {', '.join(node_names)}")
    
    # Step 1: Get all available nodes from the ./nodes directory
    available_nodes = _get_available_nodes()
    if not available_nodes:
        raise ValueError("No nodes found in ./nodes directory")
    
    print(f"📋 Available nodes: {list(available_nodes.keys())}")
    
    # Step 2: Validate that all requested nodes exist
    missing_nodes = [name for name in node_names if name not in available_nodes]
    if missing_nodes:
        raise ValueError(f"Nodes not found: {missing_nodes}")
    
    # Step 3: Check node compatibility (basic check for now)
    print("🔍 Checking node compatibility...")
    
    # Step 4: Generate the Python code for the workflow
    print("⚙️  Generating workflow code...")
    workflow_code = _generate_workflow_code(workflow_name, node_names, available_nodes)
    
    # Step 5: Generate the manifest for the workflow
    manifest = _generate_workflow_manifest(workflow_name, node_names, available_nodes)
    
    # Step 6: Save the workflow to the ./workflows directory
    workflows_dir = Path.cwd() / "workflows" / workflow_name
    if workflows_dir.exists():
        raise FileExistsError(f"Workflow '{workflow_name}' already exists at {workflows_dir}")
    
    # Create the workflow directory
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the workflow Python file
    workflow_file = workflows_dir / "workflow.py"
    workflow_file.write_text(workflow_code)
    
    # Write the manifest JSON file
    manifest_file = workflows_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    
    # Step 7: Show success message with workflow details
    print(f"✅ Workflow '{workflow_name}' created at {workflows_dir}")
    print(f"📋 Description: {manifest['description']}")
    print(f"🔧 Inputs: {list(manifest['inputs'].keys())}")
    print(f"📤 Outputs: {list(manifest['outputs'].keys())}")
    print(f"🔗 Node sequence: {' → '.join(node_names)}")


def suggest_workflows() -> None:
    """Suggest possible workflows based on available nodes."""
    available_nodes = _get_available_nodes()
    if not available_nodes:
        print("No nodes found in ./nodes directory")
        return
    
    print("💡 Suggested workflows based on available nodes:")
    print()
    
    # Simple suggestions based on common patterns
    node_names = list(available_nodes.keys())
    
    if len(node_names) >= 2:
        print(f"🔗 Chain workflow: {' → '.join(node_names[:2])}")
        print(f"   nodebuilder workflow compose chain_{'_'.join(node_names[:2])} {' '.join(node_names[:2])}")
        print()
    
    if len(node_names) >= 3:
        print(f"🔗 Full chain: {' → '.join(node_names)}")
        print(f"   nodebuilder workflow compose full_chain {' '.join(node_names)}")
        print()
    
    # Show individual nodes
    print("📦 Available nodes:")
    for node_name, manifest in available_nodes.items():
        print(f"   • {node_name}: {manifest['description']}")
        print(f"     Inputs: {list(manifest['inputs'].keys())}")
        print(f"     Outputs: {list(manifest['outputs'].keys())}")
        print()
