"""
Service pour le Dashboard - agrège les données des repositories.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from ..database.repositories.statistics_repository import StatisticsRepository


class DashboardService:
    """
    Service pour le Dashboard.
    Agrège toutes les données nécessaires pour l'affichage du tableau de bord.
    """
    
    def __init__(self, session: Session):
        """
        Initialise le service Dashboard.
        
        Args:
            session: Session SQLAlchemy
        """
        self.session = session
        self.stats_repo = StatisticsRepository(session)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Obtient toutes les données du Dashboard.
        
        Returns:
            Dict contenant:
                - kpis: Cartes de statistiques
                - activities_status: Distribution des activités
                - completion_percentage: Pourcentage de progression
                - recent_activities: Activités récentes
                - busy_teachers: Enseignants chargés
                - delayed_activities: Activités en retard
        """
        stats = self.stats_repo.get_dashboard_statistics()
        
        return {
            'kpis': [
                {'label': 'Universités', 'value': stats['num_universities'], 'icon': '🎓'},
                {'label': 'UFR', 'value': stats['num_ufrs'], 'icon': '🏛️'},
                {'label': 'Enseignants', 'value': stats['num_teachers'], 'icon': '👨‍🏫'},
                {'label': 'Activités', 'value': stats['num_activities'], 'icon': '📚'},
                {'label': 'Classes', 'value': stats['num_cohorts'], 'icon': '👥'},
                {'label': 'Étudiants', 'value': stats['num_students'], 'icon': '🎓'},
                {'label': 'Heures planifiées', 'value': f"{int(stats['total_hours_done'])}h", 'icon': '⏱️'},
                {'label': 'Volume total', 'value': f"{int(stats['total_volume_hours'])}h", 'icon': '📊'},
            ],
            'activities_status': self.stats_repo.get_activities_by_status(),
            'activities_by_type': self.stats_repo.get_activities_by_type(),
            'completion_percentage': self.stats_repo.get_completion_percentage(),
            'recent_activities': self._format_recent_activities(),
            'busy_teachers': self._format_busy_teachers(),
            'delayed_activities': self._format_delayed_activities(),
        }
    
    def get_kpis(self) -> List[Dict[str, Any]]:
        """
        Obtient les KPIs (cartes statistiques).
        
        Returns:
            Liste de dicts {label, value, icon}
        """
        return self.get_dashboard_data()['kpis']
    
    def get_completion_info(self) -> Dict[str, Any]:
        """
        Obtient les infos de progression globale.
        
        Returns:
            Dict {percentage, hours_done, total_volume}
        """
        stats = self.stats_repo.get_dashboard_statistics()
        return {
            'percentage': self.stats_repo.get_completion_percentage(),
            'hours_done': stats['total_hours_done'],
            'total_volume': stats['total_volume_hours'],
        }
    
    def _format_recent_activities(self) -> List[Dict[str, Any]]:
        """Formate les activités récentes pour l'affichage."""
        activities = self.stats_repo.get_recent_activities(limit=4)
        result = []
        for a in activities:
            completion = 0
            if a.volume_hours > 0:
                completion = round((a.hours_done / a.volume_hours) * 100, 1)
            result.append({
                'id': a.id,
                'name': a.name,
                'type': a.type.value if hasattr(a.type, 'value') else str(a.type),
                'volume_hours': a.volume_hours,
                'hours_done': a.hours_done,
                'status': a.status.value if hasattr(a.status, 'value') else str(a.status),
                'completion_percentage': completion,
            })
        return result
    
    def _format_busy_teachers(self) -> List[Dict[str, Any]]:
        """Formate les enseignants chargés pour l'affichage."""
        teachers = self.stats_repo.get_busy_teachers(limit=5)
        result = []
        for t in teachers:
            total_hours = sum(a.volume_hours for a in t.activities) if hasattr(t, 'activities') else 0
            result.append({
                'id': t.id,
                'full_name': t.full_name,
                'email': t.email,
                'speciality': t.speciality,
                'num_activities': len(t.activities) if hasattr(t, 'activities') else 0,
                'total_hours': total_hours,
            })
        return result
    
    def _format_delayed_activities(self) -> List[Dict[str, Any]]:
        """Formate les activités en retard pour l'affichage."""
        activities = self.stats_repo.get_delayed_activities(limit=5)
        result = []
        for a in activities:
            delay = a.volume_hours - a.hours_done
            result.append({
                'id': a.id,
                'name': a.name,
                'type': a.type.value if hasattr(a.type, 'value') else str(a.type),
                'volume_hours': a.volume_hours,
                'hours_done': a.hours_done,
                'delay_hours': round(delay, 1),
                'status': a.status.value if hasattr(a.status, 'value') else str(a.status),
            })
        return result
