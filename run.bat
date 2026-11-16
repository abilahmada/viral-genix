@echo off
title ViralGenix - AI Content Intelligence
echo ===================================================
echo       VIRALGENIX - AI CONTENT INTELLIGENCE
echo ===================================================
echo Memeriksa dan menjalankan aplikasi Streamlit...
echo.

if exist ".venv\Scripts\python.exe" (
    echo Menjalankan via Virtual Environment [.venv]...
    ".venv\Scripts\python.exe" -m streamlit run app.py
) else (
    echo Menjalankan via Python Sistem...
    streamlit run app.py
)

pause
