import os
import re
import tempfile

md = "# T\nintro\n\n## Visits\nVisits are free, Monday to Saturday.\n\n## Pets\nDogs are banned near the pool.\n\n## Fees\nOne month of rent.\n"
check("sections splits on ## headings", lambda: fn("sections")(md) == [("Visits", "Visits are free, Monday to Saturday."), ("Pets", "Dogs are banned near the pool."), ("Fees", "One month of rent.")])

path = os.path.join(tempfile.mkdtemp(), "handbook.md")
open(path, "w", encoding="utf-8").write(md)
search = fn("search_handbook")


def with_handbook(f):
    g = search.__globals__
    real = g["HANDBOOK"]
    g["HANDBOOK"] = path
    try:
        return f()
    finally:
        g["HANDBOOK"] = real


check("search_handbook finds the best section first", lambda: with_handbook(lambda: search("are dogs allowed near the pool", k=2))[0]["heading"] == "Pets")
check("search_handbook returns heading and text", lambda: with_handbook(lambda: search("pool", k=1)) == [{"heading": "Pets", "text": "Dogs are banned near the pool."}])
check("sections without any query word are dropped", lambda: with_handbook(lambda: search("pool", k=3)) == [{"heading": "Pets", "text": "Dogs are banned near the pool."}])
check("search_handbook respects k", lambda: len(with_handbook(lambda: search("are of the rent month visits pool", k=2))) == 2)
check("the real handbook path exists", lambda: os.path.exists(str(var("HANDBOOK"))), "HANDBOOK points to ../day15/handbook.md: do Week 3 Day 1 first.")
check("deposit: 2 months, +0.5 with a pet", lambda: fn("deposit")(900) == 1800 and fn("deposit")(900, True) == 2250)
check("list_sections returns the headings, one per line", lambda: with_handbook(lambda: fn("list_sections")()).strip().splitlines() == ["Visits", "Pets", "Fees"],
      "Read HANDBOOK inside the function, like search_handbook.")
check("tools and resource are registered with the decorators", lambda: re.search(r"@mcp\.tool\(\)\s*\ndef search_handbook", src) and re.search(r"@mcp\.tool\(\)\s*\ndef deposit", src)
      and re.search(r'@mcp\.resource\("handbook://sections"\)\s*\ndef list_sections', src))
check("client_config", lambda: fn("client_config")("/py", "/srv/mcp_server.py") == {"mcpServers": {"dar-yasmine": {"command": "/py", "args": ["/srv/mcp_server.py"]}}})
