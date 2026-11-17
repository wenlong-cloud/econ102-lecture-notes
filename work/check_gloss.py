import io, os, re, json, glob
C = r"D:\WILL\ECON102\course"
S = r"D:\WILL\ECON102\src"
g = json.load(io.open(os.path.join(S, "glossary.json"), encoding="utf-8"))
print("glossary entries:", len(g) if isinstance(g, list) else len(g.keys()))
print("gloss files:", sorted(os.path.basename(p) for p in glob.glob(os.path.join(S, "gloss_*.json"))))
for p in sorted(glob.glob(os.path.join(C, "lec*.html"))) + [os.path.join(C, "index.html")]:
    s = io.open(p, encoding="utf-8").read()
    print("%-14s term=%d  ask=%s  gjs=%s" % (
        os.path.basename(p), s.count('class="term"'),
        "ask-panel" in s, "glossary-data.js" in s))
