import io, os, re, json, glob
C = r"D:\WILL\ECON102\course"
raw = io.open(os.path.join(C, "glossary-data.js"), encoding="utf-8").read()
m = re.search(r"window\.GLOSSARY\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
data = json.loads(m.group(1))
print("data keys:", len(data))

bad = []
for p in sorted(glob.glob(os.path.join(C, "lec*.html"))):
    s = io.open(p, encoding="utf-8").read()
    ids = re.findall(r'data-t="([^"]+)"', s)
    miss = [i for i in ids if i not in data]
    if miss:
        bad.append((os.path.basename(p), miss[:5]))
    for need in ['id="ask-open"', 'id="ask-panel"', 'id="ask-log"', 'id="ask-text"', 'id="ask-send"',
                 'id="ask-setup"', 'id="ask-key"', 'id="ask-ctx"', 'glossary-data.js']:
        if need not in s:
            bad.append((os.path.basename(p), "missing " + need))
print("problems:", bad if bad else "none")

g = io.open(os.path.join(C, "glossary.html"), encoding="utf-8").read()
print("glossary.html entries:", g.count('class="gentry"'), "chips:", g.count('class="chip"'),
      "has search:", 'id="gsearch"' in g)
idx = io.open(os.path.join(C, "index.html"), encoding="utf-8").read()
print("index ask:", 'id="ask-open"' in idx, "nav glossary:", 'glossary.html' in idx)
