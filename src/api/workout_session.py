from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import func

from db.session import get_session
from core.auth import get_current_user
from models.user import User
from models.workout_session import WorkoutSession
from schemas.workout_session import WorkoutSessionCreate
from models.exercise import Exercise
from models.workout_session_exercise import WorkoutSessionExercise
from schemas.workout_session_exercise import WorkoutSessionExerciseCreate
import uuid

router = APIRouter(prefix="/workout_sessions", tags=["sessions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_workout_session = session.exec(
        select(WorkoutSession).where(
            WorkoutSession.user_id == current_user.id,
            func.lower(WorkoutSession.name) == func.lower(data.name),
        )
    ).first()

    if user_workout_session:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sesja treningowa o podanej nazwie już istnieje!",
        )

    workout_session = WorkoutSession(user_id=current_user.id, name=data.name)
    session.add(workout_session)
    session.commit()
    session.refresh(workout_session)
    return {"detail": "Pomyślnie utworzono sesję treningową!"}



@router.post("/{session_id}/exercises", status_code=status.HTTP_201_CREATED)
def add_exercise_to_session(
    session_id: uuid.UUID,
    data: WorkoutSessionExerciseCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    
    exercise = db.exec(
        select(Exercise).where(Exercise.id == data.exercise_id)
    ).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Nie znaleziono ćwiczenia!")


    workout_session = db.exec(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
            )
    ).first()

    if not workout_session:
        raise HTTPException(status_code=404, detail="Sesja nie istnieje!")


    existing = db.exec(
        select(WorkoutSessionExercise).where(
            WorkoutSessionExercise.workout_session_id == session_id,
            WorkoutSessionExercise.exercise_id == data.exercise_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ćwiczenie już istnieje w tej sesji treningowej!")


    session_exercise = WorkoutSessionExercise(
        workout_session_id=session_id,
        exercise_id=data.exercise_id
    )

    db.add(session_exercise)
    db.commit()
    db.refresh(session_exercise)

    return {"detail": "Pomyślnie dodano ćwiczenie do sesji treningowej!"}


@router.delete("/{session_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_exercise_from_session(
    session_id: uuid.UUID,
    exercise_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workout_session = db.exec(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
    ).first()

    if not workout_session:
        raise HTTPException(status_code=404, detail="Brak dostępu do podanej sesji treningowej!")

    session_exercise = db.exec(
        select(WorkoutSessionExercise).where(
            WorkoutSessionExercise.workout_session_id == session_id,
            WorkoutSessionExercise.exercise_id == exercise_id,
        )
    ).first()

    if not session_exercise:
        raise HTTPException(status_code=404, detail="Brak dostępnych danych!")

    db.delete(session_exercise)
    db.commit()

    return {"detail": "Pomyślnie usunięto ćwiczenie z sesji treningowej!"}