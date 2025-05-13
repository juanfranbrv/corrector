@echo off
start uv run uvicorn app.main:app --reload
timeout /t 5 /nobreak >nul
start http://localhost:8000