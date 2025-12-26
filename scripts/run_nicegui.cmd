@echo off
cd /d "%~dp0\.."

title Korrekturleser - NiceGUI
uv run python nicegui_app/main.py
