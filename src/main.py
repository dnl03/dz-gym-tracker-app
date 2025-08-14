from fastapi import FastAPI
from db.session import create_all
from api.auth import router as auth_router

app = FastAPI(title="GymTracker")

@app.on_event("startup")
def on_startup():
    create_all()

app.include_router(auth_router)
