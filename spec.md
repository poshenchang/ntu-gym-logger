# NTU Gym Crowd Logger

## Goal
Learn when the NTU gym (and indoor pool) is usually quiet, by weekday and time.

## Scope (v1)
- `log.py`: fetch https://rent.pe.ntu.edu.tw, parse 健身中心 and 室內游泳池 現在人數/最適人數/最大乘載人數
  and 最後更新時間, then append to `data.csv`
  (fetched_at, site_updated_at, venue, count, optimal, max).
  Skip the row if site_updated_at hasn't changed since the last row (catches a stale counter).
- Schedule: every 10 min during opening hours (Mon–Fri 8–22, Sat 9–22, Sun 9–18).
  GitHub Actions cron, committing data.csv. Fallback if the site blocks non-TW IPs:
  a systemd timer on an always-on box.
- `heatmap.py`: data.csv → one static HTML file showing median count per weekday × 30-min slot,
  colored relative to `optimal`. No JS deps. Publish via GitHub Pages so it's readable on a phone.
- Run it after ~2 weeks of data.

## Out of scope
Prediction models, notifications, other venues.

## Tech
Python stdlib + requests + BeautifulSoup. No DB. No credentials needed.

## Verification
- pytest: the parser runs against a saved HTML fixture (tests/fixtures/home.html).
- `check.py`: timestamps increase, 0 ≤ count ≤ max, no gaps > 1h during opening hours.
- log.py exits non-zero if parsing finds nothing, so the Action fails loudly.

## Steps
1. Save the fixture, write the parser and its test.
2. Write log.py and test it with workflow_dispatch. Confirm GH runners can reach the site.
3. Add the cron and let it collect data for 2 weeks.
4. Write heatmap.py and publish it.