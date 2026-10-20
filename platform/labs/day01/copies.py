# Part C: shallow vs deep copy
import copy

config = {"layers": [64, 32], "lr": 0.01}

# 1. Make a shallow copy and a deep copy of config.
shallow = ...  # TODO
deep = ...     # TODO

# 2. Change the original (predict what each copy will show).
config["layers"].append(16)
config["lr"] = 0.1

# 3. Compare all three.
print("config :", config)
print("shallow:", shallow)
print("deep   :", deep)

# 4. One sentence each, in your own words:
WHY_SHALLOW_LAYERS_CHANGED = ""
WHY_SHALLOW_LR_DID_NOT = ""
