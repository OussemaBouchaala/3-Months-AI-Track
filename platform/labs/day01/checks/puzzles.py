explain = var("EXPLAIN")
lines = [l for l in out.splitlines() if l.strip()]
check("All 4 puzzles still print (don't edit the puzzles)", lambda: len(lines) == 4 and lines[0] == "[[1, 0, 0], [1, 0, 0], [1, 0, 0]]")
for i, hint in [(1, "How many distinct inner lists does grid hold? Compare id(grid[0]) and id(grid[1])."),
                (2, "Does `acc = acc + [n]` change the default list, or make a new one?"),
                (3, "What exactly is immutable in a tuple: the slots, or the objects inside them?"),
                (4, "Where does `layers` live: on each instance, or on the class?")]:
    check(f"Puzzle {i} explained", lambda i=i: filled(explain.get(i), 10), hint)
