@echo off
REM =====================================================
REM  Shopee Tools Bot - One-Command Runner (Windows)
REM  Cara pakai (double-click atau dari CMD):
REM    run.bat                -> jalankan bot (pakai token di .env)
REM    run.bat <BOT_TOKEN>    -> set token sekali, lalu jalankan
REM =====================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

REM 1. Cek python
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python tidak ditemukan. Install Python 3.10+ dari https://www.python.org/downloads/
  pause
  exit /b 1
)
echo [OK] Python ditemukan.

REM 2. Buat virtual environment kalau belum ada
if not exist ".venv" (
  echo [INFO] Membuat virtual environment .venv ...
  python -m venv .venv
)

REM 3. Aktifkan venv
call .venv\Scripts\activate.bat

REM 4. Install dependencies
echo [INFO] Menginstall dependencies ...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
echo [OK] Dependencies siap.

REM 5. Siapkan .env
if not exist ".env" (
  copy /y ".env.example" ".env" >nul
  echo [INFO] File .env dibuat dari template.
)

REM 6. Kalau token dikirim sebagai argumen, tulis ke .env
if not "%~1"=="" (
  > .env.tmp (
    for /f "usebackq tokens=1* delims==" %%A in (".env") do (
      if "%%A"=="BOT_TOKEN" (
        echo BOT_TOKEN=%~1
      ) else (
        echo %%A=%%B
      )
    )
  )
  move /y .env.tmp .env >nul
  echo [OK] BOT_TOKEN tersimpan di .env.
)

REM 7. Jalankan bot
echo [INFO] Menjalankan Shopee Tools Bot ... (tutup jendela untuk berhenti)
echo.
python bot.py
pause
