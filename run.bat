@echo off
echo =============================================================
echo Starting Document Compliance and Privacy Analyzer...
echo =============================================================
set PYTHONPATH=.
python -m streamlit run app.py
pause
