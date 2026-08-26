#!/bin/sh

cd "$(dirname "$0")/.."

# Playwright webServer starts FastAPI (Mock LLM) and Vite on its own.
# The backend requires a .env with a JWT secret, so create one if missing.
if [ ! -f .env ]; then
  cp .env.example .env
  sed -i '' 's/^LLM_PROVIDERS=.*/LLM_PROVIDERS=Mock/' .env
fi

pnpm run pw:run
