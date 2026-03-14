"""
Constantes et énumérations du système.

⚠️  NE PAS redéfinir les enums ici — elles sont définies dans
    src/database/models.py et enregistrées dans SQLAlchemy.
    Ce fichier les réexporte simplement sous les deux noms
    (avec et sans suffixe Enum) pour compatibilité.
"""

# ── Source unique : src/database/models.py ────────────────────────
from src.database.models import (
    ProgramLevelEnum,
    ActivityTypeEnum,
    ActivityStatusEnum,
    PriorityEnum,
    TeacherStatusEnum,
    LeaveStatusEnum,
    LeaveTypeEnum,
    VacationTypeEnum,
)

# ── Alias courts (compatibilité avec l'ancien code) ───────────────
ProgramLevel   = ProgramLevelEnum
ActivityType   = ActivityTypeEnum
ActivityStatus = ActivityStatusEnum
TeacherStatus  = TeacherStatusEnum
LeaveStatus    = LeaveStatusEnum
LeaveType      = LeaveTypeEnum
VacationType   = VacationTypeEnum

__all__ = [
    "ProgramLevelEnum",   "ProgramLevel",
    "ActivityTypeEnum",   "ActivityType",
    "ActivityStatusEnum", "ActivityStatus",
    "PriorityEnum",
    "TeacherStatusEnum",  "TeacherStatus",
    "LeaveStatusEnum",    "LeaveStatus",
    "LeaveTypeEnum",      "LeaveType",
    "VacationTypeEnum",   "VacationType",
]