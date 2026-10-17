# Part C: shallow vs deep copy

config = {"layers": [64, 32], "lr": 0.01}

# 1. Make a shallow copy and a deep copy of config.
import copy 
s, d = config.copy(), copy.deepcopy(config)


# 2. Then: config["layers"].append(16) and config["lr"] = 0.1
config["layers"].append(16) 
config["lr"] = 0.1

# 3. Print all three. In a comment, explain why the shallow copy changed
#    for "layers" but not for "lr".
print(config,s,d)