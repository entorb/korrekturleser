@echo off
cd /d "%~dp0\.."

title Korrekturleser FastAPI and Vue
start /b uv run uvicorn fastapi_app.main:app --host 127.0.0.1 --port 9002 --reload
start /b pnpm dev

@REM pause
