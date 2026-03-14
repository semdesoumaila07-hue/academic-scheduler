"""
Package des entités métier du système d'ordonnancement académique.

Ce package contient toutes les classes représentant les entités du domaine :
- Structure universitaire : University, UFR, Program, Cohort
- Acteurs : Teacher, Student
- Activités : AcademicActivity, ScheduleSlot
- Congés : LeaveRequest
- Calendrier : AcademicCalendar, Holiday, VacationPeriod
"""

from .university import University
from .ufr import UFR
from .program import Program
from .cohort import Cohort
from .teacher import Teacher
from .student import Student
from .academic_activity import AcademicActivity
from .schedule_slot import ScheduleSlot
from .leave_request import LeaveRequest
from .academic_calendar import AcademicCalendar
from .holiday import Holiday
from .vacation_period import VacationPeriod

__all__ = [
    'University',
    'UFR',
    'Program',
    'Cohort',
    'Teacher',
    'Student',
    'AcademicActivity',
    'ScheduleSlot',
    'LeaveRequest',
    'AcademicCalendar',
    'Holiday',
    'VacationPeriod',
]