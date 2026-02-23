# A-Stock Reports

A-share HTML report hosting repo for GitHub Pages.

## Structure

- `index.html`: report homepage index
- `reports/`: published HTML reports
- `reports/index.json`: metadata for index generation
- `tools/publish_report.py`: append one report and refresh index

## Publish One Report

```bash
python tools/publish_report.py \
  --source /absolute/path/to/report.html \
  --title "报告标题" \
  --symbol "股票代码" \
  --notes "可选备注"
```

Then commit and push:

```bash
git add reports index.html reports/index.json
git commit -m "docs(reports): add new html report"
git push
```

## GitHub Pages

In repository settings:

1. Open `Pages`
2. Source: `Deploy from a branch`
3. Branch: `main`, folder: `/ (root)`

Site URL:

- `https://songshen06.github.io/a-stock-reports/`
