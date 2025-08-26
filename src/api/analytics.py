from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlmodel import Session, select

from typing import Optional, Union
from db.session import get_session
from core.auth import get_current_user
from datetime import date, datetime, timedelta
from models.user import User


from models.exercise import Exercise
from models.workout_set import WorkoutSet
from models.workout_session import WorkoutSession
from models.workout_session_exercise import WorkoutSessionExercise
from models.one_rep_max import OneRepMax

from schemas.workout_set import WorkoutSetRead
from schemas.one_rep_max import OneRepMaxRead


router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get(
    "",
    response_model=Union[list[WorkoutSetRead], list[OneRepMaxRead]],
    status_code=status.HTTP_200_OK,
)
def analyze_sets(
    exercise_id: int = Query(..., description="ID ćwiczenia"),
    a_type: str = Query(..., regex="^(sets|1rm)$"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    exercise = db.exec(select(Exercise).where(Exercise.id == exercise_id)).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Brak danych dla wybranego ćwiczenia!")

    today = date.today()
    if not date_to:
        date_to = today
    if not date_from:
        date_from = today - timedelta(days=180)

    if date_from > date_to or date_to > today:
        raise HTTPException(status_code=400, detail="Niepoprawny zakres dat!")

    date_from_dt = datetime.combine(date_from, datetime.min.time())
    date_to_dt = datetime.combine(date_to, datetime.max.time())

    if a_type == "sets":
        stmt = (
            select(
                WorkoutSet.id,
                Exercise.name.label("exercise_name"),
                WorkoutSet.reps,
                WorkoutSet.weight_kg,
                WorkoutSet.volume,
                WorkoutSet.intensity,
                WorkoutSet.created_at
            )
            .join(WorkoutSessionExercise, WorkoutSessionExercise.id == WorkoutSet.workout_session_exercise_id)
            .join(WorkoutSession, WorkoutSession.id == WorkoutSessionExercise.workout_session_id)
            .join(Exercise, Exercise.id == WorkoutSessionExercise.exercise_id)
            .where(
                WorkoutSessionExercise.exercise_id == exercise_id,
                WorkoutSession.user_id == current_user.id,
                WorkoutSet.created_at >= date_from_dt,
                WorkoutSet.created_at <= date_to_dt,
            )
            .order_by(WorkoutSet.created_at)
        )
        return db.exec(stmt).all()

    elif a_type == "1rm":
        stmt = (
            select(
                OneRepMax.id,
                Exercise.name.label("exercise_name"),
                OneRepMax.weight,
                OneRepMax.created_at,
            )
            .join(Exercise, Exercise.id == OneRepMax.exercise_id)
            .where(
                OneRepMax.exercise_id == exercise_id,
                OneRepMax.user_id == current_user.id,
                OneRepMax.created_at >= date_from_dt,
                OneRepMax.created_at <= date_to_dt,
            )
            .order_by(OneRepMax.created_at)
        )

        return db.exec(stmt).all()
