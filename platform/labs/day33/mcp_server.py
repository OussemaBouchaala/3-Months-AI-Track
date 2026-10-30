"""An MCP server: your tools, usable by any MCP client.

MCP (Model Context Protocol) is a standard plug for AI tools. Write the server once, and
Claude Desktop, Claude Code, Cursor and others can all use your tools, with no new
glue code for each one.

1. `sections`: split the handbook into `## ` sections.
2. `search_handbook` (a **tool**): the sections that best match a question.
3. `deposit` (a **tool**): the deposit rule from day 29.
4. `list_sections` (a **resource**): read-only data a client can browse.
5. `client_config`: the JSON a client needs to start this server.

Pressing **Run** in Bench shows a demo. An MCP client starts this same file and talks
to it over stdin/stdout. Install the SDK once with `pip install "mcp[cli]"`.
"""
import json
import os
import re
import sys
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
        """A stand-in with the same decorators, used only when the `mcp` package is missing."""

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
    """Split a Markdown document into `(heading, body)` pairs, one per `## ` section.

    `re.split(r"^## ", markdown, flags=re.M)` cuts the text at every line that
    starts with `## ` (`re.M` makes `^` match at each line start). The first
    piece is whatever comes before the first section, so `[1:]` drops it. Then
    `partition("\\n")` separates the heading line from the rest.

    Example:
        >>> md = "# Handbook\\nintro\\n\\n## Visits\\nFree, Monday to Saturday.\\n\\n## Pets\\nNo dogs near the pool.\\n"
        >>> sections(md)
        [('Visits', 'Free, Monday to Saturday.'), ('Pets', 'No dogs near the pool.')]
    """
    out = []
    for part in re.split(r"^## ", markdown, flags=re.M)[1:]:
        head, _, body = part.partition("\n")
        out.append((head.strip(), body.strip()))
    return out


@mcp.tool()
def search_handbook(query: str, k: int = 3) -> list[dict]:
    """Search the agency handbook. Returns up to k sections as {"heading": ..., "text": ...}.

    A simple keyword search: each section scores the number of **distinct**
    query words it contains (`&` is the intersection of two sets). Sections
    with no match are dropped, the rest are sorted best first, and `k` are kept.

    `@mcp.tool()` publishes the function to MCP clients. The type hints and
    this docstring become the tool's description, so they are written for the model.

    Example (on your handbook from day 15):
        >>> [s["heading"] for s in search_handbook("can I bring my dog", k=2)]  # doctest: +SKIP
        ['Pets', 'Visits']
    """
    words = set(re.findall(r"\w+", query.lower()))
    scored = []
    for head, body in sections(Path(HANDBOOK).read_text(encoding="utf-8")):
        score = len(words & set(re.findall(r"\w+", (head + " " + body).lower())))
        if score:
            scored.append((score, {"heading": head, "text": body}))
    return [d for _, d in sorted(scored, key=lambda t: -t[0])][:k]


@mcp.tool()
def deposit(monthly_rent: float, has_pet: bool = False) -> float:
    """Security deposit in TND for a yearly rental: 2 months of rent, plus half a month with a pet.

    Example:
        >>> deposit(900), deposit(900, has_pet=True)
        (1800, 2250.0)
    """
    return monthly_rent * (2.5 if has_pet else 2)


@mcp.resource("handbook://sections")
def list_sections() -> str:
    """The handbook's section headings, one per line.

    A **resource** is read-only data a client can show or attach to the
    conversation, unlike a tool, which the model calls to do something.

    Example:
        >>> print(list_sections())  # doctest: +SKIP
        Visits
        Pets
        Fees
    """
    return "\n".join(h for h, _ in sections(Path(HANDBOOK).read_text(encoding="utf-8")))


def client_config(python_path, script_path):
    """The JSON block an MCP client needs to start this server.

    The client runs `command` with `args` (your Python and this file), then
    talks to the process over stdin/stdout (the "stdio" transport). Paste this
    into the client's settings, for example `claude_desktop_config.json`.

    Example:
        >>> print(json.dumps(client_config("C:/venv/python.exe", "C:/ml-bench/work/day33/mcp_server.py"), indent=1))
        {
         "mcpServers": {
          "dar-yasmine": {
           "command": "C:/venv/python.exe",
           "args": [
            "C:/ml-bench/work/day33/mcp_server.py"
           ]
          }
         }
        }
    """
    return {"mcpServers": {"dar-yasmine": {"command": python_path, "args": [script_path]}}}


if __name__ == "__main__":
    if "--config" in sys.argv:          # python mcp_server.py --config  -> paste into the client's config
        print(json.dumps(client_config(sys.executable, str(Path(__file__).resolve())), indent=2))
    elif os.environ.get("BENCH_RUN"):   # Run in Bench: a demo instead of waiting for a client
        print("Tool search_handbook('dogs near the pool'):")
        for hit in search_handbook("dogs near the pool", k=2):
            print(f"  - {hit['heading']}: {hit['text'][:70]}")
        print("Tool deposit(1200, has_pet=True):", deposit(1200, True))
        print("Resource handbook://sections:", list_sections().replace("\n", " | "))
        print("\nConfig for an MCP client:")
        print(json.dumps(client_config(sys.executable, str(Path(__file__).resolve())), indent=2))
    else:
        mcp.run()                       # stdio: the client starts this process and talks over stdin/stdout
