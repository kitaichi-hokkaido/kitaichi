#!/usr/bin/env python3
"""Regenerate dashboard/cf_dashboard.html from data/cf_tracking.csv.

Run this after appending today's row(s) to data/cf_tracking.csv:
    python3 scripts/build_dashboard.py

The output is a single self-contained HTML file (data embedded as JSON)
suitable for publishing as-is via the Artifact tool.
"""
import csv
import json
import os
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "cf_tracking.csv")
OUT_PATH = os.path.join(ROOT, "dashboard", "cf_dashboard.html")


def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def build_campaigns(rows):
    by_row = defaultdict(list)
    for r in rows:
        by_row[r["row_no"]].append(r)

    campaigns = []
    for row_no, entries in by_row.items():
        entries.sort(key=lambda r: r["date"])
        latest = entries[-1]
        history = [
            {
                "date": e["date"],
                "amount": to_num(e["support_amount"]),
                "supporters": to_num(e["supporter_count"]),
            }
            for e in entries
        ]
        prev = entries[-2] if len(entries) > 1 else None
        campaigns.append(
            {
                "row_no": row_no,
                "name": latest["project_name"],
                "site": latest["site"],
                "url": latest["url"],
                "period_start": latest["period_start"],
                "period_end": latest["period_end"],
                "target_amount": to_num(latest["target_amount"]),
                "amount": to_num(latest["support_amount"]),
                "supporters": to_num(latest["supporter_count"]),
                "prev_amount": to_num(prev["support_amount"]) if prev else None,
                "prev_supporters": to_num(prev["supporter_count"]) if prev else None,
                "note": latest["note"],
                "history": history,
            }
        )
    campaigns.sort(key=lambda c: (c["period_end"] or "9999-99-99"))
    return campaigns


