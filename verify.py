#!/usr/bin/env python3
"""lusus 公证链的独立校验：只用标准库。用法：python3 verify.py [仓库目录]"""
import hashlib, json, re, sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent)
bad, prev, seq, by_seq = [], "0" * 64, 0, {}
files = sorted((root / "chain").rglob("*.jsonl"))
for f in files:
    for n, line in enumerate(f.read_text("utf-8").splitlines(), 1):
        e = json.loads(line)
        seq += 1
        if e["seq"] != seq:
            bad.append(f"{f.name}:{n} seq 应为 {seq}，实为 {e['seq']}")
            seq = e["seq"]
        if e["prev"] != prev:
            bad.append(f"{f.name}:{n} prev 与上一条 link 不符")
        link = hashlib.sha256(bytes.fromhex(e["prev"]) + bytes.fromhex(e["leaf"])).hexdigest()
        if link != e["link"]:
            bad.append(f"{f.name}:{n} link 算不出来")
        prev, by_seq[e["seq"]] = e["link"], e
    for ext in (".ots", ".tsr"):
        if not f.with_name(f.name + ext).exists():
            print(f"提示：{f.name}{ext} 不存在")
ids = {}
for e in by_seq.values():
    m = re.fullmatch(r"(J|TH|K)-(\d+)", e["item"])
    if m:
        ids.setdefault(m.group(1), []).append(int(m.group(2)))
for t, ns in sorted(ids.items()):
    gaps = sorted(set(range(1, max(ns) + 1)) - set(ns))
    dup = len(ns) - len(set(ns))
    print(f"{t}：{len(ns)} 条，编号 1–{max(ns)}" + (f"，缺 {gaps[:20]}" if gaps else "，连续") + (f"，重复 {dup}" if dup else ""))
    if gaps or dup:
        bad.append(f"{t} 编号不连续或重复")
rev = sorted((root / "reveals").glob("*.json")) if (root / "reveals").exists() else []
for f in rev:
    r = json.loads(f.read_text("utf-8"))
    e = by_seq.get(r["seq"])
    leaf = hashlib.sha256(r["payload"].encode("utf-8")).hexdigest()
    if not e or e["item"] != r["item"] or e["leaf"] != leaf:
        bad.append(f"揭晓 {f.name} 与链上 leaf 不符")
print(f"链：{seq} 条、{len(files)} 个批次；揭晓 {len(rev)} 条；链头 {prev}")
print("✗ " + "\n✗ ".join(bad) if bad else "✓ 全部通过")
sys.exit(1 if bad else 0)
