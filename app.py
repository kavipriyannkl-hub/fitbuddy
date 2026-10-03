import os
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "plan": None
        }
    )


@app.post("/generate", response_class=HTMLResponse)
def generate_plan(
    request: Request,
    age: int = Form(..., ge=10, le=100),
    gender: str = Form(...),
    goal: str = Form(...),
    fitness_level: str = Form(...),
    equipment: str = Form(...),
    duration: str = Form(...)
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        plan_text = (
            "Error: GEMINI_API_KEY is missing. "
            "The service owner needs to configure the deployment environment."
        )

    else:
        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are FitBuddy, a professional AI fitness coach.

Create a safe, practical and personalized 7-day fitness plan.

User Details:
Age: {age}
Gender: {gender}
Fitness Goal: {goal}
Fitness Level: {fitness_level}
Available Equipment: {equipment}
Workout Duration: {duration}

Create the response using this structure:

FITBUDDY - PERSONALIZED 7-DAY FITNESS PLAN

User Goal:
Mention the fitness goal.

DAY 1
- Warm-up
- Exercises
- Sets and reps or duration
- Rest time
- Cool-down

DAY 2
- Warm-up
- Exercises
- Sets and reps or duration
- Rest time
- Cool-down

DAY 3
...

Continue until DAY 7.

Also include:

NUTRITION TIPS
Give 4 to 5 nutrition suggestions suitable for the user's goal.

RECOVERY TIPS
Give advice about sleep, hydration, stretching and rest.

SAFETY NOTE
Remind the user to stop exercising if they experience pain,
dizziness, unusual shortness of breath, or other concerning symptoms.

Keep the plan easy to understand.
Do not recommend extreme diets or unsafe exercises.
"""

            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
                contents=prompt
            )

            if response.text:
                plan_text = response.text
            else:
                plan_text = "Gemini returned an empty response."

        except Exception:
            plan_text = "Plan generation is temporarily unavailable. Please try again shortly."

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "plan": plan_text
        }
    )

@app.get('/healthz')
def health():
    return {'status': 'ok'}

