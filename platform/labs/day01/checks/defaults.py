add_buggy, add_fixed = fn("add_buggy"), fn("add_fixed")
check("add_buggy returns the list with x appended",
      lambda: add_buggy(7)[-1] == 7, "Append x to items, then `return items`.")
check("add_buggy reuses ONE default list across calls (the bug)",
      lambda: isinstance(add_buggy(1), list) and add_buggy(1) is add_buggy(2), "Keep `items=[]` in the signature and return that same list.")
check("add_fixed gives a fresh list on every call",
      lambda: add_fixed(1) == [1] and add_fixed(2) == [2],
      "Default to None, then create the list inside: `if items is None: items = []`.")
check("add_fixed still appends to a list you pass in",
      lambda: add_fixed(3, [1, 2]) == [1, 2, 3])

log_buggy, log = fn("log_request_buggy"), fn("log_request")
check("log_request_buggy leaks history between requests",
      lambda: isinstance(log_buggy("u1"), list) and log_buggy("u1") is log_buggy("u2"), "Use `history=[]` and return history.")
check("log_request starts every request with a clean history",
      lambda: log("u1") == ["u1"] and log("u2") == ["u2"],
      "Same fix as add_fixed: `history=None`, then create the list inside.")
