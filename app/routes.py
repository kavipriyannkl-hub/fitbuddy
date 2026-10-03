import os
import secrets
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from . import ai
from .database import get_db
from .models import User, Plan

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")
security = HTTPBasic(auto_error=False)
Goal = Literal["weight loss", "muscle gain", "general wellness", "improve endurance", "increase strength"]

class Profile(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=10, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Literal["low", "medium", "high"]
    fitness_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    equipment: Literal["no equipment", "home equipment", "dumbbells", "full gym"] = "no equipment"
    duration: Literal[20, 30, 45, 60] = 30

    @field_validator("duration", mode="before")
    @classmethod
    def parse_duration(cls, value):
        return int(value) if isinstance(value, str) and value.isdigit() else value

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value):
        return value.strip() if isinstance(value, str) else value

class Feedback(BaseModel):
    access_token: str
    feedback: str = Field(min_length=1, max_length=2000)

    @field_validator("feedback", mode="before")
    @classmethod
    def trim_feedback(cls, value):
        return value.strip() if isinstance(value, str) else value

def admin(credentials: HTTPBasicCredentials | None = Depends(security)):
    username, password = os.getenv("ADMIN_USERNAME"), os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise HTTPException(503, "Admin access has not been configured.")
    if credentials is None or not (
        secrets.compare_digest(credentials.username.encode(), username.encode()) and
        secrets.compare_digest(credentials.password.encode(), password.encode())):
        raise HTTPException(401, "Admin login required", headers={"WWW-Authenticate": "Basic"})

def owned_user(db, token):
    user = db.scalar(select(User).where(User.access_token == token))
    if user is None:
        raise HTTPException(404, "Plan not found")
    return user

def create_plan(db, profile):
    content = ai.workout(profile.model_dump(exclude={"name"}))
    tip = ai.nutrition(profile.goal)
    user = User(**profile.model_dump(), access_token=secrets.token_urlsafe(32))
    user.plans.append(Plan(content=content, nutrition_tip=tip))
    db.add(user)
    db.commit()
    return user

def revise_plan(db, user, feedback):
    previous = user.plans[-1]
    profile = {key: getattr(user, key) for key in Profile.model_fields if key != "name"}
    content = ai.workout(profile, previous.content, feedback)
    user.plans.append(Plan(content=content, nutrition_tip=previous.nutrition_tip, feedback=feedback))
    db.commit()

def page(request, name, **context):
    response = templates.TemplateResponse(request=request, name=name, context=context)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return page(request, "index.html")

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(request: Request, profile: Profile = Form(), db: Session = Depends(get_db)):
    try:
        user = create_plan(db, profile)
    except ai.GenerationError as exc:
        return page(request, "index.html", error=str(exc), values=profile.model_dump())
    return RedirectResponse(f"/plans/{user.access_token}", status_code=303)

@router.get("/plans/{token}", response_class=HTMLResponse)
def result(request: Request, token: str, db: Session = Depends(get_db)):
    user = owned_user(db, token)
    return page(request, "result.html", user=user, plan=user.plans[-1])

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, payload: Feedback = Form(), db: Session = Depends(get_db)):
    user = owned_user(db, payload.access_token)
    try:
        revise_plan(db, user, payload.feedback)
    except ai.GenerationError as exc:
        return page(request, "result.html", user=user, plan=user.plans[-1], error=str(exc))
    return RedirectResponse(f"/plans/{user.access_token}", status_code=303)

@router.get("/nutrition-tip", response_class=HTMLResponse)
def tip_page(request: Request):
    return page(request, "nutrition.html")

@router.post("/nutrition-tip", response_class=HTMLResponse)
def tip(request: Request, goal: Goal = Form()):
    try:
        return page(request, "nutrition.html", tip=ai.nutrition(goal), goal=goal)
    except ai.GenerationError as exc:
        return page(request, "nutrition.html", error=str(exc), goal=goal)

@router.get("/view-all-users", response_class=HTMLResponse, dependencies=[Depends(admin)])
def all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).options(selectinload(User.plans)).order_by(User.id.desc())).all()
    return page(request, "all_users.html", users=users)

@router.post("/api/workouts", status_code=201)
def api_workout(profile: Profile, db: Session = Depends(get_db)):
    try:
        user = create_plan(db, profile)
        return {"access_token": user.access_token, "plan": user.plans[-1].content, "nutrition_tip": user.plans[-1].nutrition_tip}
    except ai.GenerationError as exc:
        raise HTTPException(503, str(exc))

@router.post("/api/feedback")
def api_feedback(payload: Feedback, db: Session = Depends(get_db)):
    user = owned_user(db, payload.access_token)
    try:
        revise_plan(db, user, payload.feedback)
        return {"plan": user.plans[-1].content, "version": len(user.plans)}
    except ai.GenerationError as exc:
        raise HTTPException(503, str(exc))

@router.get("/api/nutrition-tip")
def api_tip(goal: Goal):
    try:
        return {"tip": ai.nutrition(goal)}
    except ai.GenerationError as exc:
        raise HTTPException(503, str(exc))

@router.get("/healthz")
def health():
    return {"status": "ok"}

@router.get("/api/users", dependencies=[Depends(admin)])
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).options(selectinload(User.plans)).order_by(User.id.desc())).all()
    return [{"id": user.id, "name": user.name, "age": user.age, "weight": user.weight,
             "goal": user.goal, "intensity": user.intensity,
             "plans": [{"content": plan.content, "nutrition_tip": plan.nutrition_tip,
                        "feedback": plan.feedback, "created_at": plan.created_at} for plan in user.plans]}
            for user in users]
