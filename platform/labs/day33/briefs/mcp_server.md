# Your first MCP server
**Topic:** MCP = one standard plug between tools and AI apps: write the server once, every client can use it.

## Real example
A library exposes its catalogue as MCP tools. A server is just functions with type hints and docstrings; the SDK turns them into tool schemas. This sketch fakes the decorator to show what the SDK does with your function:

```python
import inspect, json

registry = {}
def tool(f):                         # what @mcp.tool() does, roughly
    sig = inspect.signature(f)
    registry[f.__name__] = {"description": f.__doc__.strip(),
                            "params": {n: p.annotation.__name__ for n, p in sig.parameters.items()}}
    return f

@tool
def find_book(title: str, max_results: int = 5) -> list:
    """Find books whose title contains the text."""
    return [b for b in ["Le Petit Prince", "Petit Pays"] if title.lower() in b.lower()][:max_results]

print(json.dumps(registry, indent=1))
print(find_book("petit"))
```

In the real SDK the class is `MCPServer` (version 1 called it `FastMCP`); the starter imports whichever you have. Type hints become the schema, the docstring becomes the description. Write both carefully: they're what the model reads.

## Your mission
Expose the handbook search and the deposit calculator as an MCP server.

## Steps
1. `sections`, then `search_handbook` (word-overlap score, drop zero scores, top k).
2. `deposit` and the `list_sections` resource.
3. `client_config`: the `mcpServers` block.
4. `pip install "mcp[cli]"`, then test with the inspector: `mcp dev mcp_server.py` (opens a web UI where you call the tools).
5. Optional: `python mcp_server.py --config`, paste into Claude Desktop's config, restart it, and ask it about deposits.

## Done when
**Check** passes and the MCP inspector lists your 2 tools and 1 resource.
