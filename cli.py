"""Offline demo: python cli.py  (no Fetch.ai install needed)"""
from core import *
p = {}
print("Haqdaar: tell me about yourself (state, income, category, occupation, age).")
while (q := next_question(p)) or True:
    if q is None: break
    p = parse(input(f"{q}\n> "), p)
have = [x.strip() for x in input("Documents you already have (comma-separated)?\n> ").split(",") if x.strip()]
print(full_report(p, have))
import json
ms = match_schemes(p)
if ms: print("\nPre-filled form for", ms[0]["name"]); print(json.dumps(prefill(ms[0], p), indent=2, ensure_ascii=False))
