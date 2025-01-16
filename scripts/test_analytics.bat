@echo off
:: Script para Windows
echo Installing dependencies...
pip install -r requirements/analytics.txt

echo.
echo Creating test directories...
mkdir templates\reports 2>nul

echo.
echo Running tests...
pytest tests/analytics/ -v --asyncio-mode=strict

echo.
echo Checking coverage...
pytest tests/analytics/ --cov=src/analytics --cov-report=term-missing 