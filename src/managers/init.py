"""
Package des managers.

Les managers coordonnent les services et repositories pour
fournir des opérations de haut niveau.
"""

from .structure_manager import StructureManager
from .activity_manager import ActivityManager
from .schedule_generator import ScheduleGenerator

__all__ = [
    'StructureManager',
    'ActivityManager',
    'ScheduleGenerator',
]