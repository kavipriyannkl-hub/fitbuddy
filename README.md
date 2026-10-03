# FitBuddy – AI Fitness Plan Generator

FitBuddy follows the supplied project guide: personalized 7-day workouts, feedback-based revisions, nutrition/recovery tips, saved profiles and plans, and a coach dashboard. Built with FastAPI, Jinja2, Google Gemini, SQLAlchemy and SQLite.

## Run locally

Python 3.12 or newer:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Set `GEMINI_API_KEY`, `ADMIN_USERNAME` and a strong `ADMIN_PASSWORD`. No credentials are included in the repository.

```sh
uvicorn app.main:app --reload --no-access-log
```

Open http://127.0.0.1:8000. API documentation: `/docs`. Health check: `/healthz`. Database tables are created on startup. Data remains in `fitbuddy.db` between local restarts.

## Features and routes

| Route | Purpose |
| --- | --- |
| `GET /` | Name, age, weight, goal, intensity, experience, equipment and duration form |
| `POST /generate-workout` | Generate and save a workout and nutrition tip |
| `GET /plans/{token}` | Private result page and full plan history |
| `POST /submit-feedback` | Generate a revised plan without overwriting the original |
| `GET/POST /nutrition-tip` | Standalone goal-based nutrition/recovery tip |
| `GET /view-all-users` | Password-protected coach dashboard with original and updated plans |
| `POST /api/workouts` | JSON profile → plan, tip and private access token |
| `POST /api/feedback` | JSON access token and feedback → revised plan/version |
| `GET /api/nutrition-tip?goal=muscle%20gain` | JSON nutrition tip |
| `GET /api/users` | Authenticated coach API with profiles and plan history |

Save/bookmark the private plan URL after generating. The token acts as access to the plan: anyone with the link can read and revise it. Unknown tokens return 404; users cannot look up profiles by sequential IDs. Coach access is disabled until both admin environment variables are set. Use HTTPS when hosting.

The old single-page prototype has been replaced with the guide's modular `app/main.py`, `app/routes.py`, model/database/AI modules and separate input, result and admin templates. Existing `uvicorn app:app` commands still work through the package export.

## Gemini configuration

Workout generation and feedback use `GEMINI_WORKOUT_MODEL`; standalone nutrition uses `GEMINI_TIP_MODEL`. Defaults are `gemini-3.8-flash` and `gemini-3.5-flash-lite`, listed by Google's current [model documentation](https://ai.google.dev/gemini-api/docs/models). `GEMINI_MODEL` remains a legacy fallback when `GEMINI_WORKOUT_MODEL` is unset. The reference's older Gemini 1.5 examples are replaced with configurable current models using `google-genai`. Select a model available to your API account. Calls have a 60-second timeout. Missing keys, provider failures and empty responses show a generic error; failed operations do not save partial users or plan revisions.

## Deploy on Render

`render.yaml` preserves a free demonstration service. Set the Gemini key and admin credentials in Render's environment settings. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-access-log`.

**Free service files are temporary. Saved users and plans can be lost on redeploy/restart.** For durable hosted storage, configure a persistent disk on a supporting service, mount it at `/var/data`, and set `DATABASE_URL=sqlite:////var/data/fitbuddy.db`. That hosting option may cost money; this repository does not purchase or deploy it. Back up the SQLite database. Use a single instance for SQLite. The database URL currently supports SQLite only.

## Data handling

Age, weight, fitness goal, intensity, experience, equipment and duration are sent to Google Gemini. Names are stored locally and are excluded from the workout prompt. Feedback and the prior plan are sent to Gemini for revisions; users should avoid entering private medical details. Profiles and plan versions are stored in SQLite and visible to the authorized coach. HTML output is escaped, private pages disable caching and referrer sharing, and the recommended server command disables access logs so private plan tokens do not enter those logs. Configure the hosting proxy similarly. Fitness output is AI-generated general guidance, not medical advice.

## Test

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use an isolated in-memory database and mocked AI; they cover form/API generation, validation, feedback history, failure rollback, private access, admin authorization and escaping. They do not prove live Gemini availability. See `docs/` for the seven project phases, acceptance criteria and a demonstration script. Actual team details, live demo evidence and API validation must be supplied when completing an institutional submission.
