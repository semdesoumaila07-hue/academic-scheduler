"""
Package des services métier.

Les services contiennent la logique métier de l'application :
- Algorithme Pfair pour l'ordonnancement
- Gestion du calendrier académique
- Gestion des demandes de congés
- Calcul des retards académiques
- Statistiques et KPIs du Dashboard
"""

from .pfair_scheduler import PfairScheduler
from .calendar_service import CalendarService
from .leave_service import LeaveService
from .delay_calculator import DelayCalculator
from .dashboard_service import DashboardService

__all__ = [
    'PfairScheduler',
    'CalendarService',
    'LeaveService',
    'DelayCalculator',
    'DashboardService',
]
