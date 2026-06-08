# AGENTS.md

Respond like smart caveman. Cut filler. Fragments fine. Technical terms exact.

## Dev setup

```sh
uv sync                  # Python deps
pnpm install             # JS deps
cp .env.example .env     # then edit LLM_PROVIDERS=Mock for local
```

Local DB auto-creates `db.sqlite` with mock user (secret `test`, Torben, ID:1). Prod detection: check `/home/entorb/korrekturleser` exists.

## Run apps

| App | Script | URL |
|-----|--------|-----|
| FastAPI (V2 BE) | `scripts/run_fastapi.sh` | `localhost:9002` |
| Vue.js (V2 FE) | `scripts/run_vue.sh` | `localhost:5173/korrekturleser-vue/` |
| Streamlit (V1) | `scripts/run_streamlit.sh` | `localhost:8503/korrekturleser-streamlit/` |
| NiceGUI (V3) | `scripts/run_nicegui.sh` | `localhost:8505/korrekturleser-nice/` |

## Code generation

**FastAPI must be running** before generating frontend API client:

```sh
scripts/run_fastapi.sh   # terminal 1
pnpm generate-api        # terminal 2 — reads localhost:9002/openapi.json
```

`pnpm generate-api` does two things:
1. Generates `vue_app/src/api/` via `@hey-api/openapi-ts`
2. Runs `scripts/gen_mode_descriptions.py` → produces `vue_app/src/config/modes.ts`

Both outputs are auto-generated — DO NOT edit manually.

## After each change

| Scope | Command |
|-------|---------|
| Python | `scripts/chk_py_format.sh` (ruff format + check) |
| JS/TS/Vue | `scripts/chk_js_format.sh` (biome) |
| Full suite | `scripts/run_checks.sh` (runs all `chk_*.sh` sequentially) |

Frontend check pipeline: `pnpm check` runs (in parallel): `format types lint spell test knip`.

If a check fails → fix → rerun only that check → repeat → finally rerun full suite.

## Architecture

- **`shared/`** — single source of truth for business logic (DB, LLM providers, mode configs, config). Used by both Streamlit and FastAPI.
- **`fastapi_app/`** — REST API with JWT auth (24h tokens). 4 routers: auth, config, text, stats.
- **`vue_app/`** — Vue 3 + Quasar + Pinia + TypeScript.
- **`streamlit_app/`** — V1 PoC (legacy).
- **`nicegui_app/`** — V3 standalone (PoC, not in active use).

### Mode config (single source of truth)

File: `shared/mode_configs.py` — defines `MODE_CONFIGS` dict + `TextMode` Literal.

To add a mode:
1. Add `ModeConfig` entry to `MODE_CONFIGS`
2. Add mode string to `TextMode` Literal
3. Regenerate: `pnpm generate-api` (needs FastAPI running)

### Database

Auto-detects PROD vs local. Local: SQLite (`db.sqlite`) mirrors MySQL schema. Prod: MySQL via connection pool. Mocked LLM (`LLM_PROVIDERS=Mock`) skips all DB writes.

### Vue FE conventions

Separate `vue_app/AGENTS.md` covers Pinia store style (direct mutations, no setters), error handling, component patterns.

## Testing

| Stack | Command | Notes |
|-------|---------|-------|
| Python | `uv run pytest --quiet --tb=short` | `tests/conftest.py` sets `LLM_PROVIDERS=Mock` before any import |
| Vue | `pnpm test` (vitest) | `vue_app/__tests__/` |
| Vue + coverage | `pnpm test-cov` | |

Python tests use FastAPI `TestClient` with session-scoped auth fixtures. E2E: `pnpm cy:run` (Cypress).

## Deployment

Target: Uberspace shared hosting via SCP. Script: `scripts/deploy.sh` — builds Vue, runs checks, rsyncs to `entorb@entorb.net`. Prod runs under gunicorn (see `deployment.md`).
