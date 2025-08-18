from fastapi import FastAPI
from db.session import create_all, engine
from db.exercise_repository import seed_exercises
from api.auth import router as auth_router
from api.profile import router as profile_router
from sqlmodel import Session


app = FastAPI(title="GymTracker")

@app.on_event("startup")
def on_startup():
    create_all()
    with Session(engine) as session:
        seed_exercises(session)


app.include_router(auth_router)
app.include_router(profile_router)
