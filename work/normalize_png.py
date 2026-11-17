# -*- coding: utf-8 -*-
"""Normalize PowerPoint-exported PNG names (幻灯片N.PNG / SlideN.PNG) to slide-NNN.png."""
import os, re, sys, glob, shutil

ASSETS = r"D:\WILL\ECON102\assets"

def main():
    for d in sorted(glob.glob(os.path.join(ASSETS, "*"))):
        if not os.path.isdir(d):
            continue
        files = [f for f in os.listdir(d) if f.lower().endswith(".png")]
        pat = re.compile(r"(\d+)")
        moved = 0
        for f in files:
            if re.fullmatch(r"slide-\d{3}\.png", f):
                continue
            m = re.search(r"(\d+)", os.path.splitext(f)[0])
            if not m:
                print("SKIP", f)
                continue
            n = int(m.group(1))
            dst = os.path.join(d, "slide-%03d.png" % n)
            if os.path.abspath(os.path.join(d, f)) == os.path.abspath(dst):
                continue
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(os.path.join(d, f), dst)
            moved += 1
        total = len([f for f in os.listdir(d) if f.lower().endswith(".png")])
        print(f"{os.path.basename(d)}: moved={moved} total={total}")

if __name__ == "__main__":
    main()
