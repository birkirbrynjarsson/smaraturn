# Smaraturn

Post the daily lunch menu on the teams Slack channel. Used by [AGR](https://www.agrinventory.com) employees to know about the menu option in the cafeteria on the 19th floor of the Smáratorg Tower.

Flask API and automation service for collecting weekly cafeteria `.docx` menus, parsing them into a JSON key-value store, exposing menu endpoints, and posting daily menus to Slack.

## What This Project Does

- Fetches unread menu emails and saves `.docx` attachments.
- Parses weekly menu documents into day-level entries.
- Stores parsed menus in [menu.json](menu.json) via the local [pickledb](pickledb/pickledb.py) fork.
- Serves menu data through a REST API from [app.py](app.py).
- Runs scheduled background jobs from [scheduledTasks.py](scheduledTasks.py).
- Posts daily menu messages to Slack through [slackbot.py](slackbot.py).

## Repository Structure

- [app.py](app.py): Main Flask app, API routes, and in-process background scheduler setup.
- [wsgi.py](wsgi.py): WSGI entrypoint for production servers.
- [menuParser.py](menuParser.py): Parser for weekly menu `.docx` files.
- [getmail.py](getmail.py): IMAP client that downloads trusted `.docx` attachments.
- [scheduledTasks.py](scheduledTasks.py): Cron-style jobs for mail fetch, parsing, stashing, and Slack posting.
- [slackbot.py](slackbot.py): Slack webhook posting logic.
- [slackMenu.py](slackMenu.py): Food string to emoji decoration.
- [menu.json](menu.json): Persistent menu database (JSON).
- [menus](menus): Historical/stashed menu source files.
- [assets](assets): Static assets (currently [assets/chef.png](assets/chef.png)).
- [Dockerfile](Dockerfile): Container setup.
- [Pipfile](Pipfile), [Pipfile.lock](Pipfile.lock): Dependencies and locked versions.
- [secrets.py.secret](secrets.py.secret): Encrypted secrets template.

## Runtime Flow

1. Startup in [app.py](app.py):
   - Initializes Flask + Flask-RESTX API under `/api/v1`.
   - Configures APScheduler background jobs.
2. Scheduled ingestion:
   - `getmail.main()` saves unread trusted attachments to `attachments/`.
   - Parser converts `.docx` contents to `{YYYY-MM-DD: [dishes...]}`.
   - Data is written into [menu.json](menu.json).
3. API consumers request menus.
4. Slack job posts decorated dishes at scheduled time.

## Prerequisites

- Python 3.12 (matches [Pipfile](Pipfile)).
- Pipenv (recommended) or virtualenv + pip.
- Network access to:
  - Gmail IMAP (`imap.gmail.com`) for mail ingestion.
  - Slack incoming webhook URL for posting.

## Setup

### Option A: Pipenv (recommended)

1. Install Pipenv:

   ```bash
   python3 -m pip install --user pipenv
   ```

2. Install dependencies:

   ```bash
   pipenv install
   ```

3. Start shell:

   ```bash
   pipenv shell
   ```

### Option B: venv + pip

1. Create and activate environment:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. Install minimal dependencies:

   ```bash
   pip install flask flask-restx apscheduler pytz python-docx easyimap requests gunicorn
   ```

Note: The project vendors [pickledb/pickledb.py](pickledb/pickledb.py), so no external `pickledb` package is required.

## Secrets Configuration

The code imports a local module named `secrets` in [getmail.py](getmail.py) and [slackbot.py](slackbot.py).

Create `secrets.py` in the repository root with these callables:

```python
def getMailLogin() -> str:
    ...

def getMailPassword() -> str:
    ...

def getTrustedDomains() -> list[str]:
    ...

def getSlackWebhookUrl() -> str:
    ...
```

Expected behavior:

- `getTrustedDomains()` returns allowed sender substrings for filtering inbound mail.
- `getSlackWebhookUrl()` returns a valid Slack incoming webhook URL.

The file [secrets.py.secret](secrets.py.secret) is an encrypted template used in the original workflow.

## Running the Application

### Development

```bash
python app.py
```

API base URL: `http://localhost:5000/api/v1`

Swagger/OpenAPI docs: `http://localhost:5000/api/v1/swagger`

### Production (Gunicorn)

```bash
gunicorn wsgi:application --bind 0.0.0.0:5000
```

## API Reference

All routes are prefixed with `/api/v1`.

### Menus

- `GET /menus/`: all menus.
- `GET /menus/week`: current ISO week.
- `GET /menus/week/<week>`: specific week (`1-52`).
- `GET /menus/today`: today only.
- `GET /menus/<YYYY-MM-DD>`: specific date.

Optional query parameter for all menu routes:

- `slack=true|false` (default `false`): decorate menu entries with Slack emoji aliases.

### Jobs

- `GET /jobs/`: list registered scheduler jobs.
- `GET /jobs/checkmail`: run mail retrieval now.
- `POST /jobs/parsemenus`: move old attachments to `menus/`, parse `.docx` files there, and rebuild/update DB entries.

## Scheduler Jobs

Defined in [scheduledTasks.py](scheduledTasks.py), weekdays unless noted:

- 09:30: fetch mail and parse attachments.
- Monday 10:55: extra fetch/parse run.
- 11:00: post today menu to Slack.
- Day 1 of month at 01:00: move `attachments/*` to `menus/`.

Important: In [app.py](app.py), the scheduler starts at process boot, so each app process instance will run its own scheduler.

## Data Format

Data is stored as:

```json
{
  "YYYY-MM-DD": [
    "Dish 1",
    "Dish 2",
    "Dish 3"
  ]
}
```

## Docker

Build and run:

```bash
docker build -t smaraturn .
docker run --rm -p 5000:5000 smaraturn
```

Note: [Dockerfile](Dockerfile) currently uses Python 3.7.1, while [Pipfile](Pipfile) requires 3.12 and lockfile packages target modern Python versions. Update the base image to a compatible Python (for example `python:3.12-slim`) before production use.

## Operational Notes and Caveats

- `attachments/` is created on-demand by [getmail.py](getmail.py).
- `menus/` is expected to exist and contain `.docx` files for manual parse endpoints.
- `stashMenus()` uses shell `mv attachments/* menus/`; if no matching files exist, shell behavior may vary.
- Date parsing in [menuParser.py](menuParser.py) assumes Icelandic/English month abbreviations and the current year.
- Week filtering in [app.py](app.py) uses `%W` (Monday-based week number), while `/menus/week` source uses ISO week from `isocalendar()`; edge-week behavior may differ around new year.

## Helpful Commands

Run parser manually for one file:

```bash
python menuParser.py menus/1-5okt.docx
```

Run Slack post manually:

```bash
python slackbot.py
```

Run mail fetch manually:

```bash
python getmail.py
```

## Troubleshooting

- `ModuleNotFoundError: secrets`:
  - Add `secrets.py` in project root.
- IMAP auth errors:
  - Verify mailbox credentials and provider settings.
- No menus for today:
  - Trigger `/api/v1/jobs/checkmail` then `/api/v1/jobs/parsemenus`.
  - Verify incoming email sender matches `getTrustedDomains()`.
- Emoji output missing:
  - Add `?slack=true` to menu routes.

