# Part B: aliasing and id()
# Replace each `...`, write your prediction in the yellow box, Run, then Check.

# 1. Alias: point b at the SAME list as a (no copy), then mutate through b.
a = [1, 2, 3]
b = ...  # TODO
b.append(4)
print("a:", a, id(a))
print("b:", b, id(b))

# 2. Copy: c must be a NEW list with the same values as a.
c = ...  # TODO
print("c is a?", c is a, "| ids:", id(a), id(c))

# 3. += versus + on an alias. Predict x and y BEFORE you run.
x = [1, 2]
x_alias = x
x_alias += [5]

y = [1, 2]
y_alias = y
y_alias = y_alias + [5]

print("x:", x, "| y:", y)

# 4. One sentence each, in your own words:
WHY_X_CHANGED = ""
WHY_Y_DID_NOT = ""
