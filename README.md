# NTU Gym Crowd Logger

Logs occupancy of the NTU gym (健身中心) and indoor pool (室內游泳池) from
https://rent.pe.ntu.edu.tw every 10 min during opening hours, and renders a
weekday × time heatmap. See [spec.md](spec.md).

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q          # parser test against tests/fixtures/home.html
.venv/bin/python log.py      # append to data.csv (exit 1 if parsing finds nothing)
.venv/bin/python check.py    # timestamps increase, 0 ≤ count ≤ max, no >1h gaps while open
.venv/bin/python heatmap.py  # data.csv -> docs/index.html
```

- **Collection:** `.github/workflows/log.yml` runs on cron (UTC times for Taipei opening
  hours) and commits `data.csv` + `docs/index.html`. Trigger it manually first via
  *Actions → log → Run workflow* to confirm runners can reach the site.
- **Fallback:** if runners are blocked, use the systemd user timer in `deploy/`.
- **Heatmap:** enable GitHub Pages from the `main` branch, `/docs` folder.

All times are Asia/Taipei. `check.py` knows the fourth-Monday closure (open from 17:00)
but not public holidays, so expect gap reports on those days.
