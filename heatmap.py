"""Render data.csv as a static HTML heatmap: median count per weekday x 30-min slot."""

import csv
import html
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median

from check import opening_window

DATA = Path(__file__).with_name("data.csv")
OUT = Path(__file__).with_name("docs") / "index.html"
VENUES = ("健身中心", "室內游泳池")
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
SLOTS = [f"{h:02d}:{m:02d}" for h in range(8, 22) for m in (0, 30)]
RED_AT = 1.5  # ratio count/optimal at which the colour is fully red


def aggregate(rows):
    """{venue: {(weekday, slot): (median count, median optimal, n)}}"""
    buckets = defaultdict(lambda: defaultdict(list))
    for r in rows:
        t = datetime.strptime(r["site_updated_at"], "%Y-%m-%d %H:%M")
        lo, hi = opening_window(t.date())
        if not lo <= t < hi:
            continue
        slot = f"{t.hour:02d}:{30 if t.minute >= 30 else 0:02d}"
        buckets[r["venue"]][(t.weekday(), slot)].append((int(r["count"]), int(r["optimal"])))
    return {
        venue: {
            key: (median(c for c, _ in v), median(o for _, o in v), len(v))
            for key, v in cells.items()
        }
        for venue, cells in buckets.items()
    }


def colour(ratio):
    hue = 120 * max(0.0, 1 - ratio / RED_AT)  # 120 = green, 0 = red
    return f"hsl({hue:.0f} 70% 50%)"


def table(venue, cells):
    head = "".join(f"<th>{d}</th>" for d in DAYS)
    body = []
    for slot in SLOTS:
        tds = []
        for wd, day in enumerate(DAYS):
            cell = cells.get((wd, slot))
            if cell is None:
                tds.append("<td></td>")
                continue
            count, optimal, n = cell
            ratio = count / optimal if optimal else 0
            tip = f"{day} {slot}: median {count:g} / optimal {optimal:g} ({n} samples)"
            tds.append(f'<td style="background:{colour(ratio)}" title="{tip}">{count:.0f}</td>')
        body.append(f"<tr><th>{slot}</th>{''.join(tds)}</tr>")
    return (
        f"<h2>{html.escape(venue)}</h2>\n<table><thead><tr><th></th>{head}</tr></thead>"
        f"<tbody>\n{chr(10).join(body)}\n</tbody></table>"
    )


def render(rows):
    agg = aggregate(rows)
    sections = "\n".join(table(v, agg.get(v, {})) for v in VENUES)
    span = ""
    if rows:
        span = f"{rows[0]['site_updated_at']} – {rows[-1]['site_updated_at']}, {len(rows)} rows"
    legend = "".join(
        f'<span style="background:{colour(r)}">{r:.0%}</span>' for r in (0, 0.5, 1, 1.5)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NTU Gym Crowd</title>
<style>
  :root {{ --bg: #fff; --fg: #222; --muted: #777; --empty: #eee; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #111; --fg: #eee; --muted: #999; --empty: #222; }}
  }}
  body {{ background: var(--bg); color: var(--fg); font: 14px/1.4 system-ui, sans-serif;
         margin: 0 auto; padding: 16px; max-width: 640px; }}
  h1 {{ font-size: 1.3em; margin: 0 0 4px; }}
  h2 {{ font-size: 1.1em; margin: 24px 0 8px; }}
  p {{ color: var(--muted); margin: 0 0 8px; }}
  table {{ border-collapse: collapse; width: 100%; table-layout: fixed;
          font-variant-numeric: tabular-nums; }}
  th {{ font-weight: 500; color: var(--muted); font-size: 12px; }}
  tbody th {{ text-align: right; padding-right: 6px; width: 3.5em; }}
  td {{ text-align: center; color: #111; background: var(--empty);
       border: 1px solid var(--bg); padding: 2px 0; font-size: 12px; }}
  .legend span {{ display: inline-block; padding: 2px 8px; color: #111; margin-right: 4px; }}
</style>
</head>
<body>
<h1>NTU gym crowd</h1>
<p>Median people present per weekday and 30-min slot, coloured relative to the optimal count.
{html.escape(span)}</p>
<p class="legend">count / optimal: {legend}</p>
{sections}
</body>
</html>
"""


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows), encoding="utf-8")
    print(f"wrote {out} from {len(rows)} rows")


if __name__ == "__main__":
    main()
