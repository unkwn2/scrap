@echo off
chcp 65001 >nul 2>&1
echo ======================================================================
echo   Competitor Price Scraper
echo ======================================================================
echo.
echo Starting scraper...
echo.

cd /d "C:\devin_ai_powershell_devin\competitor_scraper_irepair"
python scraper.py

echo.
echo ======================================================================
echo   Done! Check the .xlsx and .json files in the folder.
echo ======================================================================
pause
