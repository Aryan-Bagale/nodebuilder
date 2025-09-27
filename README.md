# NodeBuilder

Shadcn-style CLI for LangGraph nodes and workflows. Copy node/workflow source
code directly into your project so you own and control the code.

**🚀 Now supports the full AI building blocks ecosystem:**
- Fetch nodes from GitHub repositories
- Compose workflows dynamically from available nodes
- Export MCP tools for AI agent consumption
- Framework-ready nodes with metadata and manifests

## Quick start

```bash
# install (from local during development)
pip install -e .

# fetch nodes from external repositories
nodebuilder node fetch owner/repo summarizer
nodebuilder node fetch https://github.com/owner/repo translator --branch main

# add bundled templates
nodebuilder node add summarizer
nodebuilder node add translator

# compose workflows dynamically
nodebuilder workflow compose my_workflow summarizer translator
nodebuilder workflow suggest  # see suggestions

# list what's in your project
nodebuilder list

# export tools for AI agents
nodebuilder mcp  # show available tools
nodebuilder export-mcp  # export to JSON
nodebuilder agent-prompt  # generate agent prompt
```

## Philosophy
- **No vendor lock-in**: Copies full source into your project
- **Framework-ready**: Nodes have metadata, manifests, and can be orchestrated by AI agents
- **Composable**: Build workflows dynamically from available nodes
- **AI-friendly**: Export MCP tools for agent consumption
- **Extensible**: Fetch nodes from any GitHub repository

## Commands

### Nodes
- `nodebuilder node add <name>` - Add bundled template
- `nodebuilder node fetch <repo> <node>` - Fetch from GitHub
- `nodebuilder node fetch <url> <node> --branch <branch>` - Fetch from specific branch

### Workflows  
- `nodebuilder workflow add <name>` - Add bundled template
- `nodebuilder workflow compose <name> <nodes...>` - Compose from available nodes
- `nodebuilder workflow suggest` - Get workflow suggestions

### Discovery & AI Integration
- `nodebuilder list` - List available nodes and workflows
- `nodebuilder mcp` - Show MCP tool schemas
- `nodebuilder export-mcp` - Export tools to JSON
- `nodebuilder agent-prompt` - Generate agent prompt