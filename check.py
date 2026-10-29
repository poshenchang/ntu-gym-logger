"""Sanity-check data.csv. Exits non-zero if any problem is found."""

import csv
import sys
from collections import defaultdict
from datetime import datetime, time, timedelta
from pathlib import Path

DATA = Path(__file__).with_name("data.csv")
MAX_GAP = timedelta(hours=1)


def opening_window(day):
    """Return (open, close) datetimes for a date, Asia/Taipei local time."""
    wd = day.weekday()
    if wd == 6:
        start, end = time(9), time(18)
    elif wd == 5:
        start, end = time(9), time(22)
    elif wd == 0 and 22 <= day.day <= 28:
        # Fourth Monday of the month: gym and pool closed until 17:00.
        start, end = time(17), time(22)
    else:
        start, end = time(8), time(22)
    return datetime.combine(day, start), datetime.combine(day, end)


def open_time_between(a, b):
    """How much opening time lies between datetimes a and b."""
    total = timedelta()
    day = a.date()
    while day <= b.date():
        lo, hi = opening_window(day)
        overlap = min(b, hi) - max(a, lo)
        if overlap > timedelta():
            total += overlap
        day += timedelta(days=1)
    return total


def check(rows):
    problems = []
    by_venue = defaultdict(list)
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        try:
            fetched = datetime.strptime(r["fetched_at"], "%Y-%m-%d %H:%M:%S")
            count, mx = int(r["count"]), int(r["max"])
        except (KeyError, ValueError) as e:
            problems.append(f"line {i}: unparseable row ({e})")
            continue
        if not 0 <= count <= mx:
            problems.append(f"line {i}: {r['venue']} count {count} outside 0..{mx}")
        by_venue[r["venue"]].append((i, fetched))

    for venue, seq in by_venue.items():
        for (i0, t0), (i1, t1) in zip(seq, seq[1:]):
            if t1 <= t0:
                problems.append(f"line {i1}: {venue} fetched_at {t1} not after line {i0} ({t0})")
            elif (gap := open_time_between(t0, t1)) > MAX_GAP:
                problems.append(f"line {i1}: {venue} gap of {gap} open time since {t0}")
    return problems


def main():
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    problems = check(rows)
    for p in problems:
        print(p)
    print(f"{len(rows)} rows, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
