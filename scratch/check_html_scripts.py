# -*- coding: utf-8 -*-
import re
import subprocess

with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

scripts = re.findall(r'<script(?:\s+nonce="[^"]*")?>(.*?)</script>', text, re.DOTALL)
print(f"Found {len(scripts)} inline script blocks.")

for i, s in enumerate(scripts):
    fname = f"scratch/script_{i}.js"
    with open(fname, "w", encoding="utf-8") as sf:
        sf.write(s)
    res = subprocess.run(["node", "-c", fname], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in {fname}:\n{res.stderr}")
    else:
        print(f"{fname}: SYNTAX OK")
