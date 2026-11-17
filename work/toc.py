# -*- coding: utf-8 -*-
import pymupdf, os
ROOT = r"D:\WILL\ECON102"
jobs = [("Price Theory and Applications 9th Edition.pdf", 5, 13),
        ("Intermediate Microeconomics with Calculus by Varian, Hal.pdf", 6, 15)]
for f, a, b in jobs:
    d = pymupdf.open(os.path.join(ROOT, f))
    print("#####", f, d.page_count)
    for i in range(a, b):
        t = d[i].get_text("text")
        if len(t.strip()) > 50:
            print("--- page", i + 1)
            print(t[:1600])
