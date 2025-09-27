"""MCP (Model Context Protocol) integration for AI agent consumption.

This module provides tools for making nodes discoverable and usable by AI agents.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _load_node_manifest(node_path: Path) -> Dict[str, Any]:
    """Load a node's manifest."""
    manifest_path = node_path / "manifest.json"
    if not manifest_path.exists():
        return {}
    
    try:
        return json.loads(manifest_path.read_text())
    except json.JSONDecodeError:
        return {}


def _generate_tool_schema(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Generate MCP tool schema from node manifest.
    
    Args:
        manifest: Node manifest dictionary
        
    Returns:
        MCP tool schema dictionary
    """
    tool_name = manifest.get("name", "UnknownNode")
    description = manifest.get("description", "No description available")
    inputs = manifest.get("inputs", {})
    outputs = manifest.get("outputs", {})
    
    # Generate input schema
    properties = {}
    required = []
    
    for input_name, input_type in inputs.items():
        properties[input_name] = {
            "type": "string" if input_type == "string" else "string",  # Default to string
            "description": f"Input parameter: {input_name}"
        }
        required.append(input_name)
    
    # Generate output schema
    output_properties = {}
    for output_name, output_type in outputs.items():
        output_properties[output_name] = {
            "type": "string" if output_type == "string" else "string",
            "description": f"Output: {output_name}"
        }
    
    return {
        "name": tool_name.lower().replace("node", ""),
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        },
        "outputSchema": {
            "type": "object",
            "properties": output_properties
        }
    }


def generate_mcp_tools() -> List[Dict[str, Any]]:
    """Generate MCP tool schemas for all available nodes.
    
    Returns:
        List of MCP tool schemas
    """
    tools = []
    
    # Get nodes
    nodes_dir = Path.cwd() / "nodes"
    if not nodes_dir.exists():
        return tools
    
    for node_path in nodes_dir.iterdir():
        if node_path.is_dir():
            manifest = _load_node_manifest(node_path)
            if manifest:
                tool_schema = _generate_tool_schema(manifest)
                tool_schema["node_path"] = str(node_path)
                tools.append(tool_schema)
    
    # Get workflows
    workflows_dir = Path.cwd() / "workflows"
    if workflows_dir.exists():
        for workflow_path in workflows_dir.iterdir():
            if workflow_path.is_dir():
                manifest = _load_node_manifest(workflow_path)
                if manifest:
                    tool_schema = _generate_tool_schema(manifest)
                    tool_schema["workflow_path"] = str(workflow_path)
                    tools.append(tool_schema)
    
    return tools


def export_mcp_tools(output_file: str = "mcp_tools.json") -> None:
    """Export MCP tool schemas to a JSON file.
    
    Args:
        output_file: Output file path
    """
    tools = generate_mcp_tools()
    
    output_path = Path.cwd() / output_file
    output_path.write_text(json.dumps(tools, indent=2))
    
    print(f"✅ Exported {len(tools)} MCP tools to {output_path}")
    
    # Show summary
    for tool in tools:
        print(f"🔧 {tool['name']}: {tool['description']}")
        if "node_path" in tool:
            print(f"   📦 Node: {Path(tool['node_path']).name}")
        if "workflow_path" in tool:
            print(f"   🔗 Workflow: {Path(tool['workflow_path']).name}")


def show_mcp_tools() -> None:
    """Display MCP tool schemas in a human-readable format."""
    tools = generate_mcp_tools()
    
    if not tools:
        print("No tools found. Add some nodes first with 'nodebuilder add' or 'nodebuilder add \"owner/repo node-name\"'")
        return
    
    print(f"🤖 MCP Tools ({len(tools)} available):")
    print()
    
    for tool in tools:
        print(f"🔧 {tool['name']}")
        print(f"   Description: {tool['description']}")
        
        # Show inputs
        inputs = tool.get("inputSchema", {}).get("properties", {})
        if inputs:
            print(f"   Inputs: {', '.join(inputs.keys())}")
        
        # Show outputs
        outputs = tool.get("outputSchema", {}).get("properties", {})
        if outputs:
            print(f"   Outputs: {', '.join(outputs.keys())}")
        
        # Show source
        if "node_path" in tool:
            print(f"   Source: Node ({Path(tool['node_path']).name})")
        elif "workflow_path" in tool:
            print(f"   Source: Workflow ({Path(tool['workflow_path']).name})")
        
        print()


def generate_agent_prompt() -> str:
    """Generate a prompt for AI agents describing available tools.
    
    Returns:
        Formatted prompt string
    """
    tools = generate_mcp_tools()
    
    if not tools:
        return "No tools available. Please add nodes first."
    
    prompt = "Available LangGraph Tools:\n\n"
    
    for tool in tools:
        prompt += f"**{tool['name']}**\n"
        prompt += f"- Description: {tool['description']}\n"
        
        inputs = tool.get("inputSchema", {}).get("properties", {})
        if inputs:
            prompt += f"- Inputs: {', '.join(inputs.keys())}\n"
        
        outputs = tool.get("outputSchema", {}).get("properties", {})
        if outputs:
            prompt += f"- Outputs: {', '.join(outputs.keys())}\n"
        
        prompt += "\n"
    
    return prompt
