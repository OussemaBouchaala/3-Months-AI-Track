chunks = [{"heading": "Visits", "text": "Visits are free, Monday to Saturday."},
          {"heading": "Augmentation du loyer", "text": "Pas d'augmentation la première année, puis 5% max par an."}]
sources = "\n\n".join(f"[{i}] {c['heading']}\n{c['text']}" for i, c in enumerate(chunks, 1))
prompt = ("Answer ONLY from the sources. Cite every fact like [1]. "
          "If the sources don't contain the answer, reply exactly: I don't know based on the documents.\n\n"
          f"Sources:\n{sources}\n\nQuestion: Can my landlord raise the rent by 8%?")
print(prompt)
