import io, zipfile
dt = fn("detect_type")
check("detect_type trusts the bytes first", lambda: dt("contrat.docx", b"%PDF-1.7") == "pdf" and dt("x.bin", b"%PDF-1.4") == "pdf")
check("detect_type: docx, html, text, unknown", lambda: dt("a.docx", b"PK\x03\x04\x14\x00") == "docx" and dt("page.htm", b"<!doctype") == "html" and dt("noext", b"  <html>") == "html" and dt("n.md", b"# Fees") == "text" and dt("a.xlsx", b"PK\x03\x04") == "unknown")
ht = fn("html_to_text")
page = "<html><head><style>p{color:red}</style><script>alert(1)</script></head><body><h1>Frais</h1><p>Loyer &amp; charges</p><div>2&nbsp;mois</div></body></html>"
check("html_to_text drops script/style and decodes entities", lambda: "alert" not in ht(page) and "color" not in ht(page) and "Loyer & charges" in ht(page))
check("html_to_text puts block tags on separate lines", lambda: [l.strip() for l in ht(page).splitlines() if l.strip()][:2] == ["Frais", "Loyer & charges"])
def _docx(paras):
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join("<w:p>" + "".join(f"<w:r><w:t>{t}</w:t></w:r>" for t in runs) + "</w:p>" for runs in paras)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", xml.encode("utf-8"))
    return buf.getvalue()
dx = fn("docx_to_text")
check("docx_to_text: one line per paragraph, runs joined", lambda: dx(_docx([["Frais ", "d'agence"], ["الضمان: ", "شهرين"]])).splitlines() == ["Frais d'agence", "الضمان: شهرين"])
ct = fn("clean_text")
check("clean_text removes RLM/zero-width marks and collapses spaces", lambda: ct("‏مرحبا ​  بكم\t!") == "مرحبا بكم !")
check("clean_text: NFKC turns presentation forms into letters", lambda: ct("ﻻ") == "لا")
check("clean_text: at most one empty line, no trailing spaces", lambda: ct("  a  \n\n\n\n  b \n") == "a\n\nb")
