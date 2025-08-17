from fastapi import APIRouter, Depends, status
from schemas.user_details import UserDetailsUpdate
from sqlmodel import Session, select

from models.user import User
from db.session import get_session
from core.auth import get_current_user
from models.user_details import UserDetail


router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/edit-profile", status_code=status.HTTP_200_OK)
def edit_profile(
    data: UserDetailsUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    last_user_details = session.exec(
        select(UserDetail)
        .where(UserDetail.user_id == current_user.id)
        .order_by(UserDetail.created_at.desc())
        .limit(1)
    ).first()

    new_user_details = UserDetail(
        user_id=current_user.id,
        weight_kg = data.weight_kg  if data.weight_kg  is not None else last_user_details.weight_kg,
        height_cm= data.height_cm if data.height_cm is not None else last_user_details.height_cm,
        bf_pct    = data.bf_pct     if data.bf_pct     is not None else last_user_details.bf_pct,
        biceps_cm = data.biceps_cm  if data.biceps_cm  is not None else last_user_details.biceps_cm,
        waist_cm  = data.waist_cm   if data.waist_cm   is not None else last_user_details.waist_cm,
        thigh_cm  = data.thigh_cm   if data.thigh_cm   is not None else last_user_details.thigh_cm,
        chest_cm  = data.chest_cm   if data.chest_cm   is not None else last_user_details.chest_cm,
        calf_cm   = data.calf_cm    if data.calf_cm    is not None else last_user_details.calf_cm,

    )

    session.add(new_user_details)
    session.commit()
    return {"detail": "Dane zaktualizowane pomyślnie!"}