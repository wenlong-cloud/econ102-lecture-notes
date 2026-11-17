# -*- coding: utf-8 -*-
"""Build the static study site from src/*.md + work/lec*.json + assets/*.png.

Adds (v2): clickable glossary terms, a standalone glossary page, and the data
file that the AI sidebar/popovers read.
"""
import json, os, re, html, glob

ROOT = r"D:\WILL\ECON102"
SRC = os.path.join(ROOT, "src")
WORK = os.path.join(ROOT, "work")
OUT = os.path.join(ROOT, "course")

# configurable for the portable "light" package (jpg images, separate output)
IMG_EXT = ".png"
ASSETS = os.path.join(ROOT, "assets")
IMG_BASE = "../assets"

def esc(s):
    return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def is_table_row(s):
    return s.strip().startswith("|") and s.strip().endswith("|")

def split_row(s):
    return [c.strip() for c in s.strip().strip("|").split("|")]

def md_to_html(text):
    """Tiny markdown subset: paragraphs, - / 1. lists, > quotes, | tables |, **bold**, *em*, `code`."""
    out = []
    lines = text.split("\n")
    i = 0
    buf = []
    def flush():
        if buf:
            out.append("<p>" + inline(" ".join(buf).strip()) + "</p>")
            buf.clear()
    while i < len(lines):
        s = lines[i].rstrip()
        if not s.strip():
            flush(); i += 1; continue
        m = re.match(r"^(#{2,4})\s+(.*)$", s.strip())
        if m:
            flush()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2).strip())}</h{lvl}>")
            i += 1
            continue
        if is_table_row(s):
            flush()
            rows = []
            while i < len(lines) and is_table_row(lines[i]):
                rows.append(split_row(lines[i])); i += 1
            if len(rows) >= 2 and re.match(r"^:?-{2,}:?$", rows[1][0].replace(" ", "")):
                head, body = rows[0], rows[2:]
            else:
                head, body = None, rows
            h = ['<table class="tbl">']
            if head:
                h.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>")
            h.append("<tbody>")
            for r in body:
                h.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            h.append("</tbody></table>")
            out.append("".join(h))
            continue
        if s.startswith("- "):
            flush()
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append("<li>" + inline(lines[i][2:].strip()) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i]):
                items.append("<li>" + inline(re.sub(r"^\d+\.\s", "", lines[i]).strip()) + "</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if s.startswith("> "):
            flush()
            items = []
            while i < len(lines) and lines[i].startswith("> "):
                items.append(inline(lines[i][2:].strip())); i += 1
            out.append("<blockquote>" + "<br>".join(items) + "</blockquote>")
            continue
        buf.append(s)
        i += 1
    flush()
    return "\n".join(out)

def parse_lecture_md(path):
    """Parse authored notes: '### N' blocks, body follows."""
    if not os.path.exists(path):
        return {}
    blocks = {}
    cur = None
    body = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^###\s+(\d+)\s*$", line.strip())
        if m:
            if cur is not None:
                blocks[cur] = "\n".join(body).strip()
            cur = int(m.group(1))
            body = []
        else:
            if cur is not None:
                body.append(line.rstrip("\n"))
    if cur is not None:
        blocks[cur] = "\n".join(body).strip()
    return blocks

def auto_title(sl, body=""):
    t = " ".join(sl["text"].split())
    if not t:
        b = " ".join(body.split())
        b = re.sub(r"[*`#>|]", "", b).strip()
        for cut in ["。", "：", "（", "，", "；"]:
            if cut in b[:46]:
                b = b.split(cut)[0]
        b = b.strip()
        return (b[:30] or "（图示页）")
    for sep in [" --- "]:
        if sep in t:
            return t.split(sep)[0][:80]
    return t[:80]

# ---------------------------------------------------------------- glossary ---
LEC_ORDER = []

def load_glossary():
    """Merge src/gloss_*.json (draft shards) into one dict, deduped by zh."""
    shards = sorted(glob.glob(os.path.join(SRC, "gloss_*.json")))
    merged, seen_zh, seen_id = [], {}, set()
    for p in shards:
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print("GLOSS SKIP", os.path.basename(p), e)
            continue
        for it in data:
            it.setdefault("detail", "")
            it.setdefault("alias", [])
            it.setdefault("lec", [])
            zh = it["zh"].strip()
            if zh in seen_zh:
                # same term from another shard: union the lectures/aliases,
                # keep whichever explanation is longer
                old = seen_zh[zh]
                lecs = list(old.get("lec") or [])
                for l in (it.get("lec") or []):
                    if l not in lecs:
                        lecs.append(l)
                al = list(old.get("alias") or [])
                for a in (it.get("alias") or []):
                    if a and a not in al and a != zh:
                        al.append(a)
                if len(it.get("short", "")) > len(old.get("short", "")):
                    it["lec"], it["alias"] = lecs, al
                    merged[merged.index(old)] = it
                    seen_zh[zh] = it
                else:
                    old["lec"], old["alias"] = lecs, al
                continue
            gid = it.get("id") or re.sub(r"[^a-z0-9]+", "-", it["en"].lower()).strip("-")
            base, k = gid, 2
            while gid in seen_id:
                gid = f"{base}-{k}"; k += 1
            it["id"] = gid
            seen_id.add(gid)
            merged.append(it)
            seen_zh[zh] = it
    def key(it):
        l0 = it["lec"][0] if it["lec"] else "zzz"
        return (LEC_ORDER.index(l0) if l0 in LEC_ORDER else 99, it["zh"])
    merged.sort(key=key)
    json.dump(merged, open(os.path.join(SRC, "glossary.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return merged

def term_index(gloss):
    """(regex, id-by-matched-text) for auto-linking. Longest terms first."""
    pairs = []
    for it in gloss:
        names = [it["zh"]] + [a for a in it.get("alias") or [] if a]
        for nm in names:
            nm = nm.strip()
            if len(nm) >= 2:
                pairs.append((nm, it["id"]))
    pairs.sort(key=lambda x: -len(x[0]))
    table = {}
    for nm, gid in pairs:
        table.setdefault(nm, gid)
    pat = re.compile("|".join(re.escape(n) for n in
                              sorted(table, key=lambda x: -len(x))))
    return pat, table

MAX_LINKS_PER_PAGE = 45
MAX_LINKS_PER_SLIDE = 3

def linkify(html_text, pat, table, used, budget):
    """Wrap the first occurrence of glossary terms in plain text nodes only."""
    out = []
    added = 0
    for seg in re.split(r"(<[^>]+>)", html_text):
        if not seg:
            continue
        if seg.startswith("<"):
            out.append(seg)
            continue
        if budget[0] <= 0 or added >= MAX_LINKS_PER_SLIDE:
            out.append(seg); continue
        res, last = [], 0
        for m in pat.finditer(seg):
            name = m.group(0)
            gid = table.get(name)
            if not gid or gid in used:
                continue
            used.add(gid)
            budget[0] -= 1
            added += 1
            res.append(seg[last:m.start()])
            res.append(f'<a class="term" href="glossary.html#t-{gid}" data-t="{gid}">{name}</a>')
            last = m.end()
            if budget[0] <= 0 or added >= MAX_LINKS_PER_SLIDE:
                break
        res.append(seg[last:])
        out.append("".join(res))
    return "".join(out)

def slide_html(lec, sl, body, pat=None, table=None):
    n = sl["n"]
    img = f"{IMG_BASE}/{lec['dir']}/slide-{n:03d}{IMG_EXT}"
    title = auto_title(sl, body)
    raw = sl["text"].strip()
    parts = []
    parts.append(f'<section class="slide" id="s{n}" data-n="{n}">')
    parts.append(f'  <div class="slide-head"><span class="pno">P{n}</span>'
                 f'<span class="ptitle">{esc(title)}</span></div>')
    if os.path.exists(os.path.join(ASSETS, lec["dir"], f"slide-{n:03d}{IMG_EXT}")):
        parts.append(f'  <figure class="shot"><img loading="lazy" src="{img}" alt="第{n}页">'
                     f'<figcaption>课件第 {n} 页 · 点击放大</figcaption></figure>')
    else:
        parts.append('  <p class="missing">（该页图片未导出）</p>')
    if body:
        h = md_to_html(body)
        if pat is not None:
            # per-page budget; `used` persists across the lecture so each term links once
            h = linkify(h, pat, table, lec.setdefault("_used", set()), lec.setdefault("_budget", [MAX_LINKS_PER_PAGE]))
        parts.append('  <div class="teach">' + h + "</div>")
    else:
        parts.append('  <div class="teach"><p class="todo">（本页讲解待补）</p></div>')
    if raw:
        parts.append('  <details class="raw"><summary>幻灯片原文 / 板书</summary><pre>' + esc(raw) + "</pre></details>")
    parts.append("</section>")
    return "\n".join(parts)

def build_lecture(lec, syllabus, gloss, pat, table):
    lec.pop("_used", None); lec.pop("_budget", None)
    data = json.load(open(os.path.join(WORK, lec["json"]), encoding="utf-8"))
    all_slides = data["slides"]
    lo, hi = lec.get("range", [1, 10 ** 9])
    skip = set(lec.get("skip", []))
    slides = [s for s in all_slides if lo <= s["n"] <= hi and s["n"] not in skip]
    notes = parse_lecture_md(os.path.join(SRC, lec["id"] + ".md"))
    body_all = []
    toc = []
    for sl in slides:
        body_all.append(slide_html(lec, sl, notes.get(sl["n"], ""), pat, table))
        toc.append(f'<a href="#s{sl["n"]}" data-n="{sl["n"]}"><b>{sl["n"]}</b>{esc(auto_title(sl, notes.get(sl["n"], ""))[:38])}</a>')
    covered = len([s for s in slides if notes.get(s["n"])])
    idx = [x["id"] for x in syllabus]
    k = idx.index(lec["id"])
    prev = syllabus[k - 1] if k > 0 else None
    nxt = syllabus[k + 1] if k < len(syllabus) - 1 else None

    n_terms = len([g for g in gloss if lec["id"] in (g.get("lec") or [])])
    nav = ['<a class="navbtn" href="index.html">大纲</a>']
    nav.append(f'<a class="navbtn" href="glossary.html{"#" + lec["id"] if n_terms else ""}">术语表{(" · " + str(n_terms)) if n_terms else ""}</a>')
    if prev:
        nav.append(f'<a class="navbtn" href="{prev["id"]}.html">← {esc(prev["short"])}</a>')
    if nxt:
        nav.append(f'<a class="navbtn" href="{nxt["id"]}.html">{esc(nxt["short"])} →</a>')

    topics = "".join(f"<li>{esc(t)}</li>" for t in lec["topics"])
    after = f'<div class="after">{md_to_html(lec["after"])}</div>' if lec.get("after") else ""
    pct = int(round(100 * covered / max(1, len(slides))))
    page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(lec['title'])} · 微观经济学讲义</title>
<link rel="stylesheet" href="style.css"></head>
<body class="lec">
<header class="topbar">
  <div class="brand"><a href="index.html">微观经济学 · 逐页精讲</a></div>
  <nav class="nav">{''.join(nav)}{NAVASK}</nav>
</header>

<div class="layout">
  <aside class="side">
    <div class="side-inner">
      <h2>{esc(lec['short'])}</h2>
      <p class="side-sub">{esc(lec['title'])}</p>
      <input id="filter" type="search" placeholder="筛选本讲页码 / 关键词">
      {ai_box(n_terms)}
      <div class="toc">{''.join(toc)}</div>
    </div>
  </aside>

  <main class="main">
    <div class="lec-hero">
      <div class="crumb">{esc(lec['crumb'])}</div>
      <h1>{esc(lec['title'])}</h1>
      <p class="lead">{esc(lec['summary'])}</p>
      <div class="meta">共 <b>{len(slides)}</b> 页课件 · 已精讲 <b>{covered}</b> 页（{pct}%）</div>
      <div class="topics"><h3>本讲要点</h3><ul>{topics}</ul></div>
      {after}
    </div>
    {''.join(body_all)}
    <footer class="end">
      <p>本讲结束。{'<a href="' + nxt['id'] + '.html">继续：' + esc(nxt['short']) + ' →</a>' if nxt else '<a href="index.html">返回大纲</a>'}</p>
    </footer>
  </main>
</div>

{AI_PANEL}
<div id="lightbox" class="lightbox"><img id="lbimg" alt=""></div>
<script src="glossary-data.js"></script>
<script src="app.js"></script>
</body></html>"""
    open(os.path.join(OUT, lec["id"] + ".html"), "w", encoding="utf-8").write(page)
    return covered, len(slides)

# ------------------------------------------------------------------- AI UI ---
def ai_box(n_terms):
    return f"""<div class="ask">
        <button class="ask-open" type="button" data-ask>问老师 · 这一页哪里不懂？</button>
        <p class="ask-hint">用 DeepSeek 直接回答，会带上你正在看的这一讲和这一页。</p>
      </div>"""

NAVASK = '<button class="ask-open navask" type="button" data-ask>问老师</button>'

AI_PANEL = """<aside id="ask-panel" class="ask-panel" aria-hidden="true">
  <div class="ask-head">
    <b>问老师</b>
    <span class="ask-tag">DeepSeek</span>
    <button id="ask-close" type="button" title="关闭">×</button>
  </div>
  <div class="ask-setup" id="ask-setup">
    <p>第一次用要先填一个 DeepSeek API Key，它只存在你本机的浏览器里，直接发往 <code>api.deepseek.com</code>，不经过任何中间服务器。</p>
    <label>API Key<input id="ask-key" type="password" placeholder="sk-..." autocomplete="off"></label>
    <label>模型<select id="ask-model">
      <option value="deepseek-chat">deepseek-chat（快，够用）</option>
      <option value="deepseek-reasoner">deepseek-reasoner（慢，会推理）</option>
    </select></label>
    <button id="ask-save" type="button">保存并开始</button>
    <p class="ask-note">没有 Key？去 <a href="https://platform.deepseek.com/api_keys" target="_blank" rel="noopener">platform.deepseek.com</a> 建一个。</p>
  </div>
  <div class="ask-log" id="ask-log"></div>
  <div class="ask-foot">
    <label class="ask-ctx"><input type="checkbox" id="ask-ctx" checked> 带上当前页内容</label>
    <div class="ask-input">
      <textarea id="ask-text" rows="2" placeholder="比如：为什么 MR 会比价格低？"></textarea>
      <button id="ask-send" type="button">发</button>
    </div>
  </div>
</aside>"""

def build_glossary_page(syllabus, gloss):
    by_lec = {}
    for g in gloss:
        for l in g.get("lec") or ["其他"]:
            by_lec.setdefault(l, []).append(g)
    chips = ['<button class="chip on" data-lec="all">全部 %d</button>' % len(gloss)]
    for lec in syllabus:
        n = len(by_lec.get(lec["id"], []))
        if n:
            chips.append(f'<button class="chip" data-lec="{lec["id"]}">{esc(lec["short"])} {n}</button>')
    short_of = {lec["id"]: lec["short"] for lec in syllabus}
    cards = []
    for g in gloss:
        lecs = g.get("lec") or []
        tags = "".join(f'<a class="gl" href="{l}.html">{esc(short_of.get(l, l))}</a>' for l in lecs)
        detail = f'<p class="g-detail">{esc(g["detail"])}</p>' if g.get("detail") else ""
        cards.append(f"""<article class="gentry" id="t-{g['id']}" data-lec="{' '.join(lecs)}" data-q="{esc((g['zh'] + ' ' + g['en'] + ' ' + ' '.join(g.get('alias') or []) + ' ' + g['short']).lower())}">
  <h3><span class="g-zh">{esc(g['zh'])}</span><span class="g-en">{esc(g['en'])}</span></h3>
  <p class="g-short">{esc(g['short'])}</p>
  {detail}
  <p class="g-ex"><b>例子</b>{esc(g['example'])}</p>
  <div class="g-foot">{tags}</div>
</article>""")
    page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>术语表 · 微观经济学讲义</title>
<link rel="stylesheet" href="style.css"></head>
<body class="home">
<header class="topbar"><div class="brand"><a href="index.html">微观经济学 · 逐页精讲</a></div>
<nav class="nav"><a class="navbtn" href="index.html">大纲</a>
<a class="navbtn" href="lec01.html">第 1 讲</a>{NAVASK}</nav></header>
<div class="hero small">
  <h1>术语表</h1>
  <p class="sub">一共 {len(gloss)} 条。讲稿里带下划线的词，点一下就是这里的解释；这里也能直接查。</p>
</div>
<main class="home-main">
  <div class="gbar">
    <input id="gsearch" type="search" placeholder="搜中文、英文或缩写，比如 MR、弹性、externality">
    <div class="chips">{''.join(chips)}</div>
  </div>
  <div class="gcount" id="gcount"></div>
  <div class="glist">{''.join(cards)}</div>
  <p class="gempty" id="gempty" hidden>没找到。换个说法试试，或者清空搜索框。</p>
</main>
{AI_PANEL}
<script src="app.js"></script>
</body></html>"""
    open(os.path.join(OUT, "glossary.html"), "w", encoding="utf-8").write(page)
    return len(gloss)

def write_gloss_data(gloss):
    slim = {g["id"]: {k: g.get(k, "") for k in ("zh", "en", "short", "detail", "example", "lec")} for g in gloss}
    js = "window.GLOSSARY=" + json.dumps(slim, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(OUT, "glossary-data.js"), "w", encoding="utf-8").write(js)

def build_index(syllabus, stats, gloss):
    cards = []
    for lec in syllabus:
        cov, tot = stats.get(lec["id"], (0, 0))
        done = "已完成" if cov and cov == tot else (f"{cov}/{tot} 页已讲" if cov else "待更新")
        cards.append(f"""
    <a class="card" href="{lec['id']}.html">
      <div class="card-top"><span class="tag">{esc(lec['crumb'])}</span><span class="pages">{tot} 页 · {done}</span></div>
      <h3>{esc(lec['title'])}</h3>
      <p>{esc(lec['summary'])}</p>
      <ul class="mini">{''.join(f'<li>{esc(t)}</li>' for t in lec['topics'][:4])}</ul>
      <div class="card-foot">进入逐页精讲 →</div>
    </a>""")
    outline = ""
    op = os.path.join(SRC, "outline.md")
    if os.path.exists(op):
        outline = md_to_html(open(op, encoding="utf-8").read())
    tot_all = sum(v[1] for v in stats.values())
    cov_all = sum(v[0] for v in stats.values())
    page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>微观经济学 · 课程大纲与逐页精讲</title>
<link rel="stylesheet" href="style.css"></head>
<body class="home">
<header class="topbar"><div class="brand">微观经济学 · 逐页精讲</div>
<nav class="nav"><a class="navbtn" href="#outline">课程大纲</a>
<a class="navbtn" href="glossary.html">术语表 {len(gloss)}</a>
<a class="navbtn" href="#lectures">逐讲入口</a>
<a class="navbtn" href="lec01.html">从第 1 讲开始</a>{NAVASK}</nav></header>
<div class="hero">
  <h1>微观经济学：从选择到均衡</h1>
  <p class="sub">本课程共 {len(syllabus)} 份课件、{tot_all} 页幻灯片 · 逐页「原图 + 中文精讲」<br>
  当前进度：已精讲 {cov_all} 页</p>
</div>
<main class="home-main">
  <section class="outline" id="outline">{outline}</section>
  <h2 id="lectures">逐讲入口</h2>
  <div class="cards">{''.join(cards)}</div>
  <div class="ask-home">{ai_box(len(gloss))}</div>
</main>
{AI_PANEL}
<div id="lightbox" class="lightbox"><img id="lbimg" alt=""></div>
<script src="glossary-data.js"></script>
<script src="app.js"></script>
</body></html>"""
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)

if __name__ == "__main__":
    import sys
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--out":
            OUT = os.path.abspath(argv[i + 1])
        elif a == "--ext":
            IMG_EXT = argv[i + 1]
        elif a == "--assets":
            ASSETS = os.path.abspath(argv[i + 1])
        elif a == "--img-base":
            IMG_BASE = argv[i + 1]
    os.makedirs(OUT, exist_ok=True)
    syllabus = json.load(open(os.path.join(SRC, "syllabus.json"), encoding="utf-8"))
    LEC_ORDER.extend(x["id"] for x in syllabus)
    gloss = load_glossary()
    pat, table = term_index(gloss)
    write_gloss_data(gloss)
    stats = {}
    for lec in syllabus:
        try:
            stats[lec["id"]] = build_lecture(lec, syllabus, gloss, pat, table)
        except FileNotFoundError as e:
            print("SKIP", lec["id"], e)
    build_index(syllabus, stats, gloss)
    n = build_glossary_page(syllabus, gloss)
    print(f"glossary: {n} entries, {len(pat.pattern)} chars pattern")
    for k, v in stats.items():
        print(f"{k}: {v[0]}/{v[1]} pages explained")
