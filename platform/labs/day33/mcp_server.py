# An MCP server: your tools, usable by ANY MCP client (Claude Desktop, Claude Code, Cursor...) without new glue code.
# Install the SDK once: pip install "mcp[cli]"     Run it from a client (see the brief), not with Run.
# Check calls your functions directly, so it works without the mcp package.
import json
import re
from pathlib import Path

try:
    from mcp.server.mcpserver import MCPServer                 # mcp 2.x
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer    # mcp 1.x called it FastMCP
    except ImportError:      # lets Check and Run work before you install the SDK
        MCPServer = None

if MCPServer is None:
    class MCPServer:
        def __init__(self, name):
            self.name, self.tools, self.resources = name, {}, {}

        def tool(self):
            def deco(f):
                self.tools[f.__name__] = f
                return f
            return deco

        def resource(self, uri):
            def deco(f):
                self.resources[uri] = f
                return f
            return deco

        def run(self):
            raise SystemExit('Install the SDK first: pip install "mcp[cli]"')

HANDBOOK = Path(__file__).resolve().parent.parent / "day15" / "handbook.md"
mcp = MCPServer("dar-yasmine")


def sections(markdown):
    """[(heading, body), ...] for every "## " section (same as day15's split_by_heading)."""
    # TODO
    ...


@mcp.tool()
def search_handbook(query: str, k: int = 3) -> list[dict]:
    """Search the agency handbook. Returns up to k sections as {"heading": ..., "text": ...},
    ranked by how many query words (lowercase, found with re.findall on word characters) appear in heading + body. Sections with 0 matches are dropped."""
    # TODO: read HANDBOOK, score each section, sort by score (stable), keep k
    ...


@mcp.tool()
def deposit(monthly_rent: float, has_pet: bool = False) -> float:
    """Security deposit in TND for a yearly rental: 2 months of rent, plus half a month with a pet."""
    # TODO
    ...


@mcp.resource("handbook://sections")
def list_sections() -> str:
    """The handbook's section headings, one per line."""
    # TODO
    ...


def client_config(python_path, script_path):
    """The JSON block an MCP client needs to start this server over stdio:
    {"mcpServers": {"dar-yasmine": {"command": python_path, "args": [script_path]}}}"""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    if "--config" in sys.argv:       # python mcp_server.py --config  -> paste into the client's config
        print(json.dumps(client_config(sys.executable, str(Path(__file__).resolve())), indent=2))
    else:
        mcp.run()                    # stdio: the client starts this process and talks over stdin/stdout
