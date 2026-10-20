# Time the rehearsal
**Topic:** estimate speaking time per scene, add the app's waiting time, and compare with real rehearsal laps.

## Real example
A wedding speech planned at 3 minutes (different stage, same trap):

```python
speech = "Thank you all for coming tonight " * 70           # about 420 words
wpm = 130
print(f"{len(speech.split()) / wpm:.1f} minutes at {wpm} words per minute")
print("cut about", len(speech.split()) - 3 * wpm, "words")
```

Writing feels short; saying it out loud at a calm pace is longer. Count words before you rehearse.

## Your mission
Make the demo fit 3-5 minutes before you record it.

## Steps
1. `to_seconds`, `fmt`, `parse_script` (reads your day78 script).
2. `speaking_seconds`, `too_long` with the app's waits.
3. `compare` with rehearsal laps.
4. Rehearse twice with a stopwatch (lap per scene). **Run** and enter the laps. Cut words where you run long.

## Done when
**Check** passes and your second rehearsal lands within 15 seconds of the plan.
