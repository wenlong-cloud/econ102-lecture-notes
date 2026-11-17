import json, re, pathlib, sys

SRC = pathlib.Path(r"D:\WILL\ECON102\src")
WORK = pathlib.Path(r"D:\WILL\ECON102\work")

counts = {
    "lec01": 67, "lec01s": 5, "lec02": 86, "lec03": 94, "lec04": 70, "lec05": 73,
    "lec06": 23, "lec07": 66, "lec08": 24, "lec08b": 64, "lec08s": 36,
    "lec09": 85, "lec10": 128, "lec12": 65,
}

only = sys.argv[1:] or sorted(counts)
for tag in only:
    p = SRC / f"{tag}.md"
    if not p.exists():
        print(f"{tag:8s} MISSING")
        continue
    txt = p.read_text(encoding="utf-8")
    blocks = re.split(r"^###\s+(\d+)\s*$", txt, flags=re.M)
    # blocks = [pre, n1, body1, n2, body2, ...]
    pages = {}
    for i in range(1, len(blocks), 2):
        pages[int(blocks[i])] = blocks[i + 1].strip()
    nums = sorted(pages)
    need = counts[tag]
    problems = []
    if nums != list(range(1, need + 1)):
        missing = [n for n in range(1, need + 1) if n not in pages]
        extra = [n for n in nums if n > need]
        if missing:
            problems.append(f"missing {missing[:12]}{'...' if len(missing) > 12 else ''} ({len(missing)})")
        if extra:
            problems.append(f"extra {extra[:12]}")
        if not missing and not extra:
            problems.append("order/dup issue")
    lens = {n: len(re.sub(r"\s", "", pages.get(n, ""))) for n in nums}
    short = [n for n, L in lens.items() if L < 60]
    longs = [n for n, L in lens.items() if L > 700]
    dup = []
    seen = {}
    for n in nums:
        key = re.sub(r"\s", "", pages[n])[:80]
        if key in seen:
            dup.append((seen[key], n))
        seen[key] = n
    total = sum(lens.values())
    di = sum(1 for n in nums if lens[n] < 100)
    msg = f"{tag:8s} pages={len(nums)}/{need} chars={total} avg={total // max(1, len(nums))} short(<60)={len(short)} tiny(<100)={di} long(>700)={len(longs)} dup={dup[:5]}"
    if problems:
        msg += "  PROBLEMS: " + "; ".join(problems)
    print(msg)
    if short:
        print("   short pages:", short[:20])
    if longs:
        print("   long pages:", longs[:20])
