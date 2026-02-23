#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-_.\u4e00-\u9fff]", "", text)
    return text[:80] or "report"


def load_index(path: Path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_index(path: Path, items):
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def render_home(repo_root: Path, items):
    rows = []
    for item in items:
        title = html.escape(str(item.get("title", "Untitled")))
        date = html.escape(str(item.get("date", "")))
        symbol = html.escape(str(item.get("symbol", "")))
        notes = html.escape(str(item.get("notes", "")))
        href = html.escape(str(item.get("path", "")))
        subtitle = f"{symbol} · {date}" if symbol else date
        subtitle = html.escape(subtitle)
        rows.append(
            "<article class=\"card\">"
            f"<p class=\"meta\">{subtitle}</p>"
            f"<h3>{title}</h3>"
            f"<p class=\"notes\">{notes or '无附加备注'}</p>"
            f"<a class=\"btn\" href=\"{href}\" target=\"_blank\">查看报告</a>"
            "</article>"
        )

    card_rows = "\n".join(rows) if rows else "<p class=\"empty\">暂无报告，等待下一份研究产出。</p>"
    total = len(items)
    latest = html.escape(str(items[0].get("date", "-"))) if items else "-"

    content = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>A-Stock Reports</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Noto+Serif+SC:wght@500;700&display=swap');
    :root {{
      --bg: #f5f7f4;
      --ink: #11201b;
      --muted: #5a6a63;
      --panel: #ffffff;
      --line: #dce5df;
      --brand: #0f766e;
      --brand-2: #0b4f49;
      --warm: #d97706;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Manrope", "PingFang SC", "Hiragino Sans GB", sans-serif;
      background:
        radial-gradient(circle at 5% 0%, #d9efe6 0%, transparent 30%),
        radial-gradient(circle at 100% 20%, #f9e8d1 0%, transparent 28%),
        var(--bg);
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 48px; }}
    .hero {{
      border: 1px solid var(--line);
      border-radius: 20px;
      background: linear-gradient(135deg, #ffffff 0%, #f1f8f4 60%, #f8f4eb 100%);
      padding: 22px 22px 18px;
      box-shadow: 0 10px 28px rgba(16, 40, 33, 0.06);
    }}
    h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.08;
      letter-spacing: -0.02em;
      font-weight: 800;
    }}
    .subtitle {{
      margin: 8px 0 16px;
      color: var(--muted);
      font-family: "Noto Serif SC", serif;
      font-size: 14px;
      line-height: 1.65;
    }}
    .kpis {{ display: grid; gap: 10px; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .kpi {{
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--panel);
      padding: 12px;
    }}
    .kpi .label {{ color: var(--muted); font-size: 12px; }}
    .kpi .val {{ margin-top: 6px; font-weight: 800; font-size: 18px; }}
    .kpi:nth-child(2) .val {{ color: var(--brand-2); }}
    .kpi:nth-child(3) .val {{ color: var(--warm); }}
    .grid {{
      margin-top: 18px;
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--panel);
      padding: 14px;
      min-height: 170px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 6px 18px rgba(17, 32, 27, 0.05);
      transform: translateY(10px);
      opacity: 0;
      animation: rise .48s ease forwards;
    }}
    .card:nth-child(2n) {{ animation-delay: .04s; }}
    .card:nth-child(3n) {{ animation-delay: .08s; }}
    .meta {{
      margin: 0;
      font-size: 12px;
      color: var(--brand);
      font-weight: 700;
      letter-spacing: .02em;
    }}
    .card h3 {{
      margin: 8px 0 10px;
      font-size: 18px;
      line-height: 1.3;
      letter-spacing: -0.01em;
    }}
    .notes {{
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
      flex: 1;
    }}
    .btn {{
      align-self: flex-start;
      border-radius: 999px;
      border: 1px solid var(--brand);
      color: var(--brand);
      text-decoration: none;
      font-size: 12px;
      font-weight: 700;
      padding: 7px 11px;
      transition: all .18s ease;
    }}
    .btn:hover {{ background: var(--brand); color: #fff; }}
    .empty {{
      margin-top: 16px;
      border: 1px dashed var(--line);
      border-radius: 12px;
      padding: 14px;
      color: var(--muted);
      background: #ffffffaa;
    }}
    @keyframes rise {{
      to {{ transform: translateY(0); opacity: 1; }}
    }}
    @media (max-width: 720px) {{
      .kpis {{ grid-template-columns: 1fr; }}
      .wrap {{ padding: 20px 14px 28px; }}
      .hero {{ border-radius: 16px; }}
    }}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <section class=\"hero\">
      <h1>A-Stock Research Index</h1>
      <p class=\"subtitle\">本页面仅用于研究 agent 与个人学习，不构成任何投资建议。</p>
      <div class=\"kpis\">
        <div class=\"kpi\"><div class=\"label\">报告总数</div><div class=\"val\">{total}</div></div>
        <div class=\"kpi\"><div class=\"label\">最近更新</div><div class=\"val\">{latest}</div></div>
        <div class=\"kpi\"><div class=\"label\">发布方式</div><div class=\"val\">Agent Pipeline</div></div>
      </div>
    </section>
    <section class=\"grid\">
      {card_rows}
    </section>
  </main>
</body>
</html>
"""
    (repo_root / "index.html").write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Add an HTML report and update GitHub Pages index.")
    parser.add_argument("--source", required=True, help="Source HTML report path")
    parser.add_argument("--title", required=True, help="Display title in index")
    parser.add_argument("--symbol", default="", help="Ticker/symbol")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Display date (YYYY-MM-DD)")
    parser.add_argument("--notes", default="", help="Optional note")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    src = Path(args.source).expanduser().resolve()
    if not src.exists() or src.suffix.lower() != ".html":
        raise SystemExit(f"Invalid source html: {src}")

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = slugify(src.stem)
    dst_name = f"{ts}-{stem}.html"
    dst = reports_dir / dst_name
    shutil.copy2(src, dst)

    index_path = reports_dir / "index.json"
    items = load_index(index_path)
    items.insert(0, {
        "date": args.date,
        "title": args.title,
        "symbol": args.symbol,
        "notes": args.notes,
        "path": f"reports/{dst_name}",
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
    })

    save_index(index_path, items)
    render_home(repo_root, items)
    print(f"Added: reports/{dst_name}")
    print("Updated: reports/index.json")
    print("Updated: index.html")


if __name__ == "__main__":
    main()
