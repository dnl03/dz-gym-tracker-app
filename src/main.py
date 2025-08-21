from fastapi import FastAPI
from db.session import create_all, engine
from db.exercise_repository import seed_exercises
from api.auth import router as auth_router
from api.profile import router as profile_router
from api.exercises import router as exercises_router
from api.max_rep import router as max_rep_router
from api.workout_session import router as workout_session_router
from sqlmodel import Session


app = FastAPI(title="GymTracker")

@app.on_event("startup")
def on_startup():
    create_all()
    with Session(engine) as session:
        seed_exercises(session)


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(exercises_router)
app.include_router(max_rep_router)
app.include_router(workout_session_router)
