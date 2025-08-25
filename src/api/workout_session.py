from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from sqlalchemy import func

from db.session import get_session
from core.auth import get_current_user
from models.user import User
from models.workout_session import WorkoutSession
from schemas.workout_session import WorkoutSessionCreate
from models.exercise import Exercise
from models.workout_session_exercise import WorkoutSessionExercise
from schemas.workout_session_exercise import WorkoutSessionExerciseCreate
from schemas.workout_set import WorkoutSetCreate, WorkoutSetUpdate
from models.workout_set import WorkoutSet
from models.one_rep_max import OneRepMax
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
        raise HTTPException(status_code=404, detail="Brak dostępu do podanej sesji treningowej!")


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

    # remove all sets related to the exercise
    exercise_sets = db.exec(
        select(WorkoutSet).where(
            WorkoutSet.workout_session_exercise_id == session_exercise.id
        )
    ).all()

    for workout_set in exercise_sets:
        db.delete(workout_set)
    db.commit()

    # remove the exercies from session
    db.delete(session_exercise)
    db.commit()

    return {"detail": "Pomyślnie usunięto ćwiczenie z sesji treningowej!"}


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: uuid.UUID,
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


    #remove all exercises related to the workout session
    session_exercises = db.exec(
        select(WorkoutSessionExercise).where(
            WorkoutSessionExercise.workout_session_id == session_id
        )
    ).all()

    #remove all sets related to the workout session
    db.exec(
    delete(WorkoutSet).where(
            WorkoutSet.workout_session_exercise_id.in_([se.id for se in session_exercises])
        )
    )
    db.commit()

    for session_exercise in session_exercises:
        # remove all sets related to the exercise
        db.delete(session_exercise)

    db.commit()


    #remove the workout session itself
    db.delete(workout_session)
    db.commit()

    return {"detail": "Pomyślnie usunięto sesję treningową!"}


@router.post("/{session_id}/exercises/{exercise_id}/sets", status_code=status.HTTP_201_CREATED)
def add_set_to_exercise(
    session_id: uuid.UUID,
    exercise_id: int,
    data: WorkoutSetCreate,
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

    last_max_rep = db.exec(
        select(OneRepMax)
        .where(
            OneRepMax.user_id == current_user.id,
            OneRepMax.exercise_id == exercise_id,
        )
        .order_by(OneRepMax.created_at.desc())
    ).first()

    intensity = (last_max_rep.weight / data.weight_kg) if last_max_rep else 1
    volume = data.weight_kg * data.reps

    workout_set = WorkoutSet(
        workout_session_exercise_id=session_exercise.id,
        weight_kg=data.weight_kg,
        reps=data.reps,
        intensity=intensity,
        volume=volume,
    )

    db.add(workout_set)
    db.commit()
    db.refresh(workout_set)

    return {"detail": "Pomyślnie dodano serię!"}


@router.patch(
    "/{session_id}/exercises/{exercise_id}/sets/{set_id}",
    status_code=status.HTTP_200_OK,
)
def update_set(
    session_id: uuid.UUID,
    exercise_id: int,
    set_id: int,
    data: WorkoutSetUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Check if session exists and belongs to user
    workout_session = db.exec(
        select(WorkoutSession).where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
    ).first()
    if not workout_session:
        raise HTTPException(
            status_code=404, detail="Brak dostępu do podanej sesji treningowej!"
        )

    # Check if exercise belongs to this session
    session_exercise = db.exec(
        select(WorkoutSessionExercise).where(
            WorkoutSessionExercise.workout_session_id == session_id,
            WorkoutSessionExercise.exercise_id == exercise_id,
        )
    ).first()
    if not session_exercise:
        raise HTTPException(
            status_code=404, detail="Brak powiązanego ćwiczenia!"
        )

    #Check if set exists and belongs to this exercise
    workout_set = db.exec(
        select(WorkoutSet).where(
            WorkoutSet.id == set_id,
            WorkoutSet.workout_session_exercise_id == session_exercise.id,
        )
    ).first()
    if not workout_set:
        raise HTTPException(
            status_code=404, detail="Brak odpowiedniej serii treningowej!"
        )
    
    if data.reps is None and data.weight_kg is None:
        raise HTTPException(
            status_code=400, detail="Brak danych do aktualizacji!"
        )

    if data.reps is not None:
        workout_set.reps = data.reps
    if data.weight_kg is not None:
        workout_set.weight_kg = data.weight_kg

   # recalculation volume
    workout_set.volume = workout_set.weight_kg * workout_set.reps

    # 6. Przeliczenie intensity (sprawdź czy user ma 1RM)
    last_max_rep = db.exec(
        select(OneRepMax).where(
            OneRepMax.user_id == current_user.id,
            OneRepMax.exercise_id == exercise_id,
        ).order_by(OneRepMax.created_at.desc())
    ).first()

    workout_set.intensity = (last_max_rep.weight / data.weight_kg) if last_max_rep else 1

    db.add(workout_set)
    db.commit()

    return {"detail": "Seria zaktualizowana pomyślnie!"}
