"""
NodeBuilder CLI — Command Line Interface

This module defines all the command-line commands that users can run.
It's like the "control panel" for NodeBuilder - users type commands here
to add nodes, compose workflows, fetch from GitHub, etc.

Key concepts for beginners:
- CLI (Command Line Interface): Text-based way to interact with programs
- Typer: Python library that makes it easy to create CLI applications
- Commands: Different actions users can perform (add, fetch, compose, etc.)
- Subcommands: Commands organized under categories (node add, workflow compose)
"""

from __future__ import annotations  # Allows using string annotations in older Python versions

import typer  # Library for creating command-line interfaces
from nodebuilder.core import add_node, add_workflow, list_items, fetch, compose, mcp

# Create the main CLI application
app = typer.Typer(help="NodeBuilder CLI — shadcn-style node + workflow templates")


# ================ MAIN COMMANDS ================
# Shadcn-style simple commands

@app.command("add")
def add_command(
    name: str = typer.Argument(..., help="Node name or 'owner/repo node-name' for GitHub"),
):
    """
    Add a node to your project.
    
    Examples:
        nodebuilder add summarizer                    # Add from bundled templates
        nodebuilder add "aryan/nodebuilder summarizer" # Add from GitHub repository
    """
    # Check if it's a GitHub repo format (owner/repo node-name)
    if "/" in name and " " in name:
        parts = name.split()
        if len(parts) == 2:
            repo, node_name = parts
            fetch.fetch_node(repo, node_name)
            return
    
    # Add from bundled templates
    add_node(name)


@app.command("compose")
def compose_command(
    workflow_name: str = typer.Argument(..., help="Name of the workflow to create"),
    node_names: str = typer.Argument(..., help="Space-separated list of node names"),
):
    """
    Compose a workflow from available nodes.
    
    Example:
        nodebuilder compose my-workflow "summarizer translator"
    """
    nodes = node_names.split()
    compose.compose_workflow(workflow_name, nodes)


@app.command("suggest")
def suggest_command():
    """
    Get workflow suggestions based on available nodes.
    
    Example:
        nodebuilder suggest
    """
    compose.suggest_workflows()


@app.command("list")
def list_command():
    """
    List available nodes and workflows in your project.
    
    Example:
        nodebuilder list
    """
    list_items()


@app.command("export-mcp")
def export_mcp_command(output_file: str = "mcp_tools.json"):
    """
    Export MCP tool schemas for AI agents.
    
    Example:
        nodebuilder export-mcp
    """
    mcp.export_mcp_tools(output_file)


# ================ LEGACY COMMANDS (for backward compatibility) ================
# Keep the old commands working but mark them as legacy

@app.command("node")
def legacy_node_command():
    """Legacy node commands. Use 'nodebuilder add' instead."""
    print("⚠️  Legacy command. Use 'nodebuilder add <node-name>' instead.")
    print("   Examples:")
    print("   nodebuilder add summarizer")
    print("   nodebuilder add owner/repo node-name")


@app.command("workflow")
def legacy_workflow_command():
    """Legacy workflow commands. Use 'nodebuilder compose' instead."""
    print("⚠️  Legacy command. Use 'nodebuilder compose <workflow-name> <nodes...>' instead.")
    print("   Example: nodebuilder compose my-workflow summarizer translator")


@app.command("mcp")
def legacy_mcp_command():
    """Legacy MCP command. Use 'nodebuilder export-mcp' instead."""
    print("⚠️  Legacy command. Use 'nodebuilder export-mcp' instead.")
    mcp.show_mcp_tools()


@app.command("agent-prompt")
def legacy_agent_prompt_command():
    """Legacy agent prompt command."""
    prompt = mcp.generate_agent_prompt()
    print(prompt)




if __name__ == "__main__":
    app()