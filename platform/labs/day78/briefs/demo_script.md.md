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

## How to read this example
An example 3-5 minute demo script. Notice how it's built:

1. **Scene 1**: the problem with a number, in 20-30 seconds.
2. **Live scenes** on real questions: Arabic or Derja, a follow-up, a booking with confirmation, an "I don't know".
3. **The numbers** (results table) and **how it runs** (`docker compose up`).
4. Every scene has what you **say** and a `Screen:` line for what is shown. Read it aloud with a timer: 3 to 5 minutes.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
