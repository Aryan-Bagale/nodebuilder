# NodeBuilder

Beautifully designed, copy and paste LangGraph nodes and workflows into your project.

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

## Add nodes from GitHub

You can also add nodes from any GitHub repository.

```bash
nodebuilder add "owner/repo node-name"
```

For example:

```bash
nodebuilder add "aryan/nodebuilder summarizer"
nodebuilder add "langchain-ai/langgraph-nodes translator"
```

## Compose workflows

Create workflows by chaining multiple nodes together.

```bash
nodebuilder compose my-workflow summarizer translator
```

This creates a workflow that first summarizes text, then translates it.

## Available nodes

- `summarizer` - Truncates text to 200 characters (demo summarizer)
- `translator` - Translates text to target language

## Philosophy

- **Copy, don't install** - Copy the source code into your project
- **Own your code** - You own and control the code
- **Framework ready** - Works seamlessly with LangGraph
- **AI friendly** - Export tools for AI agents

## Commands

### Add nodes
```bash
nodebuilder add <node-name>                    # Add from bundled templates
nodebuilder add "owner/repo node-name"         # Add from GitHub repository
```

### Compose workflows
```bash
nodebuilder compose <workflow-name> <nodes...>  # Create workflow from nodes
nodebuilder suggest                             # Get workflow suggestions
```

### Utilities
```bash
nodebuilder list                               # List available nodes and workflows
nodebuilder export-mcp                         # Export tools for AI agents
```