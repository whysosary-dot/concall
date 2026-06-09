#!/usr/bin/env python3
"""
fetch_channel.py — @earnmoar(또는 임의) 채널의 최근 영상 목록을 긁어와
티커/회사명/연도/분기를 파싱해 calls.json '대기(pending)' 항목으로 추가.

사용법:
    python3 scripts/fetch_channel.py "https://www.youtube.com/@earnmoar/videos" --limit 30

제목 형식 예: "$DELL Dell Technologies Q1 2027 Earnings Conference Call"
실제 자막·요약·번역은 이후 Claude(Cowork)가 fetch_transcript.py로 채웁니다.
"""
import argparse, json, re, subprocess, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "calls.json")

# 티커 → 산업 대분류 매핑(예시, 필요시 확장)
SECTOR = {
    "DELL":("기술/IT","Computer Hardware"),"AVGO":("기술/IT","Semiconductors"),
    "AMBA":("기술/IT","Semiconductors"),"PANW":("기술/IT","Cybersecurity"),
    "S":("기술/IT","Cybersecurity"),"OSPN":("기술/IT","Cybersecurity"),
    "MDB":("기술/IT","Software"),"PATH":("기술/IT","Software"),
    "ADSK":("기술/IT","Software"),"NTAP":("기술/IT","Computer Hardware"),
    "COST":("소비재","Retail"),"DG":("소비재","Retail"),"DLTR":("소비재","Retail"),
    "OLLI":("소비재","Retail"),"GAP":("소비재","Apparel"),"AEO":("소비재","Apparel"),
    "KSS":("소비재","Retail"),"MAMA":("소비재","Food"),"UHAL":("산업재","Logistics"),
    "MOD":("산업재","Industrials"),
}

def parse_title(t):
    m = re.match(r"\$(\w+)\s+(.+?)\s+Q([1-4])\s+(\d{4})\s+Earnings", t)
    if not m: return None
    tk, name, q, yr = m.group(1), m.group(2), m.group(3), m.group(4)
    ind, sub = SECTOR.get(tk, ("미분류", ""))
    return {"ticker": tk, "company": name, "industry": ind, "subindustry": sub,
            "year": yr, "quarter": f"Q{q}",
            "title": t.replace(f"${tk} ", "")}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--limit", type=int, default=30)
    a = ap.parse_args()
    r = subprocess.run(["yt-dlp","--flat-playlist","-I",f"1:{a.limit}",
        "--print","%(id)s\t%(title)s", a.url], capture_output=True, text=True)
    db = json.load(open(DB, encoding="utf-8")) if os.path.exists(DB) else {"calls": []}
    have = {c["id"] for c in db["calls"]}
    added = 0
    for line in r.stdout.strip().splitlines():
        vid, _, title = line.partition("\t")
        p = parse_title(title)
        if not p: continue
        cid = f"{p['ticker']}-{p['year']}{p['quarter']}"
        if cid in have: continue
        db["calls"].append({"id": cid, **p, "videoId": vid,
            "videoUrl": f"https://youtu.be/{vid}", "publishedAt": "",
            "status": "pending", "summary_ko": "", "transcript_ko": "",
            "transcript_en": "", "qa_ko": ""})
        have.add(cid); added += 1
    db["updated"] = datetime.date.today().isoformat()
    json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ {added}건 추가(대기). 총 {len(db['calls'])}건.")

if __name__ == "__main__":
    main()
