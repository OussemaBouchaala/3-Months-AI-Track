# Write the demo script
**Topic:** a 3-5 minute story: hook, live use on real questions, an honest failure, the numbers, how it runs.

## Real example
Checking a script's timing before recording (a different demo, the same arithmetic):

```python
scenes = [("Hook", 20), ("Upload a receipt", 45), ("Auto-filled expense", 40), ("A blurry receipt fails", 30),
          ("Accuracy table", 35), ("How it's deployed", 30), ("Close", 15)]
total = sum(s for _, s in scenes)
print(f"{total // 60}:{total % 60:02d}", "OK" if 180 <= total <= 300 else "too long or too short")
print("longest:", max(scenes, key=lambda s: s[1]))
```

Showing a failure on purpose ("a blurry receipt fails, and it says so") builds more trust than a perfect run.

## Your mission
Write the script you'll record on Saturday.

## Steps
1. Scene 1: the problem with a number, in 20-30 seconds. Your name can come at the end.
2. Live scenes with real questions: one in Arabic or Derja, a follow-up, a booking with confirmation, an "I don't know".
3. One scene with the results table, one with `docker compose up`.
4. Each scene: what you say, and a `Screen:` line. Read it aloud with a timer.

## Done when
**Check** passes and reading it aloud takes 3 to 5 minutes.
