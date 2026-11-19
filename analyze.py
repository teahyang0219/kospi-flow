"""수급 데이터 -> Claude가 '누가 왜 사고 팔았는지' 해설 (JSON).

ANTHROPIC_API_KEY 가 없으면 규칙 기반 요약으로 대체한다.
"""
from __future__ import annotations

import json
import os
import re

MODEL = "claude-opus-5-5"
INV = ("외국인", "기관", "개인")


def _fmt(v: float) -> str:
    return f"{v:+,.0f}억"


def build_context(d: dict) -> str:
    s = {x["code"]: x for x in d["stocks"]}
    f = d["flow_today"]
    hist = d["flow_hist"][-5:]
    cum5 = {k: sum(h[k] for h in hist) for k in INV}
    lines = [
        f"[기준일] {d['date']}",
        f"[코스피] 종가 {d['index']['close']:,.2f} ({d['index']['pct']:+.2f}%), 고가 {d['index']['high']:,.2f} 저가 {d['index']['low']:,.2f}",
        f"[코스피 투자자별 순매수, 억원] " + ", ".join(f"{k} {_fmt(f[k])}" for k in INV),
        f"[최근 5거래일 누적] " + ", ".join(f"{k} {_fmt(cum5[k])}" for k in INV),
        "[최근 20거래일 일별] " + " | ".join(
            f"{h['date'][4:]} 외{h['외국인']:+,.0f}/기{h['기관']:+,.0f}/개{h['개인']:+,.0f}" for h in d["flow_hist"]),
        "",
        "[시총 상위 100종목 투자자별 순매수 상위/하위 (억원, 종가×수량 추정)]",
    ]
    for inv in INV:
        for side, label in (("buy", "순매수"), ("sell", "순매도")):
            items = [s[c] for c in d["ranks"][inv][side][:7]]
            lines.append(f"{inv} {label}: " + ", ".join(
                f"{x['name']}({x['code']}) {_fmt(x[inv])} [{x['pct']:+.2f}%]" for x in items))
    lines += ["", "[종목 뉴스 헤드라인]"]
    for code, heads in d["stock_news"].items():
        if code in s and heads:
            lines.append(f"- {s[code]['name']}: " + " / ".join(heads))
    lines += ["", "[증시 주요뉴스]"]
    for n in d["market_news"]:
        lines.append(f"- {n['title']} — {n['summary']}")
    return "\n".join(lines)


SYSTEM = """당신은 증권사 리서치센터의 시황 애널리스트입니다. 매일 아침 영업점 직원과 고객이 3분 안에 읽는 '전일 코스피 수급 브리핑'을 씁니다.
원칙:
- 숫자는 제공된 데이터만 사용하고 새로 만들지 마세요.
- '왜'를 설명할 때는 제공된 뉴스 또는 웹검색으로 확인한 사실(전일 미국 증시, 환율, 금리, 업종 이슈, 실적, 공시 등)에 근거하세요. 근거가 약하면 문장 끝에 '(추정)'을 붙이세요.
- 투자 권유가 아닌 사실 해설 톤. 짧고 단정한 문장. 한국어."""

INSTR = """위 데이터를 바탕으로 아래 JSON 하나만 출력하세요(코드블록 없이).
{
  "headline": "한 줄 제목 (30자 이내, 핵심 수급 주체와 방향 포함)",
  "summary": ["시황 요약 문장 3~4개"],
  "investors": {
    "외국인": {"stance": "순매수|순매도", "one_line": "한 줄 요약", "why": "이유 2~3문장"},
    "기관": {...같은 형식},
    "개인": {...같은 형식}
  },
  "stocks": [{"code": "종목코드", "name": "종목명", "who": "주도 주체 예: 외국인 매수·개인 매도", "why": "이유 1~2문장"}],
  "watch": ["오늘 장에서 지켜볼 포인트 2~3개"]
}
stocks에는 수급이 가장 두드러진 종목 8~10개를 고르세요."""


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in response")
    return json.loads(m.group(0))


def ai_commentary(d: dict, web_search: bool = True) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}] if web_search else []
    resp = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium"},
        system=SYSTEM,
        tools=tools,
        messages=[{"role": "user", "content": build_context(d) + "\n\n" + INSTR}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("model refused")
    text = "".join(b.text for b in resp.content if b.type == "text")
    out = _extract_json(text)
    out["_source"] = "ai"
    return out


def rule_commentary(d: dict) -> dict:
    """API 키 없이도 동작하는 기본 해설."""
    s = {x["code"]: x for x in d["stocks"]}
    f = d["flow_today"]
    idx = d["index"]
    top_buyer = max(INV, key=lambda k: f[k])
    top_seller = min(INV, key=lambda k: f[k])
    inv = {}
    for k in INV:
        b = [s[c]["name"] for c in d["ranks"][k]["buy"][:3]]
        se = [s[c]["name"] for c in d["ranks"][k]["sell"][:3]]
        inv[k] = {"stance": "순매수" if f[k] >= 0 else "순매도",
                  "one_line": f"{_fmt(f[k])} {'순매수' if f[k] >= 0 else '순매도'}",
                  "why": f"매수 상위 {', '.join(b)} / 매도 상위 {', '.join(se)}."}
    stocks = []
    for k in INV:
        for c in d["ranks"][k]["buy"][:2] + d["ranks"][k]["sell"][:1]:
            x = s[c]
            stocks.append({"code": c, "name": x["name"],
                           "who": f"{k} {'매수' if x[k] > 0 else '매도'} {_fmt(x[k])}",
                           "why": " / ".join(d["stock_news"].get(c, [])[:1]) or "-"})
    return {
        "headline": f"{top_buyer} 사고 {top_seller} 팔았다 — 코스피 {idx['pct']:+.2f}%",
        "summary": [f"코스피는 {idx['close']:,.2f}로 {idx['pct']:+.2f}% 마감했습니다.",
                    "투자자별로는 " + ", ".join(f"{k} {_fmt(f[k])}" for k in INV) + "입니다."],
        "investors": inv, "stocks": stocks[:9],
        "watch": ["(AI 해설 비활성화: ANTHROPIC_API_KEY 설정 시 원인 분석이 추가됩니다)"],
        "_source": "rule",
    }


def commentary(d: dict) -> dict:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        try:
            return ai_commentary(d)
        except Exception as e:  # 실패해도 리포트는 발행
            print("AI commentary failed, fallback to rule:", repr(e))
    return rule_commentary(d)
