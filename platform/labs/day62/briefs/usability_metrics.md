# Measure usability
**Topic:** task success, time on task, and the System Usability Scale, computed from a real test session.

## Real example
Scoring one SUS questionnaire for a banking app (different product, the standard formula):

```python
answers = [4, 2, 4, 2, 3, 3, 4, 2, 3, 2]          # 1 = strongly disagree ... 5 = strongly agree
score = sum((a - 1) if i % 2 == 0 else (5 - a) for i, a in enumerate(answers)) * 2.5
print(score, "-> above the average of 68" if score >= 68 else "-> below average")
```

Questions alternate positive and negative so people can't tick "5" all the way down. 68 is the average across thousands of studies.

## Your mission
Run a usability test with 3 to 5 real users and compute the numbers.

## Steps
1. `sus_score`, `sus_grade`.
2. `task_table` and `to_markdown`.
3. Prepare 3 tasks from your scope ("ask about the deposit in Derja", "book a visit", "find which contract a clause comes from").
4. Watch each user do them without helping. Note time, success, errors. Then the 10 SUS questions.
5. **Run** with the real data.

## Done when
**Check** passes and you have a task table and a mean SUS score from real users.
