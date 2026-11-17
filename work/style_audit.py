# -*- coding: utf-8 -*-
"""扫描 src/*.md 里的 AI 腔套路句，统计到文件与句式，供后续逐类清理。"""
import re, os, sys, glob, io

SRC = r'D:\WILL\ECON102\src'

PATTERNS = [
    ('hedge', r'值得注意的是|值得一提|可以说|某种程度上|在一定程度上|总的来说|一般来说|基本上|不难发现|显而易见'),
    ('trans', r'(?:^|[。！？\n])\s*此外，|(?:^|[。！？\n])\s*与此同时，|(?:^|[。！？\n])\s*由此可见|(?:^|[。！？\n])\s*换言之|(?:^|[。！？\n])\s*换句话说|(?:^|[。！？\n])\s*其次，|(?:^|[。！？\n])\s*再次，'),
    ('summary', r'综上所述|总而言之|总的说来|(?:^|[。！？\n])\s*总之|说到底|归根结底|简而言之'),
    ('overexp', r'也就是说，|换句话说，|说白了|这就意味着|其核心在于'),
    ('parallel', r'一方面.{0,25}另一方面|首先.{0,40}其次|不仅.{0,30}而且.{0,20}还|一是.{0,25}二是'),
    ('cliche', r'赋能|抓手|闭环|底层逻辑|顶层设计|颗粒度|护城河|天花板|红利|赛道|生态位|降维打击|长期主义|破圈|拉满|出圈|弯道超车|降本增效|全链路'),
    ('echo', r'这页(?:在|的)?(?:意思|意思就是|要说的是)'),
    ('filler', r'一句话[，:]|简单说|直白地说|请注意|请记住|记住这句话|划重点'),
]

def main():
    files = sorted(glob.glob(os.path.join(SRC, '*.md')))
    total = {}
    per_file = []
    hits = []
    for f in files:
        txt = io.open(f, encoding='utf-8').read()
        name = os.path.basename(f)
        cnt = {}
        for tag, pat in PATTERNS:
            ms = list(re.finditer(pat, txt))
            if ms:
                cnt[tag] = cnt.get(tag, 0) + len(ms)
                total[tag] = total.get(tag, 0) + len(ms)
                for m in ms[:400]:
                    s = max(0, m.start() - 22); e = min(len(txt), m.end() + 22)
                    hits.append((tag, name, txt[s:e].replace('\n', ' ')))
        per_file.append((name, sum(cnt.values()), cnt))
    print('=== 分类总计 ===')
    for k, v in sorted(total.items(), key=lambda x: -x[1]):
        print(f'{k:9s} {v}')
    print('总计', sum(total.values()))
    print('\n=== 每讲 ===')
    for name, s, cnt in per_file:
        print(f'{name:12s} {s:4d}  ' + ' '.join(f'{k}:{v}' for k, v in cnt.items()))
    print('\n=== 抽样（每类前 8 条）===')
    seen = {}
    for tag, name, ctx in hits:
        if seen.get(tag, 0) < 8:
            seen[tag] = seen.get(tag, 0) + 1
            print(f'[{tag}] {name}: …{ctx}…')

if __name__ == '__main__':
    main()
