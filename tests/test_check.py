from check import check


def row(fetched, count=10, mx=100, venue="健身中心"):
    return {"fetched_at": fetched, "venue": venue, "count": str(count), "max": str(mx)}


def test_clean_data_passes():
    # Thu evening -> Fri morning: the overnight closure is not a gap.
    rows = [row("2026-10-29 21:50:00"), row("2026-10-30 08:05:00"), row("2026-10-30 08:55:00")]
    assert check(rows) == []


def test_detects_problems():
    rows = [
        row("2026-10-29 10:00:00"),
        row("2026-10-29 09:00:00"),            # goes backwards
        row("2026-10-29 11:30:00", count=101),  # over max, and 2.5h gap
    ]
    problems = check(rows)
    assert len(problems) == 3


def test_fourth_monday_morning_closure_is_not_a_gap():
    # 2026-10-26 is the fourth Monday of October.
    assert check([row("2026-10-25 17:50:00"), row("2026-10-26 17:05:00")]) == []
