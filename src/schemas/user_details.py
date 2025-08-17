from typing import Optional

from sqlmodel import SQLModel
from core.validators import WeightKg, HeightCm, BodyFatPct, CircuitCm


class UserDetailsUpdate(SQLModel):
    weight_kg: Optional[WeightKg]
    height_cm: Optional[HeightCm]

    bf_pct: Optional[BodyFatPct]
    biceps_cm: Optional[CircuitCm]
    waist_cm: Optional[CircuitCm]
    chest_cm: Optional[CircuitCm]
    thigh_cm: Optional[CircuitCm]
    calf_cm: Optional[CircuitCm]


class UserDetailsRead(SQLModel):
    model_config = {"from_attributes": True}
    weight_kg: WeightKg
    height_cm: HeightCm
    bf_pct: BodyFatPct
    biceps_cm: CircuitCm
    waist_cm: CircuitCm
    chest_cm: CircuitCm
    thigh_cm: CircuitCm
    calf_cm: CircuitCm
