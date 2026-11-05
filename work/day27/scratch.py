import itertools
grid = [f"{r}-k{k}-{'rerank' if rr else 'norerank'}"
        for r, k, rr in itertools.product(["vector", "hybrid"], [3, 5], [False, True])]
print(len(grid), grid[:3])
