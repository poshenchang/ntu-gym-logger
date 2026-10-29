#!/bin/sh
# Same steps as .github/workflows/log.yml, for the systemd fallback.
set -e
cd "$(dirname "$0")/.."
git pull --rebase --quiet
.venv/bin/python log.py
.venv/bin/python heatmap.py
git add data.csv docs/index.html
git diff --cached --quiet && exit 0
git commit -q -m "data: $(TZ=Asia/Taipei date '+%F %H:%M')"
git push --quiet
