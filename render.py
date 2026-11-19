"""데이터 + 해설 -> 정적 HTML 리포트 (site/index.html, site/r/YYYYMMDD.html)."""
from __future__ import annotations

import json
from pathlib import Path

SITE = Path(__file__).parent / "site"

TEMPLATE = r"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>코스피 수급 브리핑 __DATE_LABEL__</title>
<meta name="description" content="__HEADLINE__">
<script src="https://cdn.jsdelivr.net/npm/plotly.js-basic-dist-min@2.35.2/plotly-basic.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{color-scheme:dark;--page:#0a0a0a;--surface:#141415;--card:rgba(255,255,255,.035);--ink:#f5f5f3;--ink2:#c9c8c2;--muted:#8a8984;
--grid:#2a2a2a;--axis:#3a3a3a;--ring:rgba(255,255,255,.10);--red:#e5322d;--red2:#a3121a;--gold:#e9b949;--green:#5fd38a;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--up:#ff5a52;--down:#4d9bff;--mono:"JetBrains Mono",ui-monospace,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font-family:"Noto Sans KR",system-ui,"Malgun Gothic",sans-serif;line-height:1.6;
background:radial-gradient(ellipse 60% 40% at 10% -5%,rgba(229,50,45,.30),transparent 70%),
radial-gradient(ellipse 50% 35% at 100% 0,rgba(229,50,45,.18),transparent 70%),
linear-gradient(90deg,rgba(110,0,0,.35),transparent 7%,transparent 93%,rgba(110,0,0,.35)),var(--page);background-attachment:fixed}
.wrap{max-width:1080px;margin:0 auto;padding:28px 16px 64px}
/* hero */
.hero{position:relative;display:grid;grid-template-columns:1.35fr 1fr;gap:16px;align-items:center;padding:8px 0 20px}
.confetti{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:0}
.hero>div:not(.confetti){position:relative;z-index:1}
.confetti i{position:absolute;width:10px;height:18px;border-radius:2px;opacity:.75}
.kicker{display:flex;align-items:center;gap:14px;font-family:var(--mono);font-size:13px;letter-spacing:.32em;color:var(--gold);font-weight:700}
.kicker .ln{flex:0 0 56px;height:1px;background:linear-gradient(90deg,transparent,var(--gold))}
.kicker .ln:last-child{background:linear-gradient(90deg,var(--gold),transparent)}
.big{font-weight:900;font-size:clamp(54px,10.5vw,108px);line-height:.98;letter-spacing:-.045em;margin:14px 0 18px}
.big span{color:var(--red)}
h1{font-size:clamp(22px,3.4vw,32px);font-weight:900;line-height:1.3;margin:0 0 8px;letter-spacing:-.02em}
.lede{margin:0 0 14px;color:var(--ink2);font-size:15px}.lede b{color:var(--ink)}
.pills{display:flex;gap:8px;flex-wrap:wrap}
.pill{display:inline-block;border-radius:999px;padding:6px 16px;font-size:14px;font-weight:700;background:#1d1d1f;border:1px solid var(--ring);color:var(--ink);text-decoration:none}
.pill.red{background:var(--red2);border-color:transparent}
/* medal */
.medalbox{position:relative;display:flex;justify-content:center;padding-top:40px}
.ribbon{position:absolute;top:0;width:70px;height:150px;background:linear-gradient(#7d0d12,#c4161c);z-index:0}
.ribbon.l{transform:translateX(-38px) skewX(18deg)}.ribbon.r{transform:translateX(38px) skewX(-18deg)}
.medal{position:relative;z-index:1;width:min(300px,72vw);aspect-ratio:1;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;
background:radial-gradient(circle at 35% 30%,#ffe6a3,#e9b949 45%,#b8862b 80%,#8e6420);box-shadow:0 20px 60px rgba(0,0,0,.6),inset 0 0 0 10px rgba(255,255,255,.12);color:#2a1d05;text-align:center}
.medal::before{content:"";position:absolute;inset:22px;border-radius:50%;border:2px dashed rgba(60,40,5,.45)}
.medal .t{font-family:var(--mono);font-size:13px;letter-spacing:.3em;font-weight:700}
.medal .v{font-size:clamp(34px,5vw,46px);font-weight:900;letter-spacing:-.03em;line-height:1.1;margin:4px 0}
.medal .c{font-size:18px;font-weight:900}
.medal .d{font-size:12px;margin-top:4px;opacity:.8}
/* investor cards */
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:8px}
.tile{border-radius:18px;padding:18px 20px;border:1px solid var(--ring);background:linear-gradient(135deg,#2a2f3a,#1b1e25);display:flex;align-items:center;gap:16px}
.tile.buy{background:linear-gradient(135deg,#c4161c,#7d0d12);border-color:transparent}
.tile .who{font-size:30px;font-weight:900;letter-spacing:-.03em;display:flex;align-items:center;gap:8px;white-space:nowrap}
.tile .val{font-size:22px;font-weight:900;line-height:1.2}
.tile .note{font-size:13px;color:rgba(255,255,255,.75)}
.dot{width:12px;height:12px;border-radius:3px;display:inline-block;flex:none;box-shadow:0 0 0 2px rgba(255,255,255,.25)}
.up{color:var(--up)}.down{color:var(--down)}
/* cards */
.card{background:var(--card);border:1px solid var(--ring);border-radius:18px;padding:20px;margin-top:16px;backdrop-filter:blur(2px)}
.lab{font-family:var(--mono);font-size:12px;letter-spacing:.22em;color:var(--red);font-weight:700}
.card h2{font-size:22px;font-weight:900;margin:2px 0 12px;letter-spacing:-.02em}
.sub{font-size:13px;color:var(--muted);margin:-6px 0 12px}
/* terminal */
.term{padding:0;overflow:hidden}
.term .bar{display:flex;gap:8px;padding:12px 16px;border-bottom:1px solid var(--ring)}
.term .bar i{width:12px;height:12px;border-radius:50%;background:#555}.term .bar i:first-child{background:var(--red)}
.term .body{padding:16px 20px;font-size:15px}
.term .ln{margin:6px 0;display:flex;gap:10px}.term .ln::before{content:">";color:var(--red);font-family:var(--mono);font-weight:700}
.term .ok{color:var(--green);font-size:14px;margin-top:10px}
.term .cur{display:inline-block;width:10px;height:18px;background:var(--red);vertical-align:-3px;margin-left:4px;animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){.term .cur{animation:none}}
.inv{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.inv .box{border:1px solid var(--ring);border-radius:14px;padding:14px;background:rgba(0,0,0,.25)}
.inv .box b{display:flex;align-items:center;gap:8px;font-size:17px}
.inv .one{font-weight:700;margin:8px 0 4px;color:var(--gold)}
.inv .why{font-size:14px;color:var(--ink2)}
.tabs{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.tabs button{border:1px solid var(--ring);background:#1d1d1f;color:var(--ink);border-radius:999px;padding:7px 18px;font:inherit;font-size:14px;font-weight:700;cursor:pointer}
.tabs button[aria-selected="true"]{background:var(--red2);border-color:transparent}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.chart{width:100%;height:360px}.chart.sm{height:220px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px;border-bottom:1px solid var(--grid);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--ink2);font-weight:700;cursor:pointer;user-select:none}
tbody tr:hover{background:rgba(255,255,255,.04)}
.tblwrap{overflow-x:auto}
.stocks{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.stocks .s{border:1px solid var(--ring);border-radius:14px;padding:12px 14px;background:rgba(0,0,0,.25)}
.stocks .who{font-size:12px;color:var(--gold);font-weight:700;margin-top:2px}
.stocks .why{font-size:14px;color:var(--ink2)}
.mv{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pill.slate{background:linear-gradient(135deg,#3a4150,#262b35);border-color:transparent}
.m{display:flex;gap:14px;align-items:flex-start;border:1px solid var(--ring);border-radius:14px;padding:12px 14px;margin-top:10px;background:rgba(0,0,0,.25)}
.m .rk{font-size:30px;font-weight:900;line-height:1;width:28px;flex:none;color:var(--gold)}
.m .top{display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.m .top b{font-size:17px}.m .pct{font-size:20px;font-weight:900;white-space:nowrap}
.m .meta{font-size:12px;color:var(--muted);margin:2px 0 4px}.m .why{font-size:14px;color:var(--ink2)}.m .mb{flex:1;min-width:0}
.watch{margin:0;padding:0;list-style:none}.watch li{margin:8px 0;padding-left:26px;position:relative}
.watch li::before{content:"★";position:absolute;left:0;color:var(--gold)}
footer{margin-top:24px;font-size:12px;color:var(--muted);border-top:1px solid var(--ring);padding-top:16px}
footer .star{color:var(--gold);font-weight:700;font-size:13px;margin-bottom:6px}
@media (max-width:760px){.hero{grid-template-columns:1fr}.medalbox{order:-1;padding-top:30px}.medal{width:220px}
.tiles,.inv,.two,.stocks,.mv{grid-template-columns:1fr}.tile .who{font-size:26px}.kicker{letter-spacing:.16em;font-size:12px;gap:10px}.kicker .ln{flex-basis:28px}.chart{height:320px}}
</style></head>
<body><div class="wrap">
<header class="hero">
 <div class="confetti" aria-hidden="true" id="confetti"></div>
 <div>
  <div class="kicker"><span class="ln"></span>KOSPI FLOW · DAILY 07:00<span class="ln"></span></div>
  <div class="big"><span>K</span>ospi<br><span>F</span>low<br><span>B</span>riefing</div>
  <h1 id="headline"></h1>
  <p class="lede">전일 코스피, <b>누가 사고 누가 팔았나.</b> 개인·외국인·기관 수급과 그 이유를 매일 아침 7시에.</p>
  <div class="pills"><span class="pill red" id="dlabel"></span><a class="pill" href="#flow">수급 흐름</a><a class="pill" href="#movers">급등·급락</a><a class="pill" href="#top">상위 종목</a><a class="pill" href="archive.html">지난 리포트</a></div>
 </div>
 <div class="medalbox"><div class="ribbon l"></div><div class="ribbon r"></div><div class="medal" id="medal"></div></div>
</header>

<div class="tiles" id="tiles"></div>

<div class="card term"><div class="bar"><i></i><i></i><i></i></div><div class="body" id="summary"></div></div>

<div class="card"><div class="lab">WHO</div><h2>누가 사고, 누가 팔았나</h2><div class="inv" id="inv"></div></div>

<div class="card" id="flow">
 <div class="lab">20-DAY FLOW</div><h2>최근 20거래일 수급 흐름</h2>
 <p class="sub">위: 코스피 종가 · 아래: 투자자별 누적 순매수(억원)</p>
 <div id="cIdx" class="chart sm"></div>
 <div id="cCum" class="chart"></div>
</div>

<div class="card" id="top">
 <div class="lab">TOP 10</div><h2>투자자별 순매수·순매도 상위 종목</h2>
 <p class="sub">코스피 시가총액 상위 100종목 · 순매수 수량 × 종가로 추정한 금액(억원)</p>
 <div class="tabs" role="tablist" id="tabs"></div>
 <div class="two"><div id="cBuy" class="chart"></div><div id="cSell" class="chart"></div></div>
</div>

<div class="card" id="movers"><div class="lab">HOT MOVERS</div><h2>주목해봐야 할 종목 · 급등·급락 TOP 5</h2>
 <p class="sub">코스피 전체 · 일반주식 · 거래대금 30억 원 이상 · <span id="mvDate"></span></p>
 <div class="mv"><div><span class="pill red">급등 TOP 5</span><div id="mvUp"></div></div><div><span class="pill slate">급락 TOP 5</span><div id="mvDown"></div></div></div>
</div>

<div class="card"><div class="lab">WHY</div><h2>수급 주목 종목과 이유</h2><div class="stocks" id="stocks"></div></div>

<div class="card"><div class="lab">WATCH</div><h2>오늘 장 체크포인트</h2><ul class="watch" id="watch"></ul></div>

<div class="card">
 <div class="lab">TABLE</div><h2>시총 상위 100종목 수급표</h2>
 <p class="sub">열 제목을 누르면 정렬됩니다 · 단위 억원</p>
 <div class="tblwrap"><table id="tbl"></table></div>
</div>

<footer id="foot"></footer>
</div>
<script>
const D = __DATA__;
const C = __COMMENT__;
const INV = ["외국인","기관","개인"];
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const COL = () => ({"외국인":css("--s1"),"기관":css("--s2"),"개인":css("--s3")});
const fmt = v => (v>0?"+":"")+Math.round(v).toLocaleString("ko-KR");
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const dl = d => `${d.slice(0,4)}.${d.slice(4,6)}.${d.slice(6)}`;
const S = Object.fromEntries(D.stocks.map(s=>[s.code,s]));

document.getElementById("headline").textContent = C.headline;
document.getElementById("dlabel").textContent = dl(D.date)+" 기준";
const ix = D.index, cls = ix.pct>=0?"up":"down", arr = ix.pct>=0?"▲":"▼";
document.getElementById("medal").innerHTML = `<div class="t">KOSPI</div><div class="v">${ix.close.toLocaleString("ko-KR",{minimumFractionDigits:2})}</div>
<div class="c">${arr} ${Math.abs(ix.close-ix.prev).toFixed(2)} (${ix.pct>=0?"+":""}${ix.pct.toFixed(2)}%)</div><div class="d">${dl(D.date)} 종가</div>`;
document.getElementById("tiles").innerHTML = INV.map((k,i)=>{const v=D.flow_today[k];return `<div class="tile ${v>=0?"buy":""}">
<div class="who"><span class="dot" style="background:var(--s${i+1})"></span>${k}</div>
<div><div class="val">${fmt(v)}억</div><div class="note">${v>=0?"순매수":"순매도"}</div></div></div>`}).join("");
document.getElementById("summary").innerHTML = C.summary.map(s=>`<div class="ln"><span>${esc(s)}</span></div>`).join("")+
 `<div class="ok">✓ ${C._source==="ai"?"Claude가 뉴스·웹검색을 근거로 해설을 작성했어요.":"기본 요약을 만들었어요. (AI 해설은 API 키 설정 후)"}<span class="cur"></span></div>`;
(()=>{const cf=document.getElementById("confetti"),cs=["var(--red)","var(--gold)","#9a9a9a","#7d0d12"];let h="";
 for(let i=0;i<16;i++){const x=(i*61)%100,y=(i*37)%85,r=(i*47)%180,c=cs[i%4],s=.6+(i%3)*.25;
  h+=`<i style="left:${x}%;top:${y}%;transform:rotate(${r}deg) scale(${s});background:${c}"></i>`}cf.innerHTML=h})();
document.getElementById("inv").innerHTML = INV.map((k,i)=>{const x=C.investors[k]||{};return `<div class="box">
<b><span class="dot" style="background:var(--s${i+1})"></span>${k} · ${esc(x.stance)}</b><div class="one">${esc(x.one_line)}</div><div class="why">${esc(x.why)}</div></div>`}).join("");
document.getElementById("stocks").innerHTML = (C.stocks||[]).map(s=>{const x=S[s.code];const p=x?`<span class="${x.pct>=0?"up":"down"}">${x.pct>=0?"▲":"▼"}${Math.abs(x.pct).toFixed(2)}%</span>`:"";
return `<div class="s"><b>${esc(s.name)}</b> ${p}<div class="who">${esc(s.who)}</div><div class="why">${esc(s.why)}</div></div>`}).join("");
(()=>{const mv=D.movers||{up:[],down:[]},W=Object.fromEntries((C.movers||[]).map(m=>[m.code,m.why]));
 if(!mv.up.length&&!mv.down.length){document.getElementById("movers").style.display="none";return}
 document.getElementById("mvDate").textContent=dl(D.date)+" 종가 기준";
 const card=(m,i)=>{const up=m.pct>=0,fl=INV.filter(k=>k in m).map(k=>`${k[0]} ${Math.abs(m[k])<10?(m[k]>0?"+":"")+m[k].toFixed(1):fmt(m[k])}`).join(" / ");
  return `<div class="m"><div class="rk">${i+1}</div><div class="mb"><div class="top"><b>${esc(m.name)}</b><span class="pct ${up?"up":"down"}">${up?"▲":"▼"}${Math.abs(m.pct).toFixed(2)}%</span></div>
  <div class="meta">${m.close.toLocaleString("ko-KR")}원 · 거래대금 ${m.tv.toLocaleString("ko-KR")}억${fl?` · ${fl}억`:""}</div><div class="why">${esc(W[m.code]||"-")}</div></div></div>`};
 document.getElementById("mvUp").innerHTML=mv.up.map(card).join("");document.getElementById("mvDown").innerHTML=mv.down.map(card).join("");})();
document.getElementById("watch").innerHTML = (C.watch||[]).map(s=>`<li>${esc(s)}</li>`).join("");
document.getElementById("foot").innerHTML = `<div class="star">★ 매일 아침 07:00 자동 갱신 · 데이터 수집부터 해설까지 Claude Code로 만들었습니다</div>데이터: 네이버페이 증권(KRX 집계) · 종목별 금액은 순매수 수량×종가 추정치 · 해설: ${C._source==="ai"?"Claude AI 자동 생성(웹검색 근거)":"규칙 기반 자동 생성"} · 생성 ${esc(D.generated_at)}<br>본 자료는 정보 제공 목적이며 투자 권유가 아닙니다.`;

function layout(extra){return Object.assign({paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",
 font:{family:"system-ui,'Malgun Gothic',sans-serif",color:css("--ink2"),size:12},margin:{l:56,r:16,t:8,b:32},
 hoverlabel:{bgcolor:css("--surface"),bordercolor:css("--axis"),font:{color:css("--ink")}},showlegend:false},extra)}
const ax = o => Object.assign({type:"category",gridcolor:css("--grid"),linecolor:css("--axis"),zerolinecolor:css("--axis"),tickfont:{color:css("--muted")},fixedrange:true},o);
const cfg = {displayModeBar:false,responsive:true};

function drawFlow(){
 const md = d=>`${+d.slice(4,6)}/${+d.slice(6)}`; const xs = D.index.chart.map(r=>md(r.d));
 Plotly.react("cIdx",[{x:xs,y:D.index.chart.map(r=>r.c),type:"scatter",mode:"lines",line:{color:css("--ink2"),width:2},
  hovertemplate:"%{x}<br>코스피 %{y:,.2f}<extra></extra>"}],layout({hovermode:"x unified",xaxis:ax({showgrid:false,tickangle:0,nticks:innerWidth<600?4:7}),yaxis:ax({type:"linear",tickformat:",.0f"})}),cfg);
 const fx = D.flow_hist.map(r=>md(r.date)), col=COL();
 const tr = INV.map(k=>{let c=0;const ys=D.flow_hist.map(r=>c+=r[k]);return {x:fx,y:ys,name:k,type:"scatter",mode:"lines",
  line:{color:col[k],width:2},marker:{size:8,color:col[k],line:{color:css("--surface"),width:2}},
  hovertemplate:`${k} 누적 %{y:,.0f}억<extra></extra>`}});
 const ann = tr.map(t=>({xref:"paper",x:1,y:t.y.at(-1),text:`${t.name} ${fmt(t.y.at(-1))}`,showarrow:false,xanchor:"left",xshift:6,font:{color:css("--ink"),size:12}}));
 const nw = innerWidth<600; ann.forEach(a=>a.font.size=nw?11:12);
 Plotly.react("cCum",tr,layout({hovermode:"x unified",margin:{l:nw?74:72,r:nw?104:120,t:30,b:32},annotations:ann,showlegend:true,
  legend:{orientation:"h",xref:"container",yref:"container",x:0,y:1,yanchor:"top",font:{color:css("--ink2")}},xaxis:ax({showgrid:false,tickangle:0,nticks:nw?4:7}),yaxis:ax({type:"linear",tickformat:",.0f",ticksuffix:"억"})}),cfg);
}
let cur = "외국인";
function drawRank(){
 const col = COL()[cur];
 [["buy","cBuy","순매수 상위"],["sell","cSell","순매도 상위"]].forEach(([side,id,title])=>{
  const items = D.ranks[cur][side].map(c=>S[c]).reverse();
  Plotly.react(id,[{type:"bar",orientation:"h",y:items.map(s=>s.name),x:items.map(s=>Math.abs(s[cur])),marker:{color:col,line:{color:css("--surface"),width:2}},
   text:items.map(s=>fmt(s[cur])),textposition:"outside",cliponaxis:false,textfont:{color:css("--ink2")},
   customdata:items.map(s=>[s.pct,s["외국인"],s["기관"],s["개인"]]),
   hovertemplate:"<b>%{y}</b> (%{customdata[0]:+.2f}%)<br>외국인 %{customdata[1]:+,.0f}억<br>기관 %{customdata[2]:+,.0f}억<br>개인 %{customdata[3]:+,.0f}억<extra></extra>"}],
   layout({title:{text:`${cur} ${title}`,font:{size:14,color:css("--ink")},x:0,y:.98},margin:{l:110,r:56,t:32,b:28},
   xaxis:ax({type:"linear",tickformat:",.0f",zeroline:true}),yaxis:ax({showgrid:false,tickfont:{color:css("--ink2")}}),bargap:.35}),cfg);
 });
 document.querySelectorAll("#tabs button").forEach(b=>b.setAttribute("aria-selected",b.dataset.k===cur));
}
document.getElementById("tabs").innerHTML = INV.map(k=>`<button role="tab" data-k="${k}">${k}</button>`).join("");
document.getElementById("tabs").onclick = e=>{if(e.target.dataset.k){cur=e.target.dataset.k;drawRank()}};

let sortK="외국인", sortD=-1;
function drawTable(){
 const cols=[["name","종목"],["pct","등락률"],["외국인","외국인"],["기관","기관"],["개인","개인"],["외국인지분","외국인지분"]];
 const rows=[...D.stocks].sort((a,b)=>{const x=a[sortK],y=b[sortK];return (typeof x==="string"?x.localeCompare(y):x-y)*sortD});
 document.getElementById("tbl").innerHTML = "<thead><tr>"+cols.map(([k,l])=>`<th data-k="${k}">${l}${k===sortK?(sortD<0?" ▼":" ▲"):""}</th>`).join("")+"</tr></thead><tbody>"+
  rows.map(s=>`<tr><td>${esc(s.name)}</td><td class="${s.pct>=0?"up":"down"}">${s.pct>=0?"+":""}${s.pct.toFixed(2)}%</td>${INV.map(k=>`<td>${fmt(s[k])}</td>`).join("")}<td>${esc(s["외국인지분"]||"")}</td></tr>`).join("")+"</tbody>";
}
document.getElementById("tbl").onclick = e=>{const k=e.target.dataset?.k;if(!k)return;sortD = k===sortK?-sortD:-1;sortK=k;drawTable()};
function drawAll(){drawFlow();drawRank();drawTable()}
drawAll();

</script></body></html>"""

ARCHIVE = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>수급 브리핑 아카이브</title><style>
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--muted:#898781;--ring:rgba(11,11,11,.10)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ring:rgba(255,255,255,.10)}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ring:rgba(255,255,255,.10)}
body{margin:0;background:var(--page);color:var(--ink);font-family:system-ui,"Malgun Gothic",sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:24px 16px}a{color:inherit;text-decoration:none}
li{list-style:none;background:var(--surface);border:1px solid var(--ring);border-radius:12px;padding:12px 14px;margin:8px 0}
.d{font-size:13px;color:var(--muted)}ul{padding:0}</style></head><body><div class="wrap">
<h1>KOSPI 수급 브리핑 아카이브</h1><p><a href="index.html">← 최신 리포트</a></p><ul>__ITEMS__</ul></div></body></html>"""


def _js(o) -> str:
    return json.dumps(o, ensure_ascii=False).replace("</", "<\\/")


def render(data: dict, comment: dict) -> Path:
    d = data["date"]
    label = f"{d[:4]}.{d[4:6]}.{d[6:]}"
    html = (TEMPLATE.replace("__DATA__", _js(data)).replace("__COMMENT__", _js(comment))
            .replace("__DATE_LABEL__", label)
            .replace("__HEADLINE__", comment.get("headline", "").replace('"', "'")))
    (SITE / "r").mkdir(parents=True, exist_ok=True)
    (SITE / "r" / f"{d}.html").write_text(html, encoding="utf-8")
    (SITE / "index.html").write_text(html, encoding="utf-8")

    # 아카이브 목록
    idx_path = SITE / "archive.json"
    items = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else []
    items = [i for i in items if i["date"] != d] + [{"date": d, "headline": comment.get("headline", "")}]
    items.sort(key=lambda i: i["date"], reverse=True)
    idx_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    lis = "".join(f'<li><a href="r/{i["date"]}.html"><div class="d">{i["date"][:4]}.{i["date"][4:6]}.{i["date"][6:]}</div>'
                  f'{i["headline"]}</a></li>' for i in items)
    (SITE / "archive.html").write_text(ARCHIVE.replace("__ITEMS__", lis), encoding="utf-8")
    return SITE / "index.html"
