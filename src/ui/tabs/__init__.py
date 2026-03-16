"""Package des onglets de l'interface."""

<<<<<<< HEAD
from .leaves_tab import LeavesTab
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
from .dashboard_tab import DashboardTab
from .structure_tab import StructureTab
from .teachers_tab import TeachersTab
from .activities_tab import ActivitiesTab
from .calendar_tab import CalendarTab
from .scheduling_tab import SchedulingTab
from .analysis_tab import AnalysisTab
<<<<<<< HEAD
from .reports_tab import ReportsTab
from .timetable_tab import TimetableTab
from .availability_tab import AvailabilityTab
from .users_tab import UsersTab

__all__ = [
    "DashboardTab",
    "StructureTab",
    "TeachersTab",
    "ActivitiesTab",
    "CalendarTab",
    "SchedulingTab",
    "AnalysisTab",
    "LeavesTab",
    "ReportsTab",
    "TimetableTab",
    "AvailabilityTab",
    "UsersTab",
]
from .rooms_tab import RoomsTab
=======
from .leaves_tab import LeavesTab
from .reports_tab import ReportsTab
from .timetable_tab import TimetableTab
from .users_tab import UsersTab           # ← AJOUTÉ

__all__ = [
    'DashboardTab',
    'StructureTab',
    'TeachersTab',
    'ActivitiesTab',
    'CalendarTab',
    'SchedulingTab',
    'AnalysisTab',
    'LeavesTab',
    'ReportsTab',
    'TimetableTab',
    'UsersTab',                            # ← AJOUTÉ
]
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
