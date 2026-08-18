@echo off
cd /d "%~dp0\.."

title Korrekturleser FastAPI and Vue
start /b uv run uvicorn fastapi_app.main:app --host localhost --port 9002 --reload
start /b pnpm dev

@REM pause
