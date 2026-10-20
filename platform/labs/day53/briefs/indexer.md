# Incremental indexing
**Topic:** hash every file, compare with the last run, and only re-index what changed.

## Real example
A photo backup that only uploads new or edited photos (different files, same manifest trick):

```python
old = {"img1.jpg": "aa", "img2.jpg": "bb", "img3.jpg": "cc"}
new = {"img1.jpg": "aa", "img2.jpg": "b2", "img4.jpg": "dd"}
print("upload:", sorted(set(new) - set(old)))
print("re-upload:", [n for n in new if n in old and new[n] != old[n]])
print("remove from cloud:", sorted(set(old) - set(new)))
```

Hashing the content (not the modified date) means a copied or touched-but-unchanged file costs nothing.

## Your mission
Make `python indexer.py <docs>` cheap to re-run every day.

## Steps
1. `file_hash`, `build_manifest`.
2. `plan`: add, update, delete, unchanged.
3. `batched` and `apply_plan` (delete old chunks before re-indexing an updated file).
4. **Run** twice: the second run should print 0 indexed. Edit one file, run again: 1 updated.

## Done when
**Check** passes and a second run on the same folder indexes nothing.
