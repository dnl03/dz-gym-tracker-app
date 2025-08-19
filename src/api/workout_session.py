from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import func

from db.session import get_session
from core.auth import get_current_user
from models.user import User
from models.workout_session import WorkoutSession
from schemas.workout_session import WorkoutSessionCreate

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
