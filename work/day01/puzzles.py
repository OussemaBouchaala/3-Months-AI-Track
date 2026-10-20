# Part D: predict, then run. Write your 4 predictions in the yellow box first.

# Puzzle 1
grid = [[0] * 3] * 3
grid[0][0] = 1
print(grid)

# Puzzle 2
def f(n, acc=[]):
    acc = acc + [n]
    return acc
print(f(1), f(2))

# Puzzle 3
t = ([1, 2], 3)
t[0].append(4)
print(t)

# Puzzle 4
class Model:
    layers = []
    def add(self, layer):
        self.layers.append(layer)

m1, m2 = Model(), Model()
m1.add("conv")
print(m2.layers)
