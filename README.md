# KI Korrekturleser

## Install, Update, Run

see [scripts](scripts/)

### Setup Environment Variables

Both apps use a shared `.env` file for configuration:

```sh
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - GEMINI_API_KEY (get from https://aistudio.google.com/apikey)
# - DB_HOST, DB_USER, DB_PASS, DB_DATABASE (only for production)
# - JWT_SECRET_KEY (for FastAPI authentication)
```

### Local Development (Without Database)

The application supports local development without database access using mock mode:

- **Environment Detection**: Automatically detects if running locally or on production webserver
- **Mock User Credentials**: Login with secret `test` (user: Torben, ID: 1)
- **Database Operations**: All database operations are skipped in local mode
  - Login uses mock bcrypt-hashed credentials
  - Usage stats return (0, 0) without database queries
  - No usage tracking is saved
- **LLM Operations**: Work normally - only Gemini API key required

**Testing Mock Mode:**

```sh
uv run python tests/test_mock_mode.py
```

### Streamlit App (V1)

```sh
uv run -m streamlit run streamlit_app/app.py
```

### FastAPI Backend (V2)

```sh
uv run uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8000 --reload

# View API documentation
open http://127.0.0.1:8000/docs
```

## Project Structure

```plain
korrekturleser/
├── shared/              # Shared Python code (DB, LLM provider, config)
│   ├── config.py        # Configuration
│   ├── helper.py.       # Shared helper functions
│   ├── helper_db.py     # Database operations
│   └── llm_provider.py  # LLM operations
├── streamlit_app/       # Streamlit application (V1)
│   └── reports/         # Report pages
├── fastapi_app/         # FastAPI REST API (V1 BE)
│   └── routers/         # API endpoints
├── vue_app/             # Vue.js (V2 FE, planned)
└── tests/               # Pytest for Streamlit and FastAPI
```

## Features

Text, den ein Benutzer eingibt an Gemini AI/LLM zum Korrekturlesen senden.
Für einen kleinen Kreis von ca. 10 Benutzern

- Seite 1: Text verbessern
  - Modus 1: Korrigiere Grammatik und Rechtschreibung
  - Modus 2: Verbessere den Text
  - Modus 3: Fasse den Text zu Stichwörtern zusammen
  - Modus 4: Erstelle eine Text aus Stichwörtern
  - Input: Text of User
  - Output: 1. Response from LLM 2. Diff of input and LLM
- Seite 2: Nutzungs-Statistiken
  - Zeige die Nutzungs-Statistiken an

## Tech Stack

Ich habe sehr gute Python/uv Kenntnisse und Grundlangen in TypeScript, Vue.js, pnpm.

## Deployment

- Uberspace shared web space
- transfer of files via scp

## Login

- nur ein Geheimnis, kein Passwort
- geprüft gegen MySQL Datenbank

## Schnittstellen

### Gemini LLM

- Secret: GEMINI_API_KEY

### MySQL Datenbank

für Login und Usage Stats

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
