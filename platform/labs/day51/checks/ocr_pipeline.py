no = fn("needs_ocr")
check("needs_ocr: empty or near-empty text layer", lambda: no("") and no(None) and no("12 / 3 \n --") and not no("Le locataire paie un mois de loyer hors charges à la signature."))
check("needs_ocr counts Arabic letters too", lambda: not no("يدفع المكتري ضمانًا يساوي شهرين من معلوم الكراء عند إمضاء العقد وبعد ذلك"))
tq = fn("text_quality")
check("text_quality: clean text near 1, garbage low, empty 0", lambda: tq("Loyer: 900 TND (charges).") == 1.0 and tq("|~}^ ¦ ~~|") < 0.2 and tq("") == 0.0)
dh = fn("dehyphenate")
check("dehyphenate joins split words, keeps real dashes", lambda: dh("la loca-\ntion annuelle") == "la location annuelle" and dh("2024-\n2025") == "2024-\n2025")
rr = fn("remove_repeated_lines")
pages = ["Dar Yasmine - Contrat\nArticle 1\nLe loyer\n- 1 -", "Dar Yasmine - Contrat\nArticle 2\nLa caution\n- 2 -", "Dar Yasmine - Contrat\nArticle 3\nPage 3/3"]
check("remove_repeated_lines drops the header on every page", lambda: all("Dar Yasmine" not in p for p in rr(pages)) and "Article 2" in rr(pages)[1])
check("remove_repeated_lines drops page numbers", lambda: all("- " + str(i) not in p and "Page 3" not in p for i, p in enumerate(rr(pages), 1)))
check("a line on only one page stays", lambda: rr(["A\nB", "A\nC", "D"], 0.6) == ["B", "C", "D"])
pp = fn("process_pages")
calls = []
def fake_ocr(i):
    calls.append(i)
    return f"Article {i}: le loca-\ntaire paie la caution de {i + 1} mois de loyer, remboursée sous trente jours."
res = lambda: pp(["Le locataire paie un mois de loyer hors charges à la signature du bail.", "", "x"], fake_ocr)
check("process_pages calls OCR only on pages without text", lambda: (calls.clear(), [r["method"] for r in res()])[1] == ["text", "ocr", "ocr"] and calls == [1, 2])
check("process_pages: 1-based page numbers, dehyphenated text, quality", lambda: res()[1]["page"] == 2 and "locataire" in res()[1]["text"] and 0.9 < res()[0]["quality"] <= 1)
