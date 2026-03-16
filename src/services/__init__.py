"""
Package des services métier.

Les services contiennent la logique métier de l'application :
- Algorithme Pfair pour l'ordonnancement
- Gestion du calendrier académique
- Gestion des demandes de congés
- Calcul des retards académiques
<<<<<<< HEAD
- Statistiques et KPIs du Dashboard
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
"""

from .pfair_scheduler import PfairScheduler
from .calendar_service import CalendarService
from .leave_service import LeaveService
from .delay_calculator import DelayCalculator
<<<<<<< HEAD
from .dashboard_service import DashboardService
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f

__all__ = [
    'PfairScheduler',
    'CalendarService',
    'LeaveService',
    'DelayCalculator',
<<<<<<< HEAD
    'DashboardService',
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
]
