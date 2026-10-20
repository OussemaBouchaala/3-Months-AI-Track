# Part B: aliasing with id()

# 1. Create a list, assign it to a second name, mutate through the second name.
#    Print both names and their id().
a=[1]
b=a
b.append(2)
print(a,b,id(a)==id(b))

# 2. Same with .copy(): show the ids differ.
a=[1]
b=a.copy()
b.append(2)
print(a,b,id(a)==id(b))

# 3. With b as an alias of a, compare:
#      b += [5]      vs      b = b + [5]
#    Predict what happens to a in each case BEFORE running.
b=a
b+=[5]
print(a) 
b=a
b = b + [5]
print(a)