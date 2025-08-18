from fastapi import APIRouter, Depends
from sqlmodel import Session
from schemas.exercise import ExerciseRead

from db.session import get_session
from db.exercise_repository import list_all_exercises

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/all", response_model=list[ExerciseRead])
def list_exercises(session: Session = Depends(get_session)):
    """Endpoint pośredni, do pobierania wszystkich ćwiczeń i wyświetlenia w kliencie API"""
    return list_all_exercises(session)
