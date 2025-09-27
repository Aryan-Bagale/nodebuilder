# NodeBuilder

Under development

## Installation

```bash
pip install nodebuilder
```

## Usage

The easiest way to get started is to add a node to your project.

```bash
nodebuilder add summarizer
```

This will add the `summarizer` node to your project. You can then import and use it in your code.

```python
from nodes.summarizer.node import SummarizerNode

# Use the node
summarizer = SummarizerNode()
result = summarizer.run("Your text to summarize here")
```

## Browse Available Nodes

See all available nodes in the registry:

```bash
nodebuilder registry
```

This shows all nodes organized by category, all fetched from the GitHub repository.

## Compose workflows

Create workflows by chaining multiple nodes together.

```bash
nodebuilder compose my-workflow "summarizer translator"
```

This creates a workflow that first summarizes text, then translates it.

## AI Agent Integration

Export your nodes and workflows as tools for AI agents using the Model Context Protocol (MCP).

```bash
nodebuilder export-mcp
```

This creates `mcp_tools.json` with schemas that AI agents can understand and use.

```python
# AI agents can discover and use your tools
from mcp_tools import load_tools
tools = load_tools("mcp_tools.json")
# Agent can now use summarizer, translator, and workflows as tools
```

## Available nodes

Browse all available nodes with:

```bash
nodebuilder registry
```

Some examples:
- `summarizer` - Truncates text to 200 characters (demo summarizer)
- `translator` - Translates text to target language
- `sentiment-analyzer` - Analyzes sentiment of text input
- `text-classifier` - Classifies text into predefined categories

## Philosophy

- **Copy, don't install** - Copy the source code into your project
- **Own your code** - You own and control the code
- **Framework ready** - Works seamlessly with LangGraph
- **AI friendly** - Export tools for AI agents

## Commands

### Add nodes
```bash
nodebuilder add <node-name>                    # Add from GitHub
nodebuilder registry                           # Browse available nodes
```

### Compose workflows
```bash
nodebuilder compose <workflow-name> "<nodes...>"  # Create workflow from nodes
nodebuilder suggest                              # Get workflow suggestions
```

### Utilities
```bash
nodebuilder list                               # List available nodes and workflows
nodebuilder export-mcp                         # Export tools for AI agents
```
