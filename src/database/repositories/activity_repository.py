"""
Repository pour les Activités Académiques.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base_repository import BaseRepository
from ..models import AcademicActivityModel, ActivityStatusEnum


class ActivityRepository(BaseRepository[AcademicActivityModel]):
    """Repository pour les opérations sur les activités académiques."""
    
    def __init__(self, session: Session):
        super().__init__(AcademicActivityModel, session)
    
    def get_by_code(self, code: str) -> Optional[AcademicActivityModel]:
        """Récupère une activité par son code."""
        return self.first_by(code=code)
    
    def get_by_cohort(self, cohort_id: int) -> List[AcademicActivityModel]:
        """Récupère toutes les activités d'une cohorte."""
        return self.filter_by(cohort_id=cohort_id)
    
    def get_by_teacher(self, teacher_id: int) -> List[AcademicActivityModel]:
        """Récupère toutes les activités d'un enseignant."""
        return self.filter_by(teacher_id=teacher_id)
    
    def get_by_status(self, status: ActivityStatusEnum) -> List[AcademicActivityModel]:
        """Récupère les activités par statut."""
        return self.filter_by(status=status)
    
    def get_pending_activities(self) -> List[AcademicActivityModel]:
        """Récupère toutes les activités en attente de planification."""
        return self.filter_by(status=ActivityStatusEnum.PENDING)
    
    def get_completed_activities(self) -> List[AcademicActivityModel]:
        """Récupère toutes les activités terminées."""
        return self.filter_by(status=ActivityStatusEnum.COMPLETED)
    
    def get_in_progress_activities(self) -> List[AcademicActivityModel]:
        """Récupère toutes les activités en cours."""
        return self.filter_by(status=ActivityStatusEnum.IN_PROGRESS)
    
    def get_urgent_activities(self, cohort_id: int = None) -> List[AcademicActivityModel]:
        """
        Récupère les activités urgentes (avec retard).
        Une activité est urgente si α(τi, t) >= 1
        
        Args:
            cohort_id: ID de la cohorte (optionnel)
            
        Returns:
            Liste des activités urgentes
        """
        query = self.session.query(self.model).filter(
            and_(
                self.model.status != ActivityStatusEnum.COMPLETED,
                self.model.status != ActivityStatusEnum.CANCELLED,
                self.model.hours_done < self.model.volume_hours
            )
        )
        
        if cohort_id:
            query = query.filter(self.model.cohort_id == cohort_id)
        
        activities = query.all()
        
        # Filtrer les activités avec α >= 1 (urgentes selon Pfair)
        urgent = []
        for activity in activities:
            if activity.charge_factor > 0:
                # Calculer le temps écoulé depuis l'activation
                if activity.activation_date:
                    days_elapsed = (date.today() - activity.activation_date).days
                    expected_hours = activity.charge_factor * days_elapsed
                    delay = expected_hours - activity.hours_done
                    alpha = delay / activity.charge_factor
                    
                    if alpha >= 1.0:
                        urgent.append(activity)
        
        return urgent
    
    def get_activities_with_delay(self, cohort_id: int = None) -> List[dict]:
        """
        Récupère les activités avec leur retard calculé.
        
        Args:
            cohort_id: ID de la cohorte (optionnel)
            
        Returns:
            Liste de dictionnaires {activity, delay, alpha}
        """
        query = self.session.query(self.model).filter(
            and_(
                self.model.status != ActivityStatusEnum.COMPLETED,
                self.model.status != ActivityStatusEnum.CANCELLED
            )
        )
        
        if cohort_id:
            query = query.filter(self.model.cohort_id == cohort_id)
        
        activities = query.all()
        
        results = []
        for activity in activities:
            if activity.activation_date and activity.charge_factor > 0:
                days_elapsed = (date.today() - activity.activation_date).days
                expected_hours = activity.charge_factor * days_elapsed
                delay = expected_hours - activity.hours_done
                alpha = delay / activity.charge_factor
                
                results.append({
                    'activity': activity,
                    'delay': delay,
                    'alpha': alpha,
                    'completion_percent': (activity.hours_done / activity.volume_hours * 100) if activity.volume_hours > 0 else 0
                })
        
        # Trier par retard décroissant (plus urgent en premier)
        results.sort(key=lambda x: x['delay'], reverse=True)
        
        return results
    
    def calculate_total_delay(self, cohort_id: int) -> float:
        """
        Calcule le retard total d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            
        Returns:
            Retard total en heures
        """
        activities = self.get_by_cohort(cohort_id)
        
        total_delay = 0.0
        for activity in activities:
            if activity.activation_date and activity.charge_factor > 0:
                days_elapsed = (date.today() - activity.activation_date).days
                expected_hours = activity.charge_factor * days_elapsed
                delay = expected_hours - activity.hours_done
                
                if delay > 0:
                    total_delay += delay
        
        return total_delay
    
    def get_activities_by_priority(self, cohort_id: int = None) -> List[AcademicActivityModel]:
        """
        Récupère les activités triées par priorité.
        
        Args:
            cohort_id: ID de la cohorte (optionnel)
            
        Returns:
            Liste des activités triées par priorité décroissante
        """
        query = self.session.query(self.model).filter(
            self.model.status != ActivityStatusEnum.COMPLETED
        )
        
        if cohort_id:
            query = query.filter(self.model.cohort_id == cohort_id)
        
        return query.order_by(self.model.priority.desc()).all()
    
    def get_activities_near_deadline(self, days: int = 7) -> List[AcademicActivityModel]:
        """
        Récupère les activités dont la deadline approche.
        
        Args:
            days: Nombre de jours avant la deadline
            
        Returns:
            Liste des activités
        """
        from datetime import timedelta
        
        deadline_limit = date.today() + timedelta(days=days)
        
        return self.session.query(self.model).filter(
            and_(
                self.model.deadline.isnot(None),
                self.model.deadline <= deadline_limit,
                self.model.status != ActivityStatusEnum.COMPLETED,
                self.model.status != ActivityStatusEnum.CANCELLED
            )
        ).order_by(self.model.deadline).all()
    
    def update_hours_done(self, activity_id: int, hours: float) -> Optional[AcademicActivityModel]:
        """
        Met à jour les heures réalisées d'une activité.
        
        Args:
            activity_id: ID de l'activité
            hours: Heures à ajouter
            
        Returns:
            Activité mise à jour ou None
        """
        activity = self.get_by_id(activity_id)
        if not activity:
            return None
        
        activity.hours_done += hours
        
        # Mettre à jour le statut
        if activity.hours_done >= activity.volume_hours:
            activity.status = ActivityStatusEnum.COMPLETED
        elif activity.hours_done > 0:
            activity.status = ActivityStatusEnum.IN_PROGRESS
        
        self.session.commit()
        self.session.refresh(activity)
        
        return activity