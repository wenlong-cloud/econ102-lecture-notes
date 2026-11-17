# -*- coding: utf-8 -*-
"""Build a flat `docs/` folder that works as a GitHub Pages site root.

docs/
  index.html  lec01.html ...  glossary.html  style.css  app.js  glossary-data.js
  assets/<dir>/slide-NNN.webp      (reused from dist/, no re-encoding)
  .nojekyll

The pages reference images as `assets/<dir>/slide-NNN.webp`, so the folder can be
opened by double-clicking docs/index.html locally AND served by Pages at the
repo's /docs path without any path juggling.
"""
import os, shutil, subprocess, sys, glob

ROOT = r"D:\WILL\ECON102"
DOCS = os.path.join(ROOT, "docs")
SRC_ASSETS = os.path.join(ROOT, "dist", "ECON102-讲义", "assets")
COURSE = os.path.join(ROOT, "course")

if not os.path.isdir(SRC_ASSETS):
    sys.exit(f"missing {SRC_ASSETS} -- run work/pack.py first")

os.makedirs(DOCS, exist_ok=True)
for f in glob.glob(os.path.join(DOCS, "*.html")) + glob.glob(os.path.join(DOCS, "*.js")):
    os.remove(f)

dst_assets = os.path.join(DOCS, "assets")
if os.path.isdir(dst_assets):
    shutil.rmtree(dst_assets)
shutil.copytree(SRC_ASSETS, dst_assets)

subprocess.run([sys.executable, os.path.join(ROOT, "work", "build_site.py"),
                "--out", DOCS,
                "--ext", ".webp",
                "--assets", dst_assets,
                "--img-base", "assets"], check=True,
               env={**os.environ, "PYTHONIOENCODING": "utf-8"})

for f in ("style.css", "app.js"):
    shutil.copy2(os.path.join(COURSE, f), os.path.join(DOCS, f))

open(os.path.join(DOCS, ".nojekyll"), "w").write("")

htmls = glob.glob(os.path.join(DOCS, "*.html"))
imgs = glob.glob(os.path.join(DOCS, "assets", "*", "*.webp"))
size = sum(os.path.getsize(os.path.join(dp, f))
           for dp, _, fs in os.walk(DOCS) for f in fs)
print(f"docs: {len(htmls)} html, {len(imgs)} webp, {size/1e6:.1f} MB")
