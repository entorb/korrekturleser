# KI Korrekturleser

## Install, Update, Run

see [scripts](scripts/)

```sh
uv run -m streamlit run src/app.py
```

Eine keine App, für einen Kreis von max 10 Anwendern.

## Features

Text, den ein Benutzer eingibt an Gemini AI/LLM zum Korrekturlesen senden.

- Seite 1: Text verbessern
  - Modus 1: Korrigiere Grammatik und Rechtschreibung
  - Modus 2: Verbessere den Text
  - Modus 3: Fasse den Text zu Stichwörtern zusammen
  - Modus 4: Erstelle eine Text aus Stichwörtern
  - Input: Text of User
  - Output: 1. Response from LLM 2. Diff of input and LLM
- Seite 2: Statistics
  - Zeige die Usage Statistiken an

## Tech Stack

Ich habe sehr gute Python/uv Kenntnisse und Grundlangen in TypeScript, Vue.js, pnpm.

## Deployment

Uberspace shared web hoster.
transfer of files via scp.

## Login

- nur ein Geheimnis, kein Passwort
- Abgleich mit MySQL Datenbank

## Schnittstellen

Gemini LLM

- Secret: GEMINI_API_KEY

MySQL Datenbank für Login und Usage Stats

```sql
CREATE TABLE `user` (
 `id` smallint(5) unsigned NOT NULL,
 `name` varchar(16) NOT NULL,
 `geheimnis` varchar(16) NOT NULL,
 PRIMARY KEY (`id`),
 UNIQUE KEY `idx_geheimnis` (`geheimnis`)
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
