"""Fetch NTU gym/pool occupancy and append it to data.csv."""

import csv
import re
import ssl
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

URL = "https://rent.pe.ntu.edu.tw/"
DATA = Path(__file__).with_name("data.csv")
TZ = ZoneInfo("Asia/Taipei")
VENUES = ("健身中心", "室內游泳池")
FIELDS = ["fetched_at", "site_updated_at", "venue", "count", "optimal", "max"]
LABELS = {"現在人數": "count", "最適人數": "optimal", "最大乘載人數": "max"}


class LenientX509Adapter(HTTPAdapter):
    """Still verifies the cert chain, but drops Python 3.13's VERIFY_X509_STRICT:
    the site's certificate lacks a Subject Key Identifier and fails strict mode."""

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        kwargs["ssl_context"] = ctx
        super().init_poolmanager(*args, **kwargs)


def fetch():
    with requests.Session() as s:
        s.mount("https://", LenientX509Adapter())
        resp = s.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0 (ntu-gym-logger)"})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def parse(html):
    """Return (site_updated_at, [{venue, count, optimal, max}, ...])."""
    soup = BeautifulSoup(html, "html.parser")

    uptime = soup.select_one(".CMCUpTime")
    m = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", uptime.get_text()) if uptime else None
    site_updated_at = m.group(0) if m else None

    rows = []
    for item in soup.select(".CMCItem"):
        title = item.select_one(".IT")
        venue = title.get_text(strip=True).replace("\xa0", "") if title else ""
        if venue not in VENUES:
            continue
        row = {"venue": venue}
        for ici in item.select(".ICI"):
            span = ici.find("span")
            label = ici.get_text(strip=True).removeprefix(span.get_text(strip=True)).strip()
            if label in LABELS:
                row[LABELS[label]] = int(span.get_text(strip=True))
        if all(k in row for k in LABELS.values()):
            rows.append(row)
    return site_updated_at, rows


def last_updated_by_venue(path):
    last = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                last[r["venue"]] = r["site_updated_at"]
    return last


def append(path, fetched_at, site_updated_at, rows):
    """Append rows whose venue has a new site_updated_at. Return number written."""
    last = last_updated_by_venue(path)
    new = [r for r in rows if last.get(r["venue"]) != site_updated_at]
    if not new:
        return 0
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for r in new:
            w.writerow({"fetched_at": fetched_at, "site_updated_at": site_updated_at, **r})
    return len(new)


def main():
    site_updated_at, rows = parse(fetch())
    if not site_updated_at or not rows:
        print(f"parse failed: updated={site_updated_at!r} rows={rows!r}", file=sys.stderr)
        return 1
    fetched_at = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    n = append(DATA, fetched_at, site_updated_at, rows)
    print(f"{fetched_at} site={site_updated_at} wrote {n} row(s): {rows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
