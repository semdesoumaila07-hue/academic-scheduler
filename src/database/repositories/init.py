"""
Package des repositories.

Les repositories fournissent une couche d'abstraction entre
les modèles SQLAlchemy et les entités métier.
"""

from .base_repository import BaseRepository
from .university_repository import UniversityRepository
from .ufr_repository import UFRRepository
from .program_repository import ProgramRepository
from .cohort_repository import CohortRepository
from .teacher_repository import TeacherRepository
from .student_repository import StudentRepository
from .activity_repository import ActivityRepository
from .schedule_repository import ScheduleRepository
from .leave_request_repository import LeaveRequestRepository
from .calendar_repository import CalendarRepository
from .holiday_repository import HolidayRepository
from .vacation_period_repository import VacationPeriodRepository

__all__ = [
    'BaseRepository',
    'UniversityRepository',
    'UFRRepository',
    'ProgramRepository',
    'CohortRepository',
    'TeacherRepository',
    'StudentRepository',
    'ActivityRepository',
    'ScheduleRepository',
    'LeaveRequestRepository',
    'CalendarRepository',
    'HolidayRepository',
    'VacationPeriodRepository',
]