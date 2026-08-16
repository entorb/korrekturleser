# AGENTS.md

Respond like smart caveman. Cut filler. Fragments fine. Technical terms exact.

## Dev setup

```sh
uv sync                  # Python deps
pnpm install             # JS deps
cp .env.example .env     # set LLM_PROVIDERS=Mock for local
```

Local DB auto-creates `db.sqlite` (user Torben, secret `test`, ID:1). Prod detection: check `/home/entorb/korrekturleser` exists.

## Run apps

| App | Script | URL |
| --- | ------ | --- |
| Streamlit (V1 PoC) | `scripts/run_streamlit.sh` | `localhost:8503/korrekturleser-streamlit/` |
| FastAPI (V2 BE) | `scripts/run_fastapi.sh` | `localhost:9002` |
| Vue.js (V2 FE) | `scripts/run_vue.sh` | `localhost:5173/korrekturleser-vue/` |

## Code generation

**FastAPI must be running** before generating frontend API client:

```sh
scripts/run_fastapi.sh   # terminal 1
pnpm generate-api        # terminal 2 — reads localhost:9002/openapi.json
```

`pnpm generate-api` does two things:

1. Generates `vue_app/src/api/` via `@hey-api/openapi-ts`
2. Runs `scripts/gen_mode_descriptions.py` → `vue_app/src/config/modes.ts`

Both are auto-generated — DO NOT edit manually.

To add a mode: edit `shared/mode_configs.py` (add `ModeConfig` entry + `TextMode` literal), then regenerate.

## Checks

run after each modification

- Python: `scripts/chk_py_lint.sh`
- JavaScript: `scripts/chk_js_format.sh`

run before committing

- `scripts/run_checks.sh` (runs all `chk_*.sh` sequentially)

If a check fails → fix → rerun that check only → repeat → final `scripts/run_checks.sh`.

To re-run a single failing test:

- Python: `uv run pytest path/to/test_file.py` or `uv run pytest path/to/test_file.py::test_function`
- JavaScript: `pnpm exec vitest path/to/test.spec.ts` or `pnpm exec vitest -t "test name"`

## Architecture

- **`shared/`** — single source of truth (DB, LLM providers, mode configs, config). Used by all apps.
- **`streamlit_app/`** — V1 legacy PoC.
- **`fastapi_app/`** — REST API at root `/be/korrekturleser-fastapi`. JWT auth (24h, HS256). 4 routers: auth, config, text, stats. Rate limiter (slowapi) PROD only. CORS: PROD → `entorb.net`, local → localhost:4173/5173.
- **`vue_app/`** — Vue 3 + Quasar + Pinia + TypeScript. See `vue_app/AGENTS.md` for conventions.

### Database

Auto-detects PROD vs local. Local: SQLite (`db.sqlite`) mirrors MySQL schema. Prod: MySQL via `MySQLConnectionPool` (pool size=3). `LLM_PROVIDERS=Mock` skips all DB writes.

## Testing

| Stack | Command | Notes |
| ----- | ------- | ----- |
| Python | `scripts/chk_py_test.sh` | `tests/conftest.py` sets `LLM_PROVIDERS=Mock` + `LLM_MODEL=random` before imports |
| Python + coverage | `run_py_test_cov.sh` | |
| Vue | `scripts/chk_js_test.sh` | vitest, jsdom, `vue_app/__tests__/` |
| Vue + coverage | `run_js_test_cov.sh` | |

Python tests: FastAPI `TestClient`, session-scoped fixtures (`client`, `auth_token`, `auth_headers`).

## Deployment

Target: Uberspace via SCP. Script: `scripts/deploy.sh`. Prod under gunicorn (see `deployment.md`).
