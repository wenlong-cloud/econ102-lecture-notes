# -*- coding: utf-8 -*-
"""Sanity-check the built docs/ folder: image refs resolve, no ../ escapes."""
import glob, os, re

DOCS = r"D:\WILL\ECON102\docs"
html = glob.glob(os.path.join(DOCS, "*.html"))
text = "".join(open(p, encoding="utf-8").read() for p in html)

refs = set(re.findall(r'src="(assets/[^"]+)"', text))
missing = [r for r in refs if not os.path.exists(os.path.join(DOCS, r))]
print("html files:", len(html))
print("image refs:", len(refs), "missing:", len(missing), missing[:3])

bad = [p for p in html if "../" in open(p, encoding="utf-8").read()]
print("files still using ../ :", [os.path.basename(p) for p in bad])

for name in ("style.css", "app.js", "glossary-data.js", ".nojekyll"):
    print(f"{name}: {'ok' if os.path.exists(os.path.join(DOCS, name)) else 'MISSING'}")

first = re.search(r'src="(assets/[^"]+)"', text)
print("sample ref:", first.group(1) if first else "-")
