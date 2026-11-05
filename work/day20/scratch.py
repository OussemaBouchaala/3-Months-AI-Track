import math
N = 14                       # sections in the handbook
for word, df in [("cin", 1), ("loyer", 3), ("the", 14)]:
    idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
    print(f"{word:<6} in {df:>2} docs -> idf {idf:.2f}")