TEMPLATE = """<!doctype html>
<title>CFウォッチ</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #eeeeea;
    --surface: #ffffff;
    --surface-2: #f5f4f0;
    --border: #dedcd4;
    --ink: #201f1c;
    --ink-secondary: #63615a;
    --ink-muted: #8b887f;
    --accent-amount: #0f6e63;
    --accent-amount-fill: rgba(15, 110, 99, 0.14);
    --accent-supporters: #7a5c8e;
    --status-good: #2f8f5b;
    --status-warning: #c2831a;
    --status-critical: #b23b3b;
    --status-good-bg: rgba(47, 143, 91, 0.12);
    --status-warning-bg: rgba(194, 131, 26, 0.12);
    --status-critical-bg: rgba(178, 59, 59, 0.12);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #14161a;
      --surface: #1b1e23;
      --surface-2: #21252b;
      --border: #2c3036;
      --ink: #e7e5df;
      --ink-secondary: #a6a398;
      --ink-muted: #767468;
      --accent-amount: #3fb5a4;
      --accent-amount-fill: rgba(63, 181, 164, 0.16);
      --accent-supporters: #b79bcb;
      --status-good: #4caf77;
      --status-warning: #e0a542;
      --status-critical: #e0615f;
      --status-good-bg: rgba(76, 175, 119, 0.14);
      --status-warning-bg: rgba(224, 165, 66, 0.14);
      --status-critical-bg: rgba(224, 97, 95, 0.14);
    }
  }
  :root[data-theme="dark"] {
    --bg: #14161a;
    --surface: #1b1e23;
    --surface-2: #21252b;
    --border: #2c3036;
    --ink: #e7e5df;
    --ink-secondary: #a6a398;
    --ink-muted: #767468;
    --accent-amount: #3fb5a4;
    --accent-amount-fill: rgba(63, 181, 164, 0.16);
    --accent-supporters: #b79bcb;
    --status-good: #4caf77;
    --status-warning: #e0a542;
    --status-critical: #e0615f;
    --status-good-bg: rgba(76, 175, 119, 0.14);
    --status-warning-bg: rgba(224, 165, 66, 0.14);
    --status-critical-bg: rgba(224, 97, 95, 0.14);
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: "Zen Kaku Gothic New", "Hiragino Kaku Gothic ProN", sans-serif;
    line-height: 1.6;
  }
  .wrap {
    max-width: 1180px;
    margin: 0 auto;
    padding: 40px 24px 80px;
  }
  header.page {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px 24px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 24px;
    margin-bottom: 28px;
  }
  h1 {
    font-family: "Shippori Mincho", "Hiragino Mincho ProN", serif;
    font-weight: 700;
    font-size: 1.9rem;
    margin: 0;
    text-wrap: balance;
    letter-spacing: 0.01em;
  }
  .updated {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.85rem;
    color: var(--ink-secondary);
  }
  .summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 36px;
  }
  .summary .stat {
    background: var(--surface);
    padding: 18px 20px;
  }
  .summary .label {
    font-size: 0.78rem;
    color: var(--ink-muted);
    letter-spacing: 0.04em;
  }
  .summary .value {
    font-family: "IBM Plex Mono", monospace;
    font-variant-numeric: tabular-nums;
    font-size: 1.5rem;
    font-weight: 600;
    margin-top: 4px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 18px;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }
  .badge {
    display: inline-block;
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--surface-2);
    color: var(--ink-secondary);
    border: 1px solid var(--border);
    white-space: nowrap;
  }
  .card h2 {
    font-family: "Shippori Mincho", "Hiragino Mincho ProN", serif;
    font-size: 1.05rem;
    font-weight: 500;
    margin: 2px 0 0;
    text-wrap: balance;
  }
  a.card-link { color: inherit; text-decoration: none; }
  a.card-link h2 { text-decoration: underline; text-decoration-color: var(--border); text-underline-offset: 3px; }
  a.card-link:hover h2 { text-decoration-color: var(--accent-amount); }
  .period {
    font-size: 0.78rem;
    color: var(--ink-muted);
    font-family: "IBM Plex Mono", monospace;
  }
  .status-chip {
    font-size: 0.72rem;
    padding: 2px 9px;
    border-radius: 999px;
    font-weight: 500;
    white-space: nowrap;
  }
  .status-good { color: var(--status-good); background: var(--status-good-bg); }
  .status-warning { color: var(--status-warning); background: var(--status-warning-bg); }
  .status-critical { color: var(--status-critical); background: var(--status-critical-bg); }
  .status-neutral { color: var(--ink-muted); background: var(--surface-2); }

  .stat-row {
    display: flex;
    gap: 22px;
  }
  .stat-block .label {
    font-size: 0.75rem;
    color: var(--ink-muted);
  }
  .stat-block .amount {
    font-family: "IBM Plex Mono", monospace;
    font-variant-numeric: tabular-nums;
    font-size: 1.35rem;
    font-weight: 600;
  }
  .stat-block.amount-block .amount { color: var(--accent-amount); }
  .stat-block.supporters-block .amount { color: var(--accent-supporters); }
  .delta {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.75rem;
    color: var(--ink-secondary);
  }
  .delta.up::before { content: "+"; }

  .bar-track {
    height: 6px;
    border-radius: 999px;
    background: var(--surface-2);
    overflow: hidden;
  }
  .bar-fill { height: 100%; background: var(--accent-amount); border-radius: 999px; }
  .bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: var(--ink-muted);
    font-family: "IBM Plex Mono", monospace;
  }

  .spark { width: 100%; height: 56px; display: block; }
  .spark-empty {
    font-size: 0.75rem;
    color: var(--ink-muted);
    padding: 8px 0;
  }

  .note {
    font-size: 0.75rem;
    color: var(--status-critical);
    background: var(--status-critical-bg);
    border-radius: 8px;
    padding: 6px 10px;
  }

  footer {
    margin-top: 44px;
    font-size: 0.78rem;
    color: var(--ink-muted);
  }
</style>
<div class="wrap">
  <header class="page">
    <h1>クラウドファンディング支援状況ダッシュボード</h1>
    <div class="updated">最終更新: __LAST_UPDATED__</div>
  </header>

  <div class="summary" id="summary"></div>
  <div class="grid" id="grid"></div>

  <footer>
    対象: スプレッドシート「CFリスト＆実施者リスト」で公開期間中の案件。毎日1回、各サイトの公開ページから支援金額・支援者数を取得して記録しています。
  </footer>
</div>

<script>
const CAMPAIGNS = __CAMPAIGNS_JSON__;
const TODAY = "__TODAY__";

function yen(n) {
  if (n === null || n === undefined) return "—";
  return "¥" + Math.round(n).toLocaleString("ja-JP");
}
function num(n) {
  if (n === null || n === undefined) return "—";
  return Math.round(n).toLocaleString("ja-JP");
}
function deltaStr(cur, prev, unit) {
  if (cur === null || cur === undefined) return null;
  if (prev === null || prev === undefined) return "初日";
  const d = cur - prev;
  if (d === 0) return "前日比 ±0" + unit;
  const sign = d > 0 ? "+" : "";
  return "前日比 " + sign + Math.round(d).toLocaleString("ja-JP") + unit;
}
function daysLeft(endStr) {
  if (!endStr) return null;
  const end = new Date(endStr + "T23:59:59");
  const today = new Date(TODAY + "T00:00:00");
  return Math.ceil((end - today) / 86400000);
}
function statusFor(c) {
  const left = daysLeft(c.period_end);
  if (c.amount === null) return { cls: "status-neutral", label: "データ取得不可" };
  if (c.target_amount) {
    const pct = c.amount / c.target_amount;
    if (pct >= 1) return { cls: "status-good", label: "達成" };
    if (left !== null && left <= 7 && pct < 0.7) return { cls: "status-critical", label: "残り" + left + "日・要テコ入れ" };
    if (pct >= 0.7) return { cls: "status-good", label: "順調" };
    if (pct >= 0.35) return { cls: "status-warning", label: "推進中" };
    return { cls: "status-warning", label: "伸び悩み" };
  }
  if (left !== null) return { cls: "status-neutral", label: "残り" + left + "日" };
  return { cls: "status-neutral", label: "公開中" };
}

function sparkline(history, color, fill) {
  const pts = history.filter(h => h.amount !== null);
  if (pts.length < 2) {
    return '<div class="spark-empty">日次データが2日分たまるとグラフを表示します</div>';
  }
  const w = 280, h = 56, pad = 6;
  const vals = pts.map(p => p.amount);
  const min = Math.min(...vals, 0);
  const max = Math.max(...vals, 1);
  const range = (max - min) || 1;
  const x = i => pad + (i / (pts.length - 1)) * (w - pad * 2);
  const y = v => h - pad - ((v - min) / range) * (h - pad * 2);
  const coords = pts.map((p, i) => [x(i), y(p.amount)]);
  const line = coords.map((p, i) => (i === 0 ? "M" : "L") + p[0].toFixed(1) + "," + p[1].toFixed(1)).join(" ");
  const area = line + ` L${coords[coords.length - 1][0].toFixed(1)},${h - pad} L${coords[0][0].toFixed(1)},${h - pad} Z`;
  const last = coords[coords.length - 1];
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="支援金額の推移">
    <path d="${area}" fill="${fill}" stroke="none"></path>
    <path d="${line}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
    <circle cx="${last[0].toFixed(1)}" cy="${last[1].toFixed(1)}" r="3.2" fill="${color}"></circle>
  </svg>`;
}

function renderSummary() {
  const withData = CAMPAIGNS.filter(c => c.amount !== null);
  const totalAmount = withData.reduce((s, c) => s + c.amount, 0);
  const totalSupporters = withData.reduce((s, c) => s + (c.supporters || 0), 0);
  const el = document.getElementById("summary");
  el.innerHTML = `
    <div class="stat"><div class="label">公開中プロジェクト</div><div class="value">${CAMPAIGNS.length}件</div></div>
    <div class="stat"><div class="label">支援金額 合計</div><div class="value">${yen(totalAmount)}</div></div>
    <div class="stat"><div class="label">支援者数 合計</div><div class="value">${num(totalSupporters)}人</div></div>
  `;
}

function renderCards() {
  const grid = document.getElementById("grid");
  grid.innerHTML = CAMPAIGNS.map(c => {
    const st = statusFor(c);
    const pct = c.target_amount ? Math.min(100, Math.round((c.amount / c.target_amount) * 100)) : null;
    const amtDelta = deltaStr(c.amount, c.prev_amount, "円");
    const supDelta = deltaStr(c.supporters, c.prev_supporters, "人");
    const nameBlock = c.url
      ? `<a class="card-link" href="${c.url}" target="_blank" rel="noopener"><h2>${c.name}</h2></a>`
      : `<h2>${c.name}</h2>`;
    return `
    <div class="card">
      <div class="card-head">
        <div>
          <span class="badge">${c.site}</span>
          ${nameBlock}
          <div class="period">${c.period_start} 〜 ${c.period_end}</div>
        </div>
        <span class="status-chip ${st.cls}">${st.label}</span>
      </div>
      <div class="stat-row">
        <div class="stat-block amount-block">
          <div class="label">支援金額</div>
          <div class="amount">${yen(c.amount)}</div>
          ${amtDelta ? `<div class="delta">${amtDelta}</div>` : ""}
        </div>
        <div class="stat-block supporters-block">
          <div class="label">支援者数</div>
          <div class="amount">${num(c.supporters)}人</div>
          ${supDelta ? `<div class="delta">${supDelta}</div>` : ""}
        </div>
      </div>
      ${pct !== null ? `
      <div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
        <div class="bar-label"><span>目標 ${yen(c.target_amount)}</span><span>${pct}%</span></div>
      </div>` : ""}
      ${sparkline(c.history, "var(--accent-amount)", "var(--accent-amount-fill)")}
      ${c.note ? `<div class="note">${c.note}</div>` : ""}
    </div>`;
  }).join("");
}

renderSummary();
renderCards();
</script>
"""


def main():
    rows = load_rows()
    campaigns = build_campaigns(rows)
    last_updated = max((r["date"] for r in rows), default=str(date.today()))
    html = TEMPLATE
    html = html.replace("__CAMPAIGNS_JSON__", json.dumps(campaigns, ensure_ascii=False))
    html = html.replace("__LAST_UPDATED__", last_updated)
    html = html.replace("__TODAY__", last_updated)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {OUT_PATH} ({len(campaigns)} campaigns, last_updated={last_updated})")


if __name__ == "__main__":
    main()
