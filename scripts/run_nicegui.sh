#!/usr/bin/env bash
cd "$(dirname "$0")/.."

uv run python nicegui_app/main.py
