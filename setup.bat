@echo off
title ViralGenix Setup
echo ===================================================
echo     VIRALGENIX - INSTALASI DEPENDENCIES
echo ===================================================
echo.

if exist ".venv\Scripts\python.exe" (
    echo Menggunakan Virtual Environment [.venv]...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
) else (
    echo Menggunakan Python Sistem...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo.
echo ===================================================
echo Instalasi selesai! Jalankan 'run.bat' untuk memulai aplikasi.
echo ===================================================
pause
