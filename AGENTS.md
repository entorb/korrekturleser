# AGENTS.md

## Project Overview

**KI Korrekturleser** is an AI-powered text proofreading and improvement application for a small user group (~10 users). It provides grammar correction, text improvement, summarization, expansion, and translation features using Gemini AI.

The project consists of four applications:

- **Streamlit App** (V1 frontend) - Legacy UI in `streamlit_app/`
- **FastAPI Backend** (V2 backend) - REST API in `fastapi_app/`
- **Vue.js App** (V2 frontend) - Modern UI in `vue_app/`
- **NiceGUI App** (V3 standalone) - All-in-one UI in `nicegui_app/`

## Common Commands

### Development Setup

```sh
# Install dependencies
uv sync

# Copy environment variables template
cp .env.example .env
# Then edit .env with your GEMINI_API_KEY and FASTAPI_JWT_SECRET_KEY
```

## Running Applications

### Streamlit App (V1)

```sh
scripts/streamlit.sh
open http://127.0.0.1:8503/korrekturleser/
```

### FastAPI Backend (V2)

```sh
scripts/fastapi.sh
open http://127.0.0.1:8504

# to view API spec
open http://127.0.0.1:8504/docs
```

### Vue.js Frontend (V2)

```sh
scripts/vue.sh
open http://127.0.0.1:5173/korrekturleser2/
```

### NiceGUI App (V3)

```sh
scripts/nicegui.sh
open http://127.0.0.1:8505
```

The NiceGUI app is a standalone application that combines frontend and backend in a single Python file, using the same shared business logic layer.

### Generating TypeScript API Client

The Vue.js frontend uses auto-generated TypeScript types and API clients from the FastAPI OpenAPI spec:

```sh
# Start FastAPI backend first
scripts/fastapi.sh

# Generate TypeScript client (in a new terminal)
pnpm generate-api
```

This command does two things:

1. Creates type-safe API clients in `vue_app/src/api/` using `openapi-typescript-codegen`
2. Generates `vue_app/src/config/modes.ts` with mode descriptions extracted from `shared/helper_ai.py`

This ensures a single source of truth for mode configurations in the Python backend.

### Code checks

**IMPORTANT**: These should be executed before each commit and after each AI assistant step.

#### Python backends

```sh
scripts/ruff.sh
scripts/pytest.sh
```

#### Frontend

```sh
# Runs in parallel: format, lint, type-check, spell, test
pnpm check
```

## Architecture

### Shared Code Layer (`shared/`)

All business logic and external integrations are shared between Streamlit and FastAPI apps:

- **`config.py`**: Environment detection and LLM configuration
  - Detects PROD vs Local based on PATH_ON_WEBSERVER existence
  - Defines LLM provider and model settings

- **`helper_ai.py`**: AI mode configuration (SINGLE SOURCE OF TRUTH)
  - `MODE_CONFIGS`: Dictionary of all improvement modes with descriptions and instructions
  - Each `ModeConfig` contains: mode identifier, user-facing description, LLM instruction
  - Modes: correct, improve, summarize, expand, translate_de, translate_en
  - Used by both backend (FastAPI) and frontend (Vue.js via code generation)

- **`llm_provider.py`**: LLM abstraction layer with provider classes
  - `GeminiProvider`: Production LLM using Google Gemini API
  - `OllamaProvider`: Local development only (not available in PROD)
  - Uses `@lru_cache` for connection pooling
  - Returns tuple: `(response_text, tokens_used)`

- **`helper_db.py`**: Database operations with automatic environment detection
  - **Production (MySQL)**: Connection pooling via `get_db_pool()` and `db_connection()` context manager
  - **Local (SQLite)**: Auto-creates `db.sqlite` with `init_sqlite_db()`, uses `sqlite_connection()` context manager
  - Login: `db_select_user_from_geheimnis()` - verifies bcrypt hash for all users (O(n), acceptable for <10 users)
  - Usage tracking: `db_insert_usage()` - skips when `LLM_PROVIDER == "Mocked"`
  - Stats queries: `db_select_usage_stats_daily()`, `db_select_usage_stats_total()` - work with both MySQL and SQLite

- **`helper.py`**: Utility functions
  - `my_get_env()`: Strict environment variable getter
  - `verify_geheimnis()`: bcrypt password verification
  - `where_am_i()`: Returns "PROD" or "Local"

### Database Support

**Production (MySQL)**:

- Full MySQL database with user authentication and usage tracking
- Connection pooling via `get_db_pool()` and `db_connection()` context manager

**Local Development (SQLite)**:

- Automatic SQLite database (`db.sqlite`) created when running locally
- Schema mirrors MySQL production database
- Auto-populated with mock user (Login with secret `test`, user: Torben, ID: 1)
- Environment detection: Checks if `/home/entorb/korrekturleser` exists
- Only `GEMINI_API_KEY` required for local development

