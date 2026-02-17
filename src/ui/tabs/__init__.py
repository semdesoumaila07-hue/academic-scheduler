"""Package des onglets de l'interface."""

from .dashboard_tab import DashboardTab
from .structure_tab import StructureTab
from .teachers_tab import TeachersTab
from .activities_tab import ActivitiesTab
from .calendar_tab import CalendarTab
from .scheduling_tab import SchedulingTab
from .analysis_tab import AnalysisTab
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