#!/usr/bin/env python3
"""
fetch_transcript.py — 유튜브 영상에서 자동/수동 자막을 받아 깨끗한 텍스트로 출력.

사용법:
    python3 scripts/fetch_transcript.py "https://youtu.be/VIDEO_ID"
    python3 scripts/fetch_transcript.py "https://youtu.be/VIDEO_ID" --lang en --json out.json

요구사항: yt-dlp  (pip install yt-dlp)
API 키 불필요. 출력된 영어 텍스트를 Claude(Cowork)에게 주면 요약·번역을 채웁니다.
"""
import argparse, json, re, subprocess, sys, tempfile, os, glob

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def get_meta(url):
    r = run(["yt-dlp", "--skip-download", "--print",
             "%(id)s\t%(title)s\t%(upload_date)s\t%(channel)s", url])
    parts = (r.stdout.strip().split("\t") + ["", "", "", ""])[:4]
    return {"videoId": parts[0], "title": parts[1],
            "publishedAt": parts[2], "channel": parts[3]}

def vtt_to_text(path):
    lines, seen, out = open(path, encoding="utf-8").read().splitlines(), set(), []
    for ln in lines:
        if (not ln.strip() or "-->" in ln or ln.startswith(("WEBVTT", "Kind:", "Language:"))
                or re.match(r"^\d+$", ln)):
            continue
        ln = re.sub(r"<[^>]+>", "", ln).strip()          # strip <c> timing tags
        ln = re.sub(r"\[.*?\]", "", ln).strip()           # strip [Music] etc
        if ln and ln not in seen:                          # dedupe rolling captions
            seen.add(ln); out.append(ln)
    # join into flowing paragraphs (~ every 6 lines)
    text, buf = [], []
    for i, ln in enumerate(out):
        buf.append(ln)
        if len(buf) >= 6:
            text.append(" ".join(buf)); buf = []
    if buf: text.append(" ".join(buf))
    return "\n\n".join(text)

def fetch(url, lang):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "cap.%(ext)s")
        # try manual subs first, then auto-generated
        for flag in ["--write-subs", "--write-auto-subs"]:
            run(["yt-dlp", "--skip-download", flag, "--sub-lang",
                 f"{lang}.*,{lang}", "--sub-format", "vtt", "-o", out, url])
            files = glob.glob(os.path.join(d, "*.vtt"))
            if files:
                # prefer exact lang match
                files.sort(key=lambda f: (lang not in os.path.basename(f), len(f)))
                return vtt_to_text(files[0])
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--json", help="메타+자막을 JSON 파일로 저장")
    a = ap.parse_args()

    meta = get_meta(a.url)
    text = fetch(a.url, a.lang)
    if not text:
        sys.exit(f"❌ '{a.lang}' 자막을 찾지 못했습니다. (--lang 으로 언어 코드 변경)")

    if a.json:
        rec = {**meta, "videoUrl": a.url, "transcript_en": text,
               "summary_ko": "", "transcript_ko": "", "qa_ko": "", "status": "fetched"}
        json.dump(rec, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"✅ 저장: {a.json}  ({len(text)}자)")
    else:
        print(f"# {meta['title']}  ({meta['publishedAt']})\n")
        print(text)

if __name__ == "__main__":
    main()
