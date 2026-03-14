"""
Repository pour les statistiques et KPIs du Dashboard.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    UniversityModel, UFRModel, ProgramModel, CohortModel,
    TeacherModel, StudentModel, AcademicActivityModel,
    ActivityStatusEnum, ActivityTypeEnum
)


class StatisticsRepository:
    """
    Repository pour calculer les statistiques du Dashboard.
    Fournit les KPIs et agrégations nécessaires pour l'affichage.
    """
    
    def __init__(self, session: Session):
        """
        Initialise le repository de statistiques.
        
        Args:
            session: Session SQLAlchemy
        """
        self.session = session
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        Obtient toutes les statistiques pour le Dashboard.
        
        Returns:
            Dict contenant:
                - num_universities: Nombre d'universités
                - num_ufrs: Nombre d'UFRs
                - num_teachers: Nombre d'enseignants
                - num_activities: Nombre d'activités
                - num_cohorts: Nombre de cohortes/classes
                - num_students: Nombre d'étudiants
                - total_volume_hours: Volume total d'heures planifiées
                - total_hours_done: Heures réalisées
                - activities_completed: Nombre d'activités complétées
        """
        return {
            'num_universities': self.get_universities_count(),
            'num_ufrs': self.get_ufrs_count(),
            'num_teachers': self.get_teachers_count(),
            'num_activities': self.get_activities_count(),
            'num_cohorts': self.get_cohorts_count(),
            'num_students': self.get_students_count(),
            'total_volume_hours': self.get_total_volume_hours(),
            'total_hours_done': self.get_total_hours_done(),
            'activities_completed': self.get_completed_activities_count(),
        }
    
    def get_universities_count(self) -> int:
        """Nombre d'universités."""
        return self.session.query(func.count(UniversityModel.id)).scalar() or 0
    
    def get_ufrs_count(self) -> int:
        """Nombre d'UFRs."""
        return self.session.query(func.count(UFRModel.id)).scalar() or 0
    
    def get_teachers_count(self) -> int:
        """Nombre d'enseignants."""
        return self.session.query(func.count(TeacherModel.id)).scalar() or 0
    
    def get_activities_count(self) -> int:
        """Nombre d'activités."""
        return self.session.query(func.count(AcademicActivityModel.id)).scalar() or 0
    
    def get_cohorts_count(self) -> int:
        """Nombre de cohortes/classes."""
        return self.session.query(func.count(CohortModel.id)).scalar() or 0
    
    def get_students_count(self) -> int:
        """Nombre total d'étudiants."""
        return self.session.query(func.count(StudentModel.id)).scalar() or 0
    
    def get_total_volume_hours(self) -> float:
        """Volume total d'heures planifiées."""
        result = self.session.query(
            func.sum(AcademicActivityModel.volume_hours)
        ).scalar()
        return float(result) if result else 0.0
    
    def get_total_hours_done(self) -> float:
        """Heures réalisées au total."""
        result = self.session.query(
            func.sum(AcademicActivityModel.hours_done)
        ).scalar()
        return float(result) if result else 0.0
    
    def get_completed_activities_count(self) -> int:
        """Nombre d'activités complétées."""
        return self.session.query(func.count(AcademicActivityModel.id)).filter(
            AcademicActivityModel.status == ActivityStatusEnum.COMPLETED
        ).scalar() or 0
    
    def get_activities_by_status(self) -> Dict[str, int]:
        """
        Nombre d'activités par statut.
        
        Returns:
            Dict {statut: nombre}
        """
        result = {}
        for status in ActivityStatusEnum:
            count = self.session.query(func.count(AcademicActivityModel.id)).filter(
                AcademicActivityModel.status == status
            ).scalar() or 0
            result[status.value] = count
        return result

    def get_activities_by_type(self) -> Dict[str, int]:
        """
        Nombre d'activités par type (CM, TD, TP, etc.).
        
        Returns:
            Dict {type: nombre}
        """
        result = {}
        for act_type in ActivityTypeEnum:
            count = self.session.query(func.count(AcademicActivityModel.id)).filter(
                AcademicActivityModel.type == act_type
            ).scalar() or 0
            result[act_type.value] = count
        return result
    
    def get_completion_percentage(self) -> float:
        """
        Pourcentage de progression globale.
        
        Returns:
            Pourcentage (0-100) d'heures réalisées / Volume total
        """
        total = self.get_total_volume_hours()
        if total == 0:
            return 0.0
        done = self.get_total_hours_done()
        return round((done / total) * 100, 2)
    
    def get_recent_activities(self, limit: int = 5) -> list:
        """
        Dernières activités ajoutées.
        
        Args:
            limit: Nombre d'activités à retourner
            
        Returns:
            Liste des activités récentes
        """
        return self.session.query(AcademicActivityModel).order_by(
            AcademicActivityModel.created_at.desc()
        ).limit(limit).all()
    
    def get_busy_teachers(self, limit: int = 5) -> list:
        """
        Enseignants les plus chargés.
        
        Args:
            limit: Nombre d'enseignants à retourner
            
        Returns:
            Liste des enseignants avec plus d'activités
        """
        return self.session.query(TeacherModel).outerjoin(
            AcademicActivityModel
        ).group_by(TeacherModel.id).order_by(
            func.count(AcademicActivityModel.id).desc()
        ).limit(limit).all()
    
    def get_delayed_activities(self, limit: int = 5) -> list:
        """
        Activités avec du retard (heures_realisees < volume_hours).
        
        Args:
            limit: Nombre d'activités à retourner
            
        Returns:
            Liste des activités en retard
        """
        return self.session.query(AcademicActivityModel).filter(
            AcademicActivityModel.hours_done < AcademicActivityModel.volume_hours
        ).order_by(
            (AcademicActivityModel.volume_hours - AcademicActivityModel.hours_done).desc()
        ).limit(limit).all()
    
    def get_universities_with_details(self) -> list:
        """
        Universités avec détails (structure imbriquée).
        
        Returns:
            Liste des universités avec leurs UFRs et programmes
        """
        return self.session.query(UniversityModel).all()
