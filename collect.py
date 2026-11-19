"""KOSPI 투자자별 수급 데이터 수집 (네이버페이 증권 공개 API, 로그인 불필요).

- 코스피 지수: 개인/외국인/기관 순매수(억원), 최근 N거래일
- 시총 상위 종목: 종목별 개인/외국인/기관 순매수 수량 -> 금액(억원, 종가 기준 추정)
- 뉴스: 수급 상위 종목 헤드라인 + 증시 주요뉴스 (AI 해설 근거)
"""
from __future__ import annotations

import html
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

import requests

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.stock.naver.com/"}
M = "https://m.stock.naver.com/api"
DATA = Path(__file__).parent / "data"


def get(url: str, retries: int = 3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=H, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1 + i)


def num(s) -> float:
    if s is None:
        return 0.0
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).replace(",", "").replace("%", "").replace("+", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def last_trading_date() -> str:
    """확정된 마지막 거래일 (장중에는 전일). 삼성전자 일별 수급의 최신 일자로 판단."""
    rows = get(f"{M}/stock/005930/trend")
    return rows[0]["bizdate"]


def index_chart(code: str, end: str, days: int = 45) -> list[dict]:
    e = datetime.strptime(end, "%Y%m%d")
    s = e - timedelta(days=days)
    url = (f"https://api.stock.naver.com/chart/domestic/index/{code}/day"
           f"?startDateTime={s:%Y%m%d}0000&endDateTime={e:%Y%m%d}2359")
    return [r for r in get(url) if r["localDate"] <= end]


def index_flow(code: str, date: str) -> dict:
    r = get(f"{M}/index/{code}/trend?bizdate={date}")
    return {"date": r["bizdate"], "개인": num(r["personalValue"]),
            "외국인": num(r["foreignValue"]), "기관": num(r["institutionalValue"])}


def universe(n: int = 100) -> list[dict]:
    out, page = [], 1
    while len(out) < n:
        js = get(f"{M}/stocks/marketValue/KOSPI?page={page}&pageSize=50")
        stocks = js.get("stocks", [])
        if not stocks:
            break
        for s in stocks:
            if s.get("stockEndType") == "stock":
                out.append({"code": s["itemCode"], "name": s["stockName"],
                            "mcap": num(s.get("marketValue"))})  # 억원
        page += 1
    return out[:n]


def stock_flow(stock: dict, date: str) -> dict | None:
    rows = get(f"{M}/stock/{stock['code']}/trend")
    row = next((r for r in rows if r["bizdate"] == date), None)
    if not row:
        return None
    close = num(row["closePrice"])
    chg = num(row["compareToPreviousClosePrice"])
    if row.get("compareToPreviousPrice", {}).get("name") in ("FALLING", "LOWER_LIMIT"):
        chg = -abs(chg)
    prev = close - chg
    to_eok = close / 1e8
    return {**stock, "close": close,
            "pct": round(chg / prev * 100, 2) if prev else 0.0,
            "개인": round(num(row["individualPureBuyQuant"]) * to_eok, 1),
            "외국인": round(num(row["foreignerPureBuyQuant"]) * to_eok, 1),
            "기관": round(num(row["organPureBuyQuant"]) * to_eok, 1),
            "외국인지분": row.get("foreignerHoldRatio")}


def stock_news(code: str, n: int = 3) -> list[str]:
    try:
        js = get(f"{M}/news/stock/{code}?pageSize={n}&page=1")
        items = [it for grp in js for it in grp.get("items", [])]
        return [html.unescape(it.get("titleFull") or it.get("title") or "") for it in items[:n]]
    except Exception:
        return []


def main_news(n: int = 15) -> list[dict]:
    try:
        js = get(f"{M}/news/list?category=mainnews&pageSize={n}&page=1")
        return [{"title": html.unescape(a.get("tit") or ""), "summary": html.unescape(a.get("subcontent") or "")[:160],
                 "office": a.get("ohnm"), "dt": a.get("dt")} for a in js]
    except Exception:
        return []


def collect(date: str | None = None, top_n: int = 100, hist_days: int = 20) -> dict:
    date = date or last_trading_date()
    chart = index_chart("KOSPI", date)
    hist_dates = [r["localDate"] for r in chart][-hist_days:]

    with ThreadPoolExecutor(8) as ex:
        flows = list(ex.map(lambda d: index_flow("KOSPI", d), hist_dates))
        uni = universe(top_n)
        stocks = [s for s in ex.map(lambda s: stock_flow(s, date), uni) if s]

    # 투자자별 순매수/순매도 상위
    ranks = {}
    for inv in ("외국인", "기관", "개인"):
        srt = sorted(stocks, key=lambda s: s[inv], reverse=True)
        ranks[inv] = {"buy": [s["code"] for s in srt[:10]],
                      "sell": [s["code"] for s in srt[::-1][:10]]}

    # 뉴스: 각 투자자 상위 5개 종목 + 등락 상위
    focus = set()
    for r in ranks.values():
        focus.update(r["buy"][:5] + r["sell"][:5])
    focus.update(s["code"] for s in sorted(stocks, key=lambda s: abs(s["pct"]), reverse=True)[:5])
    with ThreadPoolExecutor(8) as ex:
        news = dict(zip(focus, ex.map(stock_news, focus)))

    last = chart[-1]
    prev_close = chart[-2]["closePrice"] if len(chart) > 1 else last["closePrice"]
    data = {
        "date": date,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "index": {"close": last["closePrice"], "prev": prev_close,
                  "pct": round((last["closePrice"] / prev_close - 1) * 100, 2),
                  "high": last["highPrice"], "low": last["lowPrice"],
                  "chart": [{"d": r["localDate"], "c": r["closePrice"]} for r in chart[-hist_days:]]},
        "flow_today": next((f for f in flows if f["date"] == date), flows[-1]),
        "flow_hist": flows,
        "stocks": stocks,
        "ranks": ranks,
        "stock_news": news,
        "market_news": main_news(),
    }
    DATA.mkdir(exist_ok=True)
    (DATA / f"{date}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


if __name__ == "__main__":
    import sys
    d = collect(sys.argv[1] if len(sys.argv) > 1 else None)
    print(d["date"], d["index"], d["flow_today"], len(d["stocks"]), "stocks")
