# KOSPI 수급 브리핑 (CCC 출품작)

매일 아침 7시, 전일 코스피의 **개인·외국인·기관 수급**과 **"누가, 왜 사고 팔았는지"**를 차트와 약식 보고서로 자동 게시합니다.

## 구성
| 파일 | 역할 |
|---|---|
| `collect.py` | 네이버페이 증권 공개 API에서 지수·시총 상위 100종목 투자자별 순매수, 뉴스 수집 (로그인 불필요) |
| `analyze.py` | Claude(claude-opus-5-5)가 데이터+뉴스+웹검색으로 수급 원인 해설 생성. API 키가 없으면 규칙 기반 요약 |
| `render.py` | 반응형 HTML 리포트(차트·표·다크모드) 생성 → `site/index.html`, `site/r/날짜.html`, `site/archive.html` |
| `main.py` | 위 3단계를 순서대로 실행 |
| `.github/workflows/daily.yml` | 평일 06:30 KST 자동 실행 → GitHub Pages에 게시 |

## 로컬 실행
```powershell
.\.venv\Scripts\python main.py            # 마지막 거래일
.\.venv\Scripts\python main.py 20261118   # 특정일
```
AI 해설을 쓰려면 실행 전에 `$env:ANTHROPIC_API_KEY = "..."` 를 직접 설정하세요.

## 매일 자동 게시 (GitHub, 무료)
1. github.com 에서 새 저장소(public) 생성 → 이 `kospi_flow` 폴더 내용을 업로드 (`.venv` 제외)
2. 저장소 **Settings → Secrets and variables → Actions → New repository secret**
   이름 `ANTHROPIC_API_KEY`, 값은 console.anthropic.com 에서 발급한 키
3. **Settings → Pages → Build and deployment → Source: GitHub Actions**
4. **Actions 탭 → daily-kospi-flow → Run workflow** 로 첫 실행 확인
5. 이후 평일 아침 자동 실행. 주소: `https://<아이디>.github.io/<저장소명>/`

## 참고
- 종목별 금액은 `순매수 수량 × 종가` 추정치입니다 (지수 합계는 거래소 집계 금액).
- 본 자료는 정보 제공 목적이며 투자 권유가 아닙니다.
