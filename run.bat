@echo off
chcp 65001 >nul 2>&1
echo ======================================================================
echo   Competitor Price Scraper - Full Pipeline
echo ======================================================================
echo.
echo Usage:
echo   run.bat              = HTTP parsers + sync
echo   run.bat --pw         = HTTP + Playwright parsers + sync
echo   run.bat --parse      = Parse only (no sync)
echo   run.bat --iphone     = iPhone only
echo   run.bat --macbook    = MacBook only
echo.

cd /d "C:\devin_ai_powershell_devin\competitor_scraper_irepair"

if "%1"=="--pw" (
    python run_all.py --with-playwright
) else if "%1"=="--parse" (
    python run_all.py --no-sync
) else if "%1"=="--iphone" (
    python run_all.py --iphone-only
) else if "%1"=="--macbook" (
    python run_all.py --macbook-only
) else (
    python run_all.py
)

echo.
echo ======================================================================
echo   Done! Check parse_results/ and sync_log_*.xlsx
echo ======================================================================
pause
