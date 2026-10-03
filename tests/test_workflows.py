import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, Plan
from app import ai

PROFILE = dict(name="Alex", age=24, weight=65, goal="muscle gain", intensity="medium", fitness_level="beginner", equipment="dumbbells", duration=30)

@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    def db():
        with sessions() as session:
            yield session
    app.dependency_overrides[get_db] = db
    monkeypatch.setenv("ADMIN_USERNAME", "coach")
    monkeypatch.setenv("ADMIN_PASSWORD", "test-only-password")
    monkeypatch.setattr(ai, "workout", lambda profile, previous=None, feedback=None: "DAY 1 through DAY 7" if previous is None else "Revised: " + feedback)
    monkeypatch.setattr(ai, "nutrition", lambda goal: "Nutrition tip for " + goal)
    with TestClient(app) as client:
        yield client, sessions
    app.dependency_overrides.clear()
    engine.dispose()

def test_browser_create_feedback_and_admin_history(client):
    browser, sessions = client
    response = browser.post("/generate-workout", data=PROFILE)
    assert response.status_code == 200
    assert "DAY 1 through DAY 7" in response.text
    token = response.url.path.split("/")[-1]
    response = browser.post("/submit-feedback", data={"access_token": token, "feedback": "more rest days"})
    assert "Revised: more rest days" in response.text
    assert "Your plan history" in response.text
    with sessions() as db:
        user = db.scalar(select(User))
        assert user.weight == 65
        assert len(user.plans) == 2
        assert user.plans[0].content == "DAY 1 through DAY 7"
    assert browser.get("/view-all-users").status_code == 401
    dashboard = browser.get("/view-all-users", auth=("coach", "test-only-password"))
    assert dashboard.status_code == 200
    assert "Original plan" in dashboard.text and "Updated plan" in dashboard.text
    assert browser.get("/api/users").status_code == 401
    users = browser.get("/api/users", auth=("coach", "test-only-password"))
    assert len(users.json()[0]["plans"]) == 2
    assert "access_token" not in users.json()[0]
    assert dashboard.headers["Cache-Control"] == "no-store"

def test_api_workflows_and_validation(client):
    browser, _ = client
    response = browser.post("/api/workouts", json=PROFILE)
    assert response.status_code == 201
    token = response.json()["access_token"]
    assert browser.post("/api/feedback", json={"access_token": token, "feedback": "more cardio"}).json()["version"] == 2
    assert browser.get("/api/nutrition-tip", params={"goal": "muscle gain"}).json()["tip"].endswith("muscle gain")
    assert browser.post("/api/workouts", json={**PROFILE, "weight": -1}).status_code == 422
    assert browser.post("/api/workouts", json={**PROFILE, "intensity": "unsafe"}).status_code == 422
    assert browser.post("/api/workouts", json={**PROFILE, "name": "  "}).status_code == 422
    assert browser.post("/api/feedback", json={"access_token": token, "feedback": " "}).status_code == 422
    assert browser.get("/plans/unknown").status_code == 404
    assert browser.post("/api/feedback", json={"access_token": "unknown", "feedback": "hello"}).status_code == 404

def test_failed_generation_does_not_save_partial_data(client, monkeypatch):
    browser, sessions = client
    def fail(*args):
        raise ai.GenerationError("Try again")
    monkeypatch.setattr(ai, "nutrition", fail)
    assert browser.post("/api/workouts", json=PROFILE).status_code == 503
    with sessions() as db:
        assert db.scalar(select(User)) is None

def test_failed_revision_preserves_previous_plan(client, monkeypatch):
    browser, sessions = client
    token = browser.post("/api/workouts", json=PROFILE).json()["access_token"]
    def fail(*args):
        raise ai.GenerationError("Try again")
    monkeypatch.setattr(ai, "workout", fail)
    assert browser.post("/api/feedback", json={"access_token": token, "feedback": "more rest"}).status_code == 503
    with sessions() as db:
        assert len(db.scalars(select(Plan)).all()) == 1

def test_admin_fails_closed_and_escapes_generated_content(client, monkeypatch):
    browser, _ = client
    monkeypatch.delenv("ADMIN_PASSWORD")
    assert browser.get("/view-all-users").status_code == 503
    monkeypatch.setattr(ai, "workout", lambda *args: '<script>alert("x")</script>')
    response = browser.post("/generate-workout", data=PROFILE)
    assert '&lt;script&gt;' in response.text
    assert '<script>alert("x")</script>' not in response.text

def test_tip_page_and_home(client):
    browser, _ = client
    assert browser.get("/").status_code == 200
    assert "Weight (kg)" in browser.get("/").text
    assert "Nutrition tip for weight loss" in browser.post("/nutrition-tip", data={"goal": "weight loss"}).text
    assert browser.get("/healthz").json() == {"status": "ok"}

def test_provider_missing_key_and_empty_response(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ai.GenerationError, match="not configured"):
        ai.generate("test")

def test_provider_empty_and_exception_are_safe(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    class FakeClient:
        def __init__(self, **kwargs):
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def generate_content(self, **kwargs):
            return type("Response", (), {"text": " "})()
    monkeypatch.setattr(ai.genai, "Client", FakeClient)
    with pytest.raises(ai.GenerationError, match="temporarily unavailable"):
        ai.generate("test")
    def fail(**kwargs):
        raise RuntimeError("sensitive internal provider error")
    monkeypatch.setattr(ai.genai, "Client", fail)
    with pytest.raises(ai.GenerationError) as error:
        ai.generate("test")
    assert "sensitive" not in str(error.value)
