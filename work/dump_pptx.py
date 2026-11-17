# -*- coding: utf-8 -*-
"""Dump slide text from .pptx files into jsonl for inventory."""
import json, os, sys, re
from pptx import Presentation
from pptx.util import Emu

SRC = r"D:\WILL\ECON102"
OUT = r"D:\WILL\ECON102\work"

def shape_text(sh):
    out = []
    if sh.shape_type == 6:  # group
        for s in sh.shapes:
            out.extend(shape_text(s))
        return out
    if sh.has_text_frame:
        t = sh.text_frame.text
        if t and t.strip():
            out.append(t.strip())
    if getattr(sh, "has_table", False) and sh.has_table:
        rows = []
        for r in sh.table.rows:
            rows.append(" | ".join(c.text.strip() for c in r.cells))
        out.append("[TABLE]\n" + "\n".join(rows))
    return out

def dump(path):
    prs = Presentation(path)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        texts = []
        pics = 0
        for sh in slide.shapes:
            texts.extend(shape_text(sh))
            if sh.shape_type == 13:
                pics += 1
        notes = ""
        try:
            if slide.has_notes_slide:
                notes = slide.notes_slide.notes_text_frame.text.strip()
        except Exception:
            pass
        slides.append({"n": i, "text": "\n---\n".join(texts), "pics": pics, "notes": notes})
    return {"file": os.path.basename(path), "count": len(slides),
            "size": [prs.slide_width, prs.slide_height], "slides": slides}

if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = os.path.join(SRC, f)
        try:
            d = dump(p)
        except Exception as e:
            print("FAIL", f, e)
            continue
        out = os.path.join(OUT, os.path.splitext(f)[0] + ".json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        print(f"{f}\t{d['count']} slides\t{d['size']}\t-> {os.path.basename(out)}")
