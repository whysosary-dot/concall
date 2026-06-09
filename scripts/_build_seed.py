#!/usr/bin/env python3
# 1회용: 채널 목록 + Dell 실제 번역으로 data/calls.json 시드 생성
import json, re, subprocess, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "calls.json")

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
def parse(t):
    m=re.match(r"\$(\w+)\s+(.+?)\s+Q([1-4])\s+(\d{4})\s+Earnings",t)
    if not m:return None
    tk,name,q,yr=m.groups()
    ind,sub=SECTOR.get(tk,("미분류",""))
    return {"ticker":tk,"company":name,"industry":ind,"subindustry":sub,
            "year":yr,"quarter":f"Q{q}","title":t.replace(f"${tk} ","")}

r=subprocess.run(["yt-dlp","--flat-playlist","-I","1:30","--print","%(id)s\t%(title)s",
    "https://www.youtube.com/@earnmoar/videos"],capture_output=True,text=True)
calls=[]
for line in r.stdout.strip().splitlines():
    vid,_,title=line.partition("\t"); p=parse(title)
    if not p:continue
    calls.append({"id":f"{p['ticker']}-{p['year']}{p['quarter']}",**p,"videoId":vid,
        "videoUrl":f"https://youtu.be/{vid}","publishedAt":"","status":"pending",
        "summary_ko":"","transcript_ko":"","transcript_en":"","qa_ko":""})

# ---- Dell 실제 콘텐츠 주입 ----
EN=__import__("dell_content",fromlist=["EN"]).EN if False else None
from dell_content import EN, KO, SUMMARY, QA
for c in calls:
    if c["id"]=="DELL-2027Q1":
        c["status"]="done"; c["publishedAt"]="2026-05-29"
        c["transcript_en"]="\n\n".join(EN); c["transcript_ko"]="\n\n".join(KO)
        c["summary_ko"]=SUMMARY; c["qa_ko"]=QA

# Dell을 맨 앞으로
calls.sort(key=lambda c:(c["id"]!="DELL-2027Q1",))
json.dump({"updated":datetime.date.today().isoformat(),"calls":calls},
    open(DB,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(f"✅ {len(calls)}건 시드 생성. done={sum(1 for c in calls if c['status']=='done')}")
