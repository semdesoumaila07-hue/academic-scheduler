"""
Repositories pour l'accès aux données.
"""
from .base_repository import BaseRepository
from .activity_repository import ActivityRepository
from .calendar_repository import CalendarRepository
from .cohort_repository import CohortRepository
from .holiday_repository import HolidayRepository
from .leave_request_repository import LeaveRequestRepository
from .constraint_report_repository import ConstraintReportRepository
from .program_repository import ProgramRepository
from .schedule_repository import ScheduleRepository
<<<<<<< HEAD
from .statistics_repository import StatisticsRepository
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
from .student_repository import StudentRepository
from .teacher_repository import TeacherRepository
from .teacher_availability_repository import TeacherAvailabilityRepository
from .ufr_repository import UFRRepository
from .university_repository import UniversityRepository
from .vacation_period_repository import VacationPeriodRepository
from .user_repository import UserRepository
from .role_repository import RoleRepository
from .permission_repository import PermissionRepository

__all__ = [
    'BaseRepository',
    'ActivityRepository',
    'CalendarRepository',
    'CohortRepository',
    'HolidayRepository',
    'LeaveRequestRepository',
    'ConstraintReportRepository',
    'ProgramRepository',
    'ScheduleRepository',
<<<<<<< HEAD
    'StatisticsRepository',
    'ProgramRepository',
    'ScheduleRepository',
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    'StudentRepository',
    'TeacherRepository',
    'TeacherAvailabilityRepository',
    'UFRRepository',
    'UniversityRepository',
    'VacationPeriodRepository',
    'UserRepository',
    'RoleRepository',
    'PermissionRepository',
    'PermissionRepository',
]
