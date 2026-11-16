@echo off
title ViralGenix - Connect to GitHub
echo ========================================================
echo       VIRALGENIX - KONEKSI KE REPOSITORI GITHUB
echo ========================================================
echo Target Remote: https://github.com/abilahmada/viral-genix.git
echo.

:: 1. Cek apakah git terinstal
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git belum terinstal atau belum masuk ke PATH sistem Windows.
    echo Silakan unduh dan instal Git terlebih dahulu dari: https://git-scm.com/
    pause
    exit /b
)

:: 2. Inisialisasi repo jika belum ada
if not exist ".git" (
    echo [1/5] Menginisialisasi Git Repository lokal...
    git init
) else (
    echo [1/5] Git Repository lokal sudah ada (.git ditemukan).
)

:: 3. Pastikan branch utama bernama main
echo [2/5] Mengatur branch utama ke 'main'...
git branch -M main

:: 4. Cek dan tambahkan remote origin
echo [3/5] Menghubungkan remote origin ke GitHub...
git remote remove origin >nul 2>nul
git remote add origin https://github.com/abilahmada/viral-genix.git
git remote -v

:: 5. Staging file dengan perlindungan .gitignore (.env aman tidak ter-commit)
echo.
echo [4/5] Memeriksa dan staging file (git add .)...
git add .
git status -s

:: 6. Commit
echo.
set /p COMMIT_MSG="Masukkan pesan commit (tekan Enter untuk default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=feat: setup ViralGenix AI Content Intelligence & Production Engine

git commit -m "%COMMIT_MSG%"

:: 7. Push ke GitHub
echo.
echo [5/5] Melakukan Push ke GitHub (branch: main)...
echo Catatan: Jika muncul jendela login GitHub, silakan login melalui browser atau masukkan Personal Access Token (PAT).
echo.
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [INFO] Jika repository GitHub sudah memiliki commit awal (misal README/License):
    echo Mencoba sinkronisasi pull rebase...
    git pull origin main --rebase
    echo Mencoba push kembali...
    git push -u origin main
)

echo.
echo ========================================================
echo            PROSES KONEKSI GITHUB SELESAI
echo ========================================================
pause