**LLM Mocked Mode**:

- When `LLM_PROVIDER == "Mocked"`, database writes are skipped
- Useful for testing without consuming API tokens

### FastAPI Application (`fastapi_app/`)

REST API with JWT authentication:

- **`main.py`**: App initialization, CORS configuration, router registration
  - CORS origins configured for local dev and production
  - Three routers: auth, improve, stats

- **`helper_fastapi.py`**: JWT authentication
  - `create_access_token()`: Creates JWT with 24h expiration
  - `get_current_user()`: FastAPI dependency for protected routes
  - Uses HS256 algorithm with FASTAPI_JWT_SECRET_KEY

- **`schemas.py`**: Pydantic models for request/response validation
  - `TextMode` Literal: Defines valid mode types
  - All API contracts defined here

- **`routers/`**:
  - `auth.py`: Authentication router
    - `POST /api/auth/login`: Authenticate with secret, returns JWT token
      - Rate limited: 5 attempts per minute per IP (production only)
      - JWT contains `user_id` and `username`
      - Token valid for 24 hours

  - `text.py`: Text improvement router
    - `POST /api/text/`: Process text with AI
      - Request: `{ text: string, mode: TextMode }`
      - Response: `{ text_original, text_ai, mode, tokens_used, model }`
      - Requires JWT authentication
      - Gets LLM provider via `get_cached_llm_provider()`
      - Maps mode to instruction using `MODE_CONFIGS`
      - Logs usage to database (production only)

  - `stats.py`: Statistics router
    - `GET /api/stats/`: Get usage statistics
      - Admin (user_id=1): Returns stats for all users
      - Regular users: Returns only their own stats
      - Returns daily and total usage (requests and tokens)

### Vue.js Application (`vue_app/`)

Modern frontend with TypeScript, Vue 3, and Quasar:

- **`src/api/`**: Auto-generated from FastAPI OpenAPI spec
  - Services: `AuthenticationService`, `TextImprovementService`, `StatisticsService`
  - Models: TypeScript types matching Pydantic schemas
  - Generated with `pnpm generate-api` (requires FastAPI running)

- **`src/services/apiClient.ts`**: API client configuration
  - Configures OpenAPI base URL from `VITE_API_BASE_URL`
  - Manages JWT token injection via `tokenManager`
  - Exports configured service instances

- **`src/config/env.ts`**: Environment validation
  - Validates required `VITE_API_BASE_URL` at startup
  - Provides typed config object for app-wide use

- **`src/config/modes.ts`**: Mode configuration (AUTO-GENERATED)
  - Generated from `shared/helper_ai.py` by `pnpm generate-api`
  - Provides mode descriptions and helper functions
  - DO NOT edit manually - regenerate using `pnpm generate-api`

- **`src/utils/jwt.ts`**: JWT token utilities
  - `decodeJwt()`: Client-side JWT decoding to extract user info
  - `isTokenExpired()`: Check if token has expired
  - No server call needed for user information extraction

- **`src/stores/`**: Pinia state management
  - `auth.ts`: Authentication state, login/logout
    - `loadUserFromToken()`: Decodes JWT client-side for user info
    - No `/api/auth/me` endpoint needed (optimization)
  - `text.ts`: Text processing state, modes, results

- **`src/views/`**: Page components
  - `LoginView.vue`: User authentication
  - `TextView.vue`: Main text improvement interface
  - `StatsView.vue`: Usage statistics (admin)

- **`__tests__/`**: Vitest unit tests
  - Store tests: `stores/__tests__/auth.spec.ts`, `text.spec.ts`
  - Test setup: `__tests__/setup.ts` with localStorage mocks

### NiceGUI Application (`nicegui_app/`)

Standalone Python application combining frontend and backend:

- **`main.py`**: Application routing and authentication
  - Uses `nicegui` library for reactive web UI
  - **Routes**: Three pages - `/` (text improvement), `/login` (authentication), `/stats` (statistics), all relative to `BASE_URL` (`/korrekturleser-nice`)
  - **Authentication**: `_require_authentication()` helper ensures all protected routes require login
  - **Auto-login**: Local development mode automatically logs in test user
  - **Port**: 8505
  - **Auto-reload**: Enabled in local mode

- **`helper_nicegui.py`**: Session management
  - **SessionManager**: Manages user authentication state using NiceGUI's `app.storage.user`
  - Session-based authentication (no JWT tokens)
  - Session usage tracking (requests and tokens)

- **`page_login.py`**: Login page
  - Login form with password input
  - bcrypt verification via `db_select_user_from_geheimnis()`
  - Auto-redirects authenticated users

