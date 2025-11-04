#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit

uv run python nicegui_app/main.py
