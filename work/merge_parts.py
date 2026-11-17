import sys, pathlib

out = pathlib.Path(sys.argv[1])
parts = [pathlib.Path(p) for p in sys.argv[2:]]
txt = "\n\n".join(p.read_text(encoding='utf-8').strip() + "\n" for p in parts)
out.write_text(txt, encoding='utf-8')
print("wrote", out, len(txt), "chars")