- **`page_text.py`**: Main text improvement page
  - Mode selector with all AI improvement modes
  - Input/output text areas with clipboard support
  - Diff visualization for correct/improve modes (using `shared/helper_diff.py`)
  - Markdown rendering for summarize mode
  - Async LLM processing with spinner
  - Ctrl+Enter / Cmd+Enter keyboard shortcuts
  - Escape key navigates to stats

- **`page_stats.py`**: Statistics page
  - Displays total and daily usage stats from database
  - Shows config (ENV, LLM provider/model)
  - Shows session stats (user, requests, tokens)
  - Admin (user_id=1) sees all users' stats
  - Escape key navigates back to text page

Key differences from V1/V2:

- Multi-file modular structure (main, pages, helpers)
- Reactive UI with NiceGUI (similar to Streamlit but more flexible)
- Session storage instead of JWT tokens
- Direct use of shared business logic (no REST API needed)

### Authentication Flow

**Streamlit (V1) & NiceGUI (V3)**:

- Uses bcrypt-hashed secret stored in DB
- Session-based authentication
- Auto-login in local development mode

**FastAPI + Vue.js (V2) - Stateless JWT Authentication**:

1. **Login**: User provides secret via `POST /api/auth/login`
   - Backend validates secret against database
   - Returns JWT token (24h validity) containing `user_id` and `username`

2. **Token Storage**: Frontend stores JWT in localStorage

3. **User Info Extraction**:
   - JWT token is decoded **client-side** to extract user information
   - No additional API call needed (optimization)
   - Token validation happens on protected routes

4. **Protected Routes**: All API requests include JWT in Authorization header
   - Backend validates token signature and expiration
   - Extracts user info from token for authorization

### Database Schema

Two tables in MySQL:

- `user`: (id, name, secret_hashed) - bcrypt hashed secrets (60 chars)
- `history`: (date, user_id, cnt_requests, cnt_tokens) - usage tracking with unique constraint on (date, user_id)

### Deployment

- Target: Uberspace shared web hosting
- Transfer: SCP file transfer
- Detection: Production mode when PATH_ON_WEBSERVER exists

## Development Notes

### LLM Provider Configuration

Edit `.env` to change LLM provider or model:

```python
# Gemini, Ollama, Mock, OpenAI, OpenAI_AzureDefaultAzureCredential
LLM_PROVIDER=Gemini
```

Ollama is available for local development only (automatically disabled in PROD).

### Adding New Improvement Modes

To add a new mode, follow these steps:

1. Add a new `ModeConfig` entry to `MODE_CONFIGS` in `shared/helper_ai.py` with:
   - `mode`: The mode identifier (e.g., "translate_fr")
   - `description`: User-facing button text (e.g., "Übersetzen -> FR")
   - `instruction`: LLM instruction for processing

2. Add the mode to the `TextMode` Literal type in `shared/helper_ai.py`
   - This type is imported by `fastapi_app/schemas.py`

3. Regenerate the TypeScript API client to sync the frontend:

   ```sh
   pnpm generate-api
   ```

   This command:
   - Generates TypeScript API client from OpenAPI spec
   - Runs `scripts/generate_mode_descriptions.py` to extract mode descriptions from `MODE_CONFIGS`
   - Creates/updates `vue_app/src/config/modes.ts` with TypeScript mode types and descriptions

This workflow ensures mode configurations are centralized in `shared/helper_ai.py` (single source of truth) and automatically propagated to the frontend.

### Testing Mock Mode

The mock mode allows full local development without database access:

- Automatic when running locally
- Test with `uv run python tests/test_mock_mode.py`
- Mock user credentials defined in `shared/helper_db.py`

### Python Path Configuration

When running tests, `pyproject.toml` configures pytest to include shared modules:

```toml
[tool.pytest.ini_options]
pythonpath = ["shared", "streamlit_app", "fastapi_app"]
```

### Frontend Testing

Vue.js uses Vitest for unit testing:

- Test files: `**/__tests__/*.spec.ts`
- Run tests: `pnpm test`
- Coverage: `pnpm test-cov`
- Config: `vitest.config.ts`

Key test files:

- `vue_app/src/stores/__tests__/auth.spec.ts` - Auth store logic
- `vue_app/src/stores/__tests__/text.spec.ts` - Text store logic
- `vue_app/__tests__/setup.ts` - Global test mocks (localStorage, etc.)

## Memory

- after modifying python files, always run `scripts/ruff.sh`
- after modifiying .ts or .vue files, always run `pnpm format`
- when you are finished with a task, that involves modification of @vue_app/ run `pnpm check`
- after modifiying the api in @fastapi_app/ run `pnpm generate-api` and `pnpm format`
