# 📞 해외사 컨콜 모음

유튜브에 올라온 해외 기업 실적발표 컨퍼런스콜(Earnings Call)을 자동으로 수집해
**핵심 요약 + 한국어 전문 번역**으로 보여주는 정적 웹사이트입니다.
GitHub Pages로 무료 호스팅됩니다. **API 키가 필요 없습니다.**

---

## 동작 원리

```
유튜브 URL
   │
   ▼  ① 수집  (scripts/fetch_transcript.py)
yt-dlp 가 자동/수동 자막(VTT)을 받아 깨끗한 영어 텍스트로 변환
   │
   ▼  ② 요약·번역  ← 번역 엔진 = Cowork의 Claude
영어 자막을 Claude에게 주면 핵심요약 / 전문번역 / Q&A 를 작성
   │
   ▼  ③ 저장  (scripts/add_to_calls.py)
결과를 data/calls.json 에 추가
   │
   ▼  ④ 배포  (git push → GitHub Pages)
index.html 이 calls.json 을 읽어 화면에 렌더링
```

> **왜 이런 구조인가?** 순수 정적 사이트(브라우저 JS만)로는 유튜브 자막을 직접 못 받습니다(CORS 차단). 번역도 LLM이 필요합니다. 그래서 수집·번역은 *바깥에서* 하고, 사이트는 결과 JSON만 보여주는 역할을 합니다. 번역 엔진으로 유료 API 대신 **Cowork의 Claude**를 쓰면 키가 필요 없습니다.

---

## 처음 설정 (5분)

1. 이 폴더를 GitHub 새 저장소에 올립니다.
   ```bash
   cd concall
   git init && git add . && git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/<USERNAME>/<REPO>.git
   git push -u origin main
   ```
2. GitHub 저장소 → **Settings → Pages → Source: GitHub Actions** 선택.
3. 잠시 후 `https://<USERNAME>.github.io/<REPO>/` 에서 공개됩니다.

---

## 컨콜 추가하기 (매번 하는 일)

Cowork에서 Claude에게 이렇게 말하면 ①~③을 대신 해줍니다:

> "이 컨콜 추가해줘: https://youtu.be/XXXX  (티커 NVDA, 반도체, 2027 Q1)"

Claude가 내부적으로 실행하는 흐름:

```bash
# ① 자막 수집
python3 scripts/fetch_transcript.py "https://youtu.be/XXXX" --lang en --json /tmp/rec.json

# ② Claude가 /tmp/rec.json 의 transcript_en 을 읽고
#    summary_ko · transcript_ko · qa_ko · ticker · industry · year · quarter 를 채움

# ③ calls.json 에 병합
python3 scripts/add_to_calls.py /tmp/rec.json

# ④ 배포
git add data/calls.json && git commit -m "add XXXX" && git push
```

직접 하고 싶다면 ②만 손으로 채우면 됩니다.

---

## 자동화 (선택)

매주 특정 채널의 새 컨콜을 자동으로 모으고 싶으면 Cowork의 **스케줄 태스크**를 쓰세요.
예: "매주 월요일 아침에 EarnMoar 채널 새 영상 확인해서 컨콜 추가해줘."
Claude가 채널 신규 영상을 훑어 위 흐름을 반복합니다.

---

## 데이터 구조 (`data/calls.json`)

```jsonc
{
  "updated": "2026-06-09",
  "calls": [
    {
      "id": "NVDA-2027Q1",          // 고유 ID
      "ticker": "NVDA",
      "company": "NVIDIA",
      "title": "NVIDIA Q1 2027 Earnings Call",
      "industry": "기술/IT",          // 필터용
      "subindustry": "Semiconductors",
      "year": "2027", "quarter": "Q1",
      "videoUrl": "https://youtu.be/...",
      "publishedAt": "2026-05-28",
      "status": "done",
      "summary_ko": "## 마크다운...",  // 핵심요약 탭
      "transcript_ko": "한국어 전문...", // 전문번역 탭
      "transcript_en": "English...",   // 원문 탭 (한·영 대조에도 사용)
      "qa_ko": "## Q&A 마크다운..."     // Q&A 탭
    }
  ]
}
```

`summary_ko`, `qa_ko`는 마크다운으로 렌더링되고, `**굵게**`는 형광펜으로 강조됩니다.
`transcript_ko`/`transcript_en`은 빈 줄(`\n\n`)로 문단을 나누면 '한·영 대조' 탭에서 문단끼리 맞춰 보여줍니다.

---

## 파일 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 단일 파일 뷰어 (필터·탭·검색) |
| `data/calls.json` | 컨콜 데이터 |
| `scripts/fetch_transcript.py` | yt-dlp 자막 수집 → 텍스트 |
| `scripts/add_to_calls.py` | 결과를 calls.json에 병합 |
| `.github/workflows/deploy.yml` | GitHub Pages 자동 배포 |

---

## 로컬에서 미리보기

`file://`로 열면 브라우저 보안 때문에 `calls.json`을 못 읽습니다. 간단한 서버로 여세요:

```bash
cd concall && python3 -m http.server 8000
# 브라우저에서 http://localhost:8000
```
