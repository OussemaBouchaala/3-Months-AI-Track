def step(tool, args, ok=True):
    return {"type": "tool", "tool": tool, "args": args, "observation": {"ok": ok}}


answer = {"type": "answer", "tool": None, "args": None, "observation": None}
book = {"task": "t", "expect_tool": "book_visit", "expect_args": {"listing_ids": ["L7"], "phone": "22123456"}, "forbid_tools": []}
dep = {"task": "t", "expect_tool": "deposit", "expect_args": {"monthly_rent": 1200, "has_pet": True}, "forbid_tools": ["book_visit"], "expect_in_answer": "3000"}
sunday = {"task": "t", "expect_tool": None, "expect_args": {}, "forbid_tools": ["book_visit"], "expect_in_answer": "no"}
R = lambda steps, ans="done", stopped="answer": {"answer": ans if stopped == "answer" else None, "stopped": stopped, "steps": steps}

check("tools_called lists tool steps in order", lambda: fn("tools_called")(R([step("deposit", {}), {"type": "invalid", "tool": None, "args": None, "observation": None}, step("rental_fee", {}), answer])) == ["deposit", "rental_fee"])
am = fn("args_match")
check("args_match: subset, extra keys ok", lambda: am({"listing_ids": ["L7"], "phone": "22123456", "name": "Amel"}, {"listing_ids": ["L7"], "phone": "22123456"}))
check("args_match: strings ignore case, values must match", lambda: am({"city": "SOUSSE"}, {"city": "sousse"}) and not am({"monthly_rent": 1000}, {"monthly_rent": 1200}) and not am({}, {"a": 1}))
sr = fn("score_run")
check("success: right tool, right args, ok observation", lambda: sr(book, R([step("book_visit", {"listing_ids": ["L7"], "phone": "22123456", "name": "A"}), answer]))["success"] is True)
check("fail: the tool call failed (observation not ok)", lambda: sr(book, R([step("book_visit", {"listing_ids": ["L7"], "phone": "22123456"}, ok=False), answer]))["success"] is False)
check("fail: wrong arguments", lambda: sr(book, R([step("book_visit", {"listing_ids": ["L8"], "phone": "22123456"}), answer]))["success"] is False)
check("fail: a forbidden tool was used", lambda: (lambda s: not s["success"] and s["forbidden_used"])(sr(sunday, R([step("book_visit", {}), answer], "No, closed on Sunday."))))
check("fail: hit max_steps", lambda: sr(book, R([step("book_visit", {"listing_ids": ["L7"], "phone": "22123456"})], stopped="max_steps"))["success"] is False)
check("expect_in_answer ignores case, commas and spaces", lambda: sr(dep, R([step("deposit", {"monthly_rent": 1200, "has_pet": True}), answer], "The deposit is 3,000 TND."))["success"] is True
      and sr(sunday, R([answer], "No: closed on Sundays."))["success"] is True and sr(sunday, R([answer], "Sure, come by!"))["success"] is False)
check("score_run reports steps and stopped", lambda: (lambda s: s["steps"] == 2 and s["stopped"] == "answer")(sr(sunday, R([step("rental_fee", {}), answer], "no"))))
check("summarize", lambda: fn("summarize")([{"success": True, "forbidden_used": False, "steps": 2, "stopped": "answer"}, {"success": False, "forbidden_used": True, "steps": 4, "stopped": "answer"}])
      == {"n": 2, "success_rate": 0.5, "avg_steps": 3, "forbidden_rate": 0.5})
check("10 scenarios, including refusals (forbid_tools) and a prompt injection", lambda: len(var("SCENARIOS")) >= 10 and sum(1 for s in var("SCENARIOS") if s["forbid_tools"]) >= 3
      and any("ignore" in s["task"].lower() for s in var("SCENARIOS")))
