#!/usr/bin/env python3
"""
add_to_calls.py — 처리된 컨콜 1건을 data/calls.json에 추가/갱신.

사용법:
    python3 scripts/add_to_calls.py record.json
같은 id가 있으면 덮어쓰고, 없으면 맨 앞에 추가합니다.
"""
import json, sys, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "calls.json")

rec = json.load(open(sys.argv[1], encoding="utf-8"))
if not rec.get("id"):
    rec["id"] = f"{rec.get('ticker','X')}-{rec.get('year','')}{rec.get('quarter','')}"

db = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else {"calls": []}
db["calls"] = [c for c in db["calls"] if c.get("id") != rec["id"]]
db["calls"].insert(0, rec)
db["updated"] = datetime.date.today().isoformat()
json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"✅ '{rec['id']}' 추가됨. 총 {len(db['calls'])}건.")
