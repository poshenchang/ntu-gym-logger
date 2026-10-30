from heatmap import aggregate, render


def test_aggregate_and_render():
    rows = [
        {"site_updated_at": "2026-10-29 20:20", "venue": "健身中心", "count": "30", "optimal": "80"},
        {"site_updated_at": "2026-10-29 20:10", "venue": "健身中心", "count": "50", "optimal": "80"},
    ]
    agg = aggregate(rows)
    assert agg["健身中心"][(3, "20:00")] == (40, 80, 2)
    page = render(rows)
    assert "median 40 / optimal 80 (2 samples)" in page
    assert "<script" not in page


def test_ignores_samples_outside_opening_hours():
    rows = [
        # Sunday 19:00 (closed at 18:00) and Thursday 07:30 (opens at 08:00).
        {"site_updated_at": "2026-11-01 19:00", "venue": "健身中心", "count": "0", "optimal": "80"},
        {"site_updated_at": "2026-10-29 07:30", "venue": "健身中心", "count": "0", "optimal": "80"},
    ]
    assert aggregate(rows) == {}
