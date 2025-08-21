from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from schemas.one_rep_max import OneRepMaxCreate
from models.user import User
from models.one_rep_max import OneRepMax
from models.exercise import Exercise
from db.session import get_session

from core.auth import get_current_user
from datetime import datetime



router = APIRouter(prefix="/max_rep", tags=["add_max_rep"])

@router.post("", status_code=status.HTTP_201_CREATED)
def add_max_rep(
    data: OneRepMaxCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if (exercise := session.get(Exercise, data.exercise_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono ćwiczenia!")

    stmt = (
        select(OneRepMax)
        .where(
            OneRepMax.user_id == current_user.id,
            OneRepMax.exercise_id == exercise.id
        )
        .order_by(OneRepMax.created_at.desc())
    )
    last_max_rep = session.exec(stmt).first()
    if last_max_rep and (datetime.now() - last_max_rep.created_at).days < 7:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Aktualizacja One Rep Max możliwa raz na 7 dni!"
        )

    one_rep_max = OneRepMax(
        user_id=current_user.id,
        exercise_id=exercise.id,
        weight=data.weight,
        video_url=data.video_url
    )
    session.add(one_rep_max)
    session.commit()
    session.refresh(one_rep_max)

    return {"detail": "Pomyślnie dodano One Rep Max!"}