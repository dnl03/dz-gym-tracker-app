from sqlmodel import Session, select
from models.exercise import Exercise

SAMPLE_EXERCISES = [
    {"name": "Przysiad ze sztangą (Back Squat)", "description": "Przysiad ze sztangą; pracują uda i pośladki."},
    {"name": "Wyciskanie sztangi leżąc (Bench Press)", "description": "Pchanie sztangi na ławce; klatka, barki, tricepsy."},
    {"name": "Martwy ciąg (Deadlift)", "description": "Zawias biodrowy; tylny łańcuch: prostowniki, pośladki, dwugłowe."},
    {"name": "Wyciskanie sztangi nad głowę (Overhead Press)", "description": "Wyciskanie stojąc; barki, tricepsy, stabilizacja core."},
    {"name": "Wiosłowanie sztangą (Barbell Row)", "description": "Poziome przyciąganie; środek pleców i bicepsy."},
    {"name": "Podciąganie na drążku (Pull-Up)", "description": "Pionowe przyciąganie; najszerszy grzbietu i bicepsy."},
    {"name": "Pompki (Push-Up)", "description": "Pchanie ciężaru ciała; klatka, barki, tricepsy."},
    {"name": "Deska (Plank)", "description": "Izometria core; brzuch i stabilizacja tułowia."},
]

def seed_exercises(session: Session):
    cnt = len(session.exec(select(Exercise)).all())
    if cnt > 0:
        return
    session.add_all([Exercise(**exercise) for exercise in SAMPLE_EXERCISES])
    session.commit()


def list_all_exercises(session: Session) -> list[Exercise]:
    stmt = select(Exercise)
    return session.exec(stmt).all()