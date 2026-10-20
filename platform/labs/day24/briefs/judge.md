# A model grades the answers
**Topic:** correct (matches the expected answer) and faithful (supported by the sources) are two different grades.

## Real example
A teacher grades short history answers. Some cases need no judge at all; the rest go to a (here faked) grader, whose messy reply is parsed defensively:

```python
import json, re

def parse(reply):
    m = re.search(r"\{.*\}", reply, re.S)
    try:
        d = json.loads(m.group())
        return {"correct": int(bool(int(d["correct"]))), "reason": str(d.get("reason", ""))}
    except Exception:
        return {"correct": 0, "reason": "unparseable"}

def grade(expected, answer, fake_judge):
    if not answer.strip():
        return {"correct": 0, "reason": "blank"}          # no judge needed
    return parse(fake_judge(expected, answer))

judge = lambda e, a: 'Grade: {"correct": 1, "reason": "same date, different wording"}'
print(grade("1956", "Tunisia became independent in 1956.", judge))
print(grade("1956", "", judge))
print(parse("I think it's correct!"))
```

## Your mission
Grade answers on correctness and faithfulness, using code where code is enough.

## Steps
1. `judge_prompt`: question, expected, answer, sources, and the exact JSON shape.
2. `parse_judgment`: regex the `{...}`, `json.loads`, coerce to 0/1, safe default.
3. `grade`: the two no-model cases first, then the judge.
4. **Run**: the three answers should grade (1,1), (0,0) and (1,1). The English one is correct even though the question is French.

## Done when
**Check** passes and the 3 sample answers get the grades you expect.
