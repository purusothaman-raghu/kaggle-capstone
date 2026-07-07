Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "Starting Document Compliance and Privacy Analyzer..." -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Cyan

$env:PYTHONPATH = "."
python -m streamlit run app.py
