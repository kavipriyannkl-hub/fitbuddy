# FitBuddy

Personalized 7-day fitness plans built with FastAPI, Jinja2, and the Gemini API.

## Run locally

Use Python 3.13 or newer. Create a virtual environment, then run:

```sh
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own Gemini API key. Never commit `.env`.

```sh
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Health check: `/healthz`.

## Deploy on Render

Create a Render Blueprint from this repository using `render.yaml`, or create a free Python web service with:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health check: `/healthz`
- Secret environment variable: `GEMINI_API_KEY`
- Optional environment variable: `GEMINI_MODEL` (defaults to `gemini-3.5-flash-lite`)

Use a newly rotated key if an earlier key was shared. Store it only in the host's environment settings. Free Render services can sleep when inactive; Gemini availability and API quotas are separate.

## Data and safety

Form details are sent to Gemini to generate the plan. This app does not persist profiles. Fitness plans are general guidance. Provider errors are shown as a generic message to avoid disclosing credentials or internal details.
