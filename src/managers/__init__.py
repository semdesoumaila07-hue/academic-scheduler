"""
Package managers — exports des managers utilisés par l'application.
"""
from .activity_manager import ActivityManager
from .structure_manager import StructureManager
from .schedule_generator import ScheduleGenerator

__all__ = [
    'ActivityManager',
    'StructureManager',
    'ScheduleGenerator',
]
