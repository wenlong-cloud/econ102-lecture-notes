# -*- coding: utf-8 -*-
"""Build the lightweight portable package: JPEG slides + static site + launcher.

Output:
  dist/ECON102-讲义/course/*.html|css|js
  dist/ECON102-讲义/assets/<dir>/slide-NNN.jpg
  dist/ECON102-讲义/打开讲义.bat
  dist/ECON102-讲义/使用说明.txt
  dist/ECON102-微观经济学讲义.zip
"""
import os, re, glob, shutil, subprocess, sys, time
from PIL import Image

ROOT = r"D:\WILL\ECON102"
COURSE = os.path.join(ROOT, "course")
DIST = os.path.join(ROOT, "dist")
PKG = os.path.join(DIST, "ECON102-讲义")
MAXW = 1200
QUAL = 80

t0 = time.time()

# ---- 1. which images does the site actually reference? ----------------------
used = set()
for p in glob.glob(os.path.join(COURSE, "*.html")):
    h = open(p, encoding="utf-8").read()
    for m in re.finditer(r'src="\.\./assets/([^/"]+)/(slide-\d+\.png)"', h):
        used.add((m.group(1), m.group(2)))
print("used images:", len(used))

# ---- 2. convert png -> jpg -------------------------------------------------
dst_assets = os.path.join(PKG, "assets")
if os.path.exists(dst_assets):
    shutil.rmtree(dst_assets)
tot = 0
n = 0
for d, name in sorted(used):
    src = os.path.join(ROOT, "assets", d, name)
    if not os.path.exists(src):
        print("MISSING", src)
        continue
    out_dir = os.path.join(dst_assets, d)
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(src)
    if im.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    out = os.path.join(out_dir, name[:-4] + ".webp")
    im.save(out, "WEBP", quality=QUAL, method=6)
    tot += os.path.getsize(out)
    n += 1
    if n % 100 == 0:
        print(f"  {n}/{len(used)}  {tot/1e6:.1f} MB  {time.time()-t0:.0f}s")

print(f"converted {n} images, {tot/1e6:.1f} MB")

# ---- 3. rebuild the html against the jpg assets ---------------------------
py = sys.executable
subprocess.run([py, os.path.join(ROOT, "work", "build_site.py"),
                "--out", os.path.join(PKG, "course"),
                "--ext", ".webp",
                "--assets", dst_assets,
                "--img-base", "../assets"], check=True,
               env={**os.environ, "PYTHONIOENCODING": "utf-8"})

for f in ("style.css", "app.js"):
    shutil.copy2(os.path.join(COURSE, f), os.path.join(PKG, "course", f))

# ---- 4. launcher + readme -------------------------------------------------
bat = """@echo off
chcp 65001 >nul
start "" "%~dp0course\\index.html"
"""
open(os.path.join(PKG, "打开讲义.bat"), "w", encoding="utf-8", newline="\r\n").write(bat)

readme = """ECON102 微观经济学 · 逐页精讲
================================

怎么打开
--------
双击「打开讲义.bat」，会用你的默认浏览器打开首页。

或者：把 course\\index.html 直接拖进浏览器窗口。

这个包是纯静态网页，不用装软件、不用联网、不用启动服务器。整个文件夹可以
随便拷到 U 盘或别的电脑上，只要保证 assets 和 course 两个文件夹在同一个
父文件夹里（页面用相对路径找图）。

里面有什么
----------
course\\index.html      课程大纲 + 逐讲入口
course\\lec01.html ...  14 个讲次的逐页精讲（原幻灯片图 + 中文讲稿）
course\\glossary.html   术语表，221 条，可搜索、可按讲次筛选
course\\style.css       样式
course\\app.js          交互（放大图、目录高亮、术语弹层、问老师）

怎么读
------
- 左边是页码目录，点一下跳到那一页；顶上搜索框可以筛选页码或关键词。
- 键盘 j / k 或 ← / → 翻上下一页。
- 讲稿里带下划线的词，点一下弹出中英文解释和例子。
- 每页下方的「幻灯片原文 / 板书」可以展开，看到 PPT 上的英文原文。
- 点图片可以放大，再点一次关闭。

关于「问老师」
--------------
右上角和左侧栏都有「问老师」按钮，右侧会滑出一个对话框，可以直接问
DeepSeek，它会带上你正在看的那一讲、那一页。

第一次用要先填一个 API Key：
  1. 打开 https://platform.deepseek.com 注册（手机号即可）
  2. 充值一点（10 元够问上千次），左侧「API keys」→ 创建，复制 sk- 开头的那串
  3. 粘贴到对话框里，点「保存并开始」

Key 只存在你这台电脑的浏览器里，不会写进本文件夹，所以把这个包发给别人时
不会带走你的 Key。

注意
----
- 幻灯片是压缩过的 1200px 图片，为了把包控制在几十 MB。原始 1600px 版本
  在老师的电脑上是另一份。
- 课件里有两处小错，讲稿里已经标出来了：第 7 讲有个「40 吨」被印成 400 吨；
  第 3 讲的工资税例子实际是 50%，不是 20%。
"""
open(os.path.join(PKG, "使用说明.txt"), "w", encoding="utf-8").write(readme)

# ---- 5. zip ---------------------------------------------------------------
zpath = os.path.join(DIST, "ECON102-微观经济学讲义.zip")
if os.path.exists(zpath):
    os.remove(zpath)
shutil.make_archive(zpath[:-4], "zip", DIST, "ECON102-讲义")
print(f"zip: {os.path.getsize(zpath)/1e6:.1f} MB")
sz = sum(os.path.getsize(os.path.join(dp, f))
         for dp, _, fs in os.walk(PKG) for f in fs)
print(f"package dir: {sz/1e6:.1f} MB, {time.time()-t0:.0f}s total")
