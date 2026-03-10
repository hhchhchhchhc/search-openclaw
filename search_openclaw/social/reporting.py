"""Small report writers used by vendored X / Zhihu scrapers."""

from __future__ import annotations

import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def safe_name(text: str) -> str:
    text = re.sub(r"\s+", "_", str(text).strip())
    text = re.sub(r"[^A-Za-z0-9_\-\u4e00-\u9fff]", "", text)
    return text[:80] or "keyword"


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_markdown_summary(path: Path, title: str, meta_lines: list[str], rows: list[dict], content_key: str) -> None:
    parts = [f"# {title}", "", *meta_lines, ""]
    for index, row in enumerate(rows, start=1):
        heading = row.get("detail_title") or row.get("title") or row.get("url") or f"Result {index}"
        parts.extend(
            [
                f"## {index}. {heading}",
                "",
                f"- URL: {row.get('url', '')}",
                "",
                str(row.get(content_key) or row.get("snippet") or row.get("text") or ""),
                "",
            ]
        )
    path.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")


def build_simple_html(title: str, subtitle_lines: list[str], rows: list[dict], content_key: str) -> str:
    cards = []
    for index, row in enumerate(rows, start=1):
        heading = row.get("detail_title") or row.get("title") or row.get("url") or f"Result {index}"
        content = str(row.get(content_key) or row.get("snippet") or row.get("text") or "")
        cards.append(
            f"""
            <article class="card">
              <div class="index">{index}</div>
              <h2>{html.escape(str(heading))}</h2>
              <a class="link" href="{html.escape(str(row.get('url') or '#'))}" target="_blank" rel="noreferrer">Open source</a>
              <pre>{html.escape(content)}</pre>
            </article>
            """
        )

    subtitle = "".join(f"<p>{html.escape(line)}</p>" for line in subtitle_lines)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{
      margin: 0;
      color: #201a14;
      font-family: "IBM Plex Sans", "PingFang SC", sans-serif;
      background:
        radial-gradient(900px 420px at 105% -10%, rgba(15,118,110,0.16), transparent 60%),
        radial-gradient(960px 440px at -5% 0%, rgba(201,109,29,0.12), transparent 58%),
        #f4efe7;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 32px 18px 60px; }}
    .hero, .card {{ background: rgba(255,255,255,0.84); border: 1px solid #d8cfbf; border-radius: 22px; }}
    .hero {{ padding: 24px; margin-bottom: 18px; }}
    .hero h1 {{ margin: 0 0 10px; font-size: clamp(2rem, 4vw, 3rem); }}
    .hero p {{ margin: 6px 0; color: #6a6259; }}
    .list {{ display: grid; gap: 14px; }}
    .card {{ padding: 18px; position: relative; box-shadow: 0 18px 44px rgba(39,28,20,0.08); }}
    .index {{ position: absolute; top: 12px; right: 16px; color: rgba(15,118,110,0.22); font-size: 2.2rem; font-weight: 700; }}
    .link {{ display: inline-flex; margin-top: 2px; color: white; background: #0f766e; padding: 8px 12px; border-radius: 999px; text-decoration: none; }}
    pre {{ white-space: pre-wrap; word-break: break-word; margin: 14px 0 0; font-family: inherit; line-height: 1.8; }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      {subtitle}
      <p>Generated at {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
    </section>
    <section class="list">{''.join(cards)}</section>
  </main>
</body>
</html>"""

