# KI Korrekturleser

This repository contains the source code for an LLM-based text improvement tool, deployed to Uberspace shared hosting and used by a small user group of 10 people. User authentication is handled via per-user secrets validated against a database.

The application has been implemented in multiple tech stacks, to compare them:

- V1: Python Streamlit
- V2: Python FastAPI backend with Vue.js frontend
- V3: Python NiceGUI
- V4: (pending) Python Flask

[SonarQube](https://sonarcloud.io/summary/overall?id=entorb_korrekturleser) is used to check the code quality.

## Installation

### Python Backend (Streamlit & FastAPI)

The backends use [uv](https://docs.astral.sh/uv/) for package management.

```sh
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
```

### Vue.js Frontend

The Vue.js frontend uses [pnpm](https://pnpm.io/) for package management.

```sh
# Install pnpm (if not already installed)
npm install -g pnpm

pnpm install
```

### Configure Environment Variables

Both backends and the fronted use a shared `.env` file for configuration: see [.env.example](.env.example)

### Local Development (With SQLite Database)

The application can be run locally with an SQLite database:

- **Environment Detection**: Automatically detects if running locally or on production webserver
- **SQLite Database**: Auto-creates `db.sqlite` when running locally
  - Schema mirrors MySQL production database
  - Includes `user` and `history` tables with proper indexes
- **Mock User**: Pre-populated with test user
  - Login with secret `test` (user: Torben, ID: 1)
  - bcrypt-hashed credentials matching production format
- **Database Operations**: Fully functional in local mode
  - User authentication works against SQLite
  - Usage tracking saves to SQLite
  - Stats queries return real data from SQLite
  - Skips database writes when `LLM_PROVIDER == "Mocked"`
- **LLM Operations**: Work normally - only Gemini API key required

## Running the Applications

### Streamlit App (V1)

```sh
scripts/streamlit.sh
open http://localhost:8503/korrekturleser-streamlit/
```

### FastAPI Backend (V2)

```sh
scripts/fastapi.sh
open http://localhost:9002

# to view API spec
open http://localhost:9002/docs
```

### Vue.js Frontend (V2)

```sh
scripts/vue.sh
open http://localhost:5173/korrekturleser-vue/
```

The FastAPI routes and types are generated from FastAPI OpenAPI spec:

```sh
# start fastapi
scripts/fastapi.sh
# export the OpenAPI spec
pnpm generate-api
```

### NiceGUI App (V3)

```sh
scripts/nicegui.sh
open http://localhost:8505/korrekturleser-nice
```

Standalone application combining frontend and backend using NiceGUI. Features:

- Session-based authentication (auto-login in local mode)
- SQLite database in local mode, MySQL in production
- Real-time UI updates with async processing
- Diff visualization and markdown rendering
- Consistent styling with Vue.js app

### Code checks

These should be executed before commit and after each AI assistant step.

#### Python backends

```sh
scripts/ruff.sh
scripts/pytest.sh
```

#### Frontend

```sh
# this runs these in parallel: format lint type-check spell test
pnpm check
```

## Project Structure

```plain
korrekturleser/
├── shared/              # Shared Python code (DB, LLM provider, config)
│   ├── config.py        # Configuration and environment detection
│   ├── helper.py        # Shared helper functions
│   ├── helper_ai.py     # AI mode configurations (single source of truth)
│   ├── helper_db.py     # Database operations (MySQL prod, SQLite local)
│   ├── helper_diff.py   # Diff HTML generation
│   └── llm_provider.py  # LLM provider abstraction (Gemini, Ollama)
├── streamlit_app/       # Streamlit application (V1)
│   └── reports/         # Report pages
├── fastapi_app/         # FastAPI REST API (V2 Backend)
│   ├── routers/         # API endpoints
│   │   ├── auth.py      # Authentication (login with JWT)
│   │   ├── text.py      # Text improvement operations
│   │   └── stats.py     # Usage statistics
│   ├── schemas.py       # Pydantic models for validation
│   └── helper_fastapi.py # JWT token management
├── vue_app/             # Vue.js application (V2 Frontend)
│   ├── src/
│   │   ├── api/         # Auto-generated API client (from OpenAPI)
│   │   ├── config/      # Configuration (modes.ts is auto-generated)
│   │   ├── views/       # Page components (Login, Text, Stats)
│   │   ├── stores/      # Pinia state stores (auth, text)
│   │   ├── services/    # API client configuration
│   │   ├── utils/       # Utilities (JWT decoding)
│   │   └── plugins/     # Quasar configuration
│   └── __tests__/       # Vitest unit tests
├── nicegui_app/         # NiceGUI application (V3 Standalone)
│   ├── main.py          # App initialization, routing, auth guard
│   ├── helper_nicegui.py # SessionManager for user state
│   ├── page_login.py    # Login page
│   ├── page_text.py     # Text improvement page
│   └── page_stats.py    # Statistics page
├── scripts/             # Helper scripts
│   ├── generate_mode_descriptions.py  # Generates TypeScript from Python modes
│   ├── fastapi.sh       # Run FastAPI backend
│   ├── vue.sh           # Run Vue.js frontend
│   ├── nicegui.sh       # Run NiceGUI app
│   └── streamlit.sh     # Run Streamlit app
└── tests/               # Pytest for Streamlit and FastAPI
```

## Architecture Details

### Shared Layer (`shared/`)

All business logic is centralized in the shared layer, used by both Streamlit and FastAPI applications:

- **`helper_ai.py`** (Single Source of Truth for AI Modes)
  - `MODE_CONFIGS`: Dictionary defining all text improvement modes
  - Each `ModeConfig` contains:
    - `mode`: Mode identifier (e.g., "correct", "improve")
    - `description`: User-facing button text (e.g., "Korrigiere", "Verbessere")
    - `instruction`: LLM prompt instruction for processing
  - Available modes: correct, improve, summarize, expand, translate_de, translate_en
  - Frontend TypeScript types are auto-generated from these configurations

- **`config.py`**: Environment detection and LLM configuration
  - `where_am_i()`: Detects PROD vs Local environment
  - LLM provider and model settings

- **`llm_provider.py`**: LLM abstraction layer
  - `GeminiProvider`: Production LLM (Google Gemini API)
  - `OllamaProvider`: Local development only
  - Connection pooling with `@lru_cache`

- **`helper_db.py`**: Database operations with automatic environment detection
  - Auto-detects local vs production environment
  - **Production**: MySQL with connection pooling
  - **Local**: SQLite (`db.sqlite`) auto-created with matching schema
  - **Mocked LLM**: Skips database writes when `LLM_PROVIDER == "Mocked"`
  - User authentication with bcrypt (works with both databases)
  - Usage tracking and statistics (works with both databases)

### FastAPI Application (`fastapi_app/`)

REST API with JWT authentication and three endpoint groups:

**Authentication Router** (`routers/auth.py`):

- `POST /api/auth/login`: Authenticate with secret, returns JWT token
  - Rate limited: 5 attempts per minute per IP (production only)
  - JWT contains `user_id` and `username`
  - Token valid for 24 hours

**Text Improvement Router** (`routers/text.py`):

- `POST /api/text/`: Process text with AI
  - Request: `{ text: string, mode: TextMode }`
  - Response: `{ text_original, text_ai, mode, tokens_used, model }`
  - Requires JWT authentication
  - Logs usage to database (production only)

**Statistics Router** (`routers/stats.py`):

- `GET /api/stats/`: Get usage statistics
  - Admin (user_id=1): Returns stats for all users
  - Regular users: Returns only their own stats
  - Returns daily and total usage (requests and tokens)

### Vue.js Application (`vue_app/`)

Modern frontend with TypeScript, Vue 3, and Quasar:

- **Auto-Generated API Client**: Types and services generated from OpenAPI spec
- **JWT Token Management**: Client-side JWT decoding for user info (no `/me` endpoint needed)
- **State Management**: Pinia stores for authentication and text processing
- **Mode Configuration**: Auto-generated from Python `MODE_CONFIGS` via `pnpm generate-api`

### Code Generation Pipeline

1. Python defines modes in `shared/helper_ai.py` (single source of truth)
2. FastAPI exposes modes via OpenAPI schema
3. `pnpm generate-api` does two things:
   - Generates TypeScript API client from OpenAPI spec
   - Runs `scripts/generate_mode_descriptions.py` to extract mode descriptions
4. Frontend uses auto-generated types and descriptions

## Features

see **Available Modes** (defined in `shared/helper_ai.py`):

**Pages**:

- **1: Text improvement**
  - Input: Text of user
  - Output: Response from LLM + Diff view (for correct/improve modes)
- **2: Usage-Statistics**
  - Daily and total usage statistics
  - Admin view: All users; Regular users: Own stats only

## Deployment

- Uberspace shared web space
- transfer of files via scp
- see [deploy.sh](scripts/deploy.sh) and [deployment.md](deployment.md) for the Uberspace setup

## Authentication

### User Authentication Flow

- Each of the ~10 users receives a unique secret
- Secrets are stored as bcrypt hashes in the database
- The backend validates the user-provided secret against the database hashes

### V2 (FastAPI + Vue.js) - Stateless JWT Authentication

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

## Interfaces

### Gemini LLM

Secret: GEMINI_API_KEY from <https://aistudio.google.com/apikey>

### Database

**Production**: MySQL database for login and usage stats.

**Local Development**: SQLite database (`db.sqlite`) with identical schema, auto-created on first run.

Schema (applies to both MySQL and SQLite):

```sql
CREATE TABLE `user` (
 `id` smallint(5) unsigned NOT NULL,
 `name` varchar(16) NOT NULL,
 `secret_hashed` varchar(60) NOT NULL COMMENT 'bcrypt hashed secret (60 chars)',
 PRIMARY KEY (`id`),
 UNIQUE KEY `idx_secret_hashed` (`secret_hashed`)
);

CREATE TABLE `history` (
 `date` date NOT NULL,
 `user_id` smallint(5) unsigned NOT NULL,
 `cnt_requests` smallint(5) unsigned NOT NULL,
 `cnt_tokens` mediumint(8) unsigned NOT NULL,
 UNIQUE KEY `unique_date_user` (`date`,`user_id`),
 KEY `idx_date` (`user_id`),
 KEY `idx_user_id` (`user_id`)
);
```
