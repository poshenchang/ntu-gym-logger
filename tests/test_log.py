import csv
from pathlib import Path

from log import append, parse

FIXTURE = Path(__file__).parent / "fixtures" / "home.html"


def test_parse_fixture():
    updated, rows = parse(FIXTURE.read_text(encoding="utf-8"))
    assert updated == "2026-10-29 20:20"
    assert rows == [
        {"venue": "健身中心", "count": 39, "optimal": 80, "max": 161},
        {"venue": "室內游泳池", "count": 33, "optimal": 50, "max": 130},
    ]


def test_parse_finds_nothing_on_unrelated_page():
    assert parse("<html><body>maintenance</body></html>") == (None, [])


def test_append_skips_stale_site_timestamp(tmp_path):
    path = tmp_path / "data.csv"
    rows = [{"venue": "健身中心", "count": 1, "optimal": 80, "max": 161}]
    assert append(path, "2026-10-29 20:21:00", "2026-10-29 20:20", rows) == 1
    assert append(path, "2026-10-29 20:31:00", "2026-10-29 20:20", rows) == 0
    assert append(path, "2026-10-29 20:41:00", "2026-10-29 20:40", rows) == 1
    with path.open(encoding="utf-8") as f:
        written = list(csv.DictReader(f))
    assert [r["site_updated_at"] for r in written] == ["2026-10-29 20:20", "2026-10-29 20:40"]
