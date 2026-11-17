# -*- coding: utf-8 -*-
"""Render PDF pages to PNG and dump text, in the same schema as the pptx dumps."""
import os, sys, json
import pymupdf

ROOT = r"D:\WILL\ECON102"
ASSETS = os.path.join(ROOT, "assets")
WORK = os.path.join(ROOT, "work")

def render(pdf, outdir, tag, zoom=2.0, dpi=None):
    doc = pymupdf.open(pdf)
    d = os.path.join(ASSETS, outdir)
    os.makedirs(d, exist_ok=True)
    slides = []
    mat = pymupdf.Matrix(zoom, zoom)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(os.path.join(d, "slide-%03d.png" % i))
        slides.append({"n": i, "text": page.get_text("text").strip(), "pics": 0, "notes": ""})
    data = {"file": os.path.basename(pdf), "count": len(slides),
            "size": [doc[0].rect.width, doc[0].rect.height], "slides": slides}
    with open(os.path.join(WORK, tag + ".json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print(f"{os.path.basename(pdf)} -> {outdir}: {len(slides)} pages, {doc[0].rect.width:.0f}x{doc[0].rect.height:.0f}")
    doc.close()

if __name__ == "__main__":
    jobs = [
        ("Lecture Monopoly updated 20240409.pdf", "lec06", "lec06"),
        ("Tax and Tax incidentce updated 20250329.pdf", "lec09t", "lec09t"),
    ]
    for pdf, outdir, tag in jobs:
        render(os.path.join(ROOT, pdf), outdir, tag)
    # page counts only
    for f in sorted(os.listdir(ROOT)):
        if f.lower().endswith(".pdf"):
            try:
                doc = pymupdf.open(os.path.join(ROOT, f))
                print(f"  pages {doc.page_count:4d}  {f}")
                doc.close()
            except Exception as e:
                print("  ERR", f, e)
