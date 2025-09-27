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


# Create sub-applications for different command categories
node_app = typer.Typer(help="Add or manage nodes")
workflow_app = typer.Typer(help="Add or manage workflows")

# Add the sub-applications to the main app
app.add_typer(node_app, name="node")
app.add_typer(workflow_app, name="workflow")


# ================ NODE COMMANDS ================
# These commands are for working with individual nodes

@node_app.command("add")
def add_node_command(name: str):
    """
    Add a node into the current project from bundled templates.
    
    This command copies a pre-built node template from the NodeBuilder package
    into your local project. The node will be available in the ./nodes/ directory.
    
    Args:
        name: Name of the node template to add (e.g., "summarizer", "translator")
        
    Example:
        nodebuilder node add summarizer
    """
    add_node(name)


@node_app.command("fetch")
def fetch_node_command(repo: str, node_name: str, branch: str = "main"):
    """
    Fetch a node from an external repository (GitHub).
    
    This command downloads a node from a GitHub repository and adds it to your
    local project. It's like copying code from someone else's GitHub repo.
    
    Args:
        repo: Repository URL or owner/repo format
        node_name: Name of the node to fetch from the repository
        branch: Git branch to fetch from (default: main)
        
    Examples:
        nodebuilder node fetch owner/repo summarizer
        nodebuilder node fetch https://github.com/owner/repo translator --branch main
    """
    fetch.fetch_node(repo, node_name, branch)


# ================ WORKFLOW COMMANDS ================
# These commands are for working with workflows (compositions of nodes)

@workflow_app.command("add")
def add_workflow_command(name: str):
    """
    Add a workflow into the current project from bundled templates.
    
    This command copies a pre-built workflow template from the NodeBuilder package
    into your local project. The workflow will be available in the ./workflows/ directory.
    
    Args:
        name: Name of the workflow template to add
        
    Example:
        nodebuilder workflow add summarize_and_translate
    """
    add_workflow(name)


@workflow_app.command("compose")
def compose_workflow_command(workflow_name: str, node_names: str):
    """
    Compose a workflow from available nodes.
    
    This command creates a new workflow by automatically connecting existing nodes
    in sequence. It generates Python code that chains the nodes together.
    
    Args:
        workflow_name: Name for the new workflow
        node_names: Space-separated list of node names to chain together
        
    Example:
        nodebuilder workflow compose my_workflow summarizer translator
    """
    nodes = node_names.split()
    compose.compose_workflow(workflow_name, nodes)


@workflow_app.command("suggest")
def suggest_workflows_command():
    """
    Suggest possible workflows based on available nodes.
    
    This command analyzes your available nodes and suggests workflows you could create.
    It's like having an assistant that looks at your tools and suggests how to use them together.
    
    Example:
        nodebuilder workflow suggest
    """
    compose.suggest_workflows()


# ================ UTILITY COMMANDS ================
# These commands help you discover and manage your nodes/workflows

@app.command("list")
def list_all():
    """
    List nodes and workflows present in the current project.
    
    This command shows you all the nodes and workflows you have in your project,
    along with their descriptions. It's like a directory listing with extra info.
    
    Example:
        nodebuilder list
    """
    list_items()


# ================ AI AGENT INTEGRATION ================
# These commands help AI agents discover and use your nodes/workflows

@app.command("mcp")
def show_mcp_tools():
    """
    Show MCP tool schemas for AI agent consumption.
    
    MCP (Model Context Protocol) is a standard for AI agents to discover and use tools.
    This command shows how your nodes/workflows appear to AI agents.
    
    Example:
        nodebuilder mcp
    """
    mcp.show_mcp_tools()


@app.command("export-mcp")
def export_mcp_tools(output_file: str = "mcp_tools.json"):
    """
    Export MCP tool schemas to JSON file for AI agents.
    
    This command creates a JSON file that AI agents can read to understand
    what tools (nodes/workflows) are available in your project.
    
    Args:
        output_file: Name of the JSON file to create (default: mcp_tools.json)
        
    Example:
        nodebuilder export-mcp
        nodebuilder export-mcp my_tools.json
    """
    mcp.export_mcp_tools(output_file)


@app.command("agent-prompt")
def generate_agent_prompt():
    """
    Generate a prompt describing available tools for AI agents.
    
    This command creates a text description of all your nodes/workflows that
    you can give to an AI agent to help it understand what tools are available.
    
    Example:
        nodebuilder agent-prompt
    """
    prompt = mcp.generate_agent_prompt()
    print(prompt)




if __name__ == "__main__":
    app()