"""매일 아침 실행: 수집 -> AI 해설 -> HTML 생성.

사용법:  python main.py [YYYYMMDD]   (날짜 생략 시 마지막 거래일)
"""
import sys

from analyze import commentary
from collect import collect
from render import render

if __name__ == "__main__":
    data = collect(sys.argv[1] if len(sys.argv) > 1 else None)
    comment = commentary(data)
    out = render(data, comment)
    print(f"[{data['date']}] {comment['headline']} ({comment['_source']}) -> {out}")
