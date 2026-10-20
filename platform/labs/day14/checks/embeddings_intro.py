import numpy as np

cos = fn("cosine")
check("cosine of a vector with itself is 1", lambda: approx(cos(np.array([1.0, 2, 3]), np.array([1.0, 2, 3])), 1.0))
check("orthogonal vectors give 0", lambda: approx(cos(np.array([1.0, 0]), np.array([0.0, 1])), 0.0))
check("opposite vectors give -1", lambda: approx(cos(np.array([1.0, 1]), np.array([-1.0, -1])), -1.0))
check("length doesn't matter, only direction", lambda: approx(cos(np.array([1.0, 2]), np.array([10.0, 20])), 1.0),
      "Divide by both norms.")
import re
check("cosine doesn't use sklearn", re.search(r"^\s*(import|from)\s+sklearn", src, re.M) is None)
ranked = lambda: fn("rank")(var("QUERY"), var("DOCS"))
check("rank returns every doc name", lambda: sorted(ranked()) == sorted(var("DOCS")))
check("rank puts the most similar first", lambda: ranked()[0] == "rent law" and ranked()[-1] == "football results",
      "sorted(docs, key=lambda name: cosine(query, docs[name]), reverse=True)")
check("You chose the Arabic corpus", lambda: filled(var("CORPUS_NAME"), 3) and filled(var("CORPUS_PATH"), 3))
