# -*- coding: utf-8 -*-
import pymupdf, os, re
ROOT = r"D:\WILL\ECON102"
for f, a, b in [("Price Theory and Applications 9th Edition.pdf", 8, 14),
                ("Intermediate Microeconomics with Calculus by Varian, Hal.pdf", 6, 14)]:
    d = pymupdf.open(os.path.join(ROOT, f))
    print("#####", f)
    for i in range(a, b):
        t = d[i].get_text("text")
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        for j, l in enumerate(lines):
            if re.match(r"^(CHAPTER|Chapter|\d{1,2}$)", l) and j + 1 < len(lines):
                nxt = lines[j + 1]
                if nxt and not re.match(r"^\d+$", nxt):
                    print(f"{l} {nxt}"[:90])
