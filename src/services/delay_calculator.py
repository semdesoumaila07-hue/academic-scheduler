"""
Service de calcul des retards académiques.

Calcule les retards (lag) pour les activités et cohortes selon l'algorithme Pfair.
"""
from typing import List, Dict, Optional
from datetime import date
from sqlalchemy.orm import Session

from ..database.repositories import ActivityRepository, CohortRepository
from ..database.models import AcademicActivityModel, ActivityStatusEnum
from .calendar_service import CalendarService


class DelayCalculator:
    """
    Service pour le calcul des retards académiques.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le calculateur de retards.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.calendar_service = CalendarService(session)
    
    def calculate_activity_delay(self, activity: AcademicActivityModel, 
                                reference_date: date = None) -> Dict:
        """
        Calcule le retard d'une activité selon Pfair.
        
        lag(τi, t) = U(τi) × t - H(t)
        
        Args:
            activity: Activité académique
            reference_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Dictionnaire avec les métriques de retard
        """
        if reference_date is None:
            reference_date = date.today()
        
        # Si l'activité n'est pas activée, pas de retard
        if not activity.activation_date:
            return {
                'activity_id': activity.id,
                'activity_name': activity.name,
                'delay': 0.0,
                'alpha': 0.0,
                'status': 'Non activée'
            }
        
        # Si l'activité est terminée ou annulée
        if activity.status in [ActivityStatusEnum.COMPLETED, ActivityStatusEnum.CANCELLED]:
            return {
                'activity_id': activity.id,
                'activity_name': activity.name,
                'delay': 0.0,
                'alpha': 0.0,
                'status': activity.status.value,
                'completion': 100.0
            }
        
        # Calculer le temps écoulé (t) en jours ouvrables
        t = self.calendar_service.calculate_effective_days(
            activity.activation_date,
            reference_date
        )
        
        # Calculer le retard : lag = U(τi) × t - H(t)
        expected_hours = activity.charge_factor * t
        delay = expected_hours - activity.hours_done
        
        # Calculer α = lag / U(τi)
        alpha = delay / activity.charge_factor if activity.charge_factor > 0 else 0.0
        
        # Calculer le pourcentage de complétion
        completion = (activity.hours_done / activity.volume_hours * 100) if activity.volume_hours > 0 else 0.0
        
        # Déterminer l'urgence
        urgency = 'Critique' if alpha >= 1.0 else ('Urgent' if alpha >= 0.5 else 'Normal')
        
        return {
            'activity_id': activity.id,
            'activity_name': activity.name,
            'delay': delay,  # En heures
            'alpha': alpha,
            'expected_hours': expected_hours,
            'hours_done': activity.hours_done,
            'volume_hours': activity.volume_hours,
            'remaining_hours': activity.volume_hours - activity.hours_done,
            'completion': completion,
            'days_elapsed': t,
            'charge_factor': activity.charge_factor,
            'urgency': urgency,
            'status': activity.status.value
        }
    
    def calculate_cohort_delay(self, cohort_id: int, reference_date: date = None) -> Dict:
        """
        Calcule le retard global d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            reference_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Dictionnaire avec les métriques de retard de la cohorte
        """
        if reference_date is None:
            reference_date = date.today()
        
        # Récupérer toutes les activités de la cohorte
        activities = self.activity_repo.get_by_cohort(cohort_id)
        
        if not activities:
            return {
                'cohort_id': cohort_id,
                'total_delay': 0.0,
                'activities_count': 0,
                'error': 'Aucune activité trouvée'
            }
        
        # Calculer le retard de chaque activité
        activities_delays = []
        total_delay = 0.0
        total_expected = 0.0
        total_done = 0.0
        total_volume = 0.0
        
        urgent_count = 0
        critical_count = 0
        
        for activity in activities:
            delay_info = self.calculate_activity_delay(activity, reference_date)
            
            if activity.status not in [ActivityStatusEnum.COMPLETED, ActivityStatusEnum.CANCELLED]:
                activities_delays.append(delay_info)
                
                if delay_info['delay'] > 0:
                    total_delay += delay_info['delay']
                
                total_expected += delay_info['expected_hours']
                total_done += activity.hours_done
                total_volume += activity.volume_hours
                
                if delay_info['urgency'] == 'Critique':
                    critical_count += 1
                elif delay_info['urgency'] == 'Urgent':
                    urgent_count += 1
        
        # Trier par retard décroissant
        activities_delays.sort(key=lambda x: x['delay'], reverse=True)
        
        # Calculer le pourcentage de complétion global
        global_completion = (total_done / total_volume * 100) if total_volume > 0 else 0.0
        
        return {
            'cohort_id': cohort_id,
            'total_delay': total_delay,
            'total_expected_hours': total_expected,
            'total_hours_done': total_done,
            'total_volume_hours': total_volume,
            'global_completion': global_completion,
            'activities_count': len(activities_delays),
            'critical_activities': critical_count,
            'urgent_activities': urgent_count,
            'activities': activities_delays,
            'reference_date': reference_date.isoformat()
        }
    
    def get_urgent_activities(self, cohort_id: int = None, 
                             reference_date: date = None) -> List[Dict]:
        """
        Récupère toutes les activités urgentes (α ≥ 0.5).
        
        Args:
            cohort_id: ID de la cohorte (optionnel, sinon toutes)
            reference_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Liste des activités urgentes avec leurs métriques
        """
        if reference_date is None:
            reference_date = date.today()
        
        # Récupérer les activités
        if cohort_id:
            activities = self.activity_repo.get_by_cohort(cohort_id)
        else:
            activities = self.activity_repo.get_in_progress_activities()
        
        urgent_activities = []
        
        for activity in activities:
            delay_info = self.calculate_activity_delay(activity, reference_date)
            
            # Considérer comme urgent si α ≥ 0.5
            if delay_info['alpha'] >= 0.5:
                urgent_activities.append(delay_info)
        
        # Trier par α décroissant (les plus urgentes en premier)
        urgent_activities.sort(key=lambda x: x['alpha'], reverse=True)
        
        return urgent_activities
    
    def get_activities_ranking(self, cohort_id: int, 
                              reference_date: date = None) -> List[Dict]:
        """
        Classe toutes les activités par ordre de priorité (α décroissant).
        
        Args:
            cohort_id: ID de la cohorte
            reference_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Liste des activités classées par priorité
        """
        if reference_date is None:
            reference_date = date.today()
        
        activities = self.activity_repo.get_by_cohort(cohort_id)
        
        ranking = []
        
        for activity in activities:
            if activity.status not in [ActivityStatusEnum.COMPLETED, ActivityStatusEnum.CANCELLED]:
                delay_info = self.calculate_activity_delay(activity, reference_date)
                ranking.append(delay_info)
        
        # Trier par α décroissant
        ranking.sort(key=lambda x: x['alpha'], reverse=True)
        
        # Ajouter le rang
        for i, activity in enumerate(ranking, 1):
            activity['rank'] = i
        
        return ranking
    
    def predict_completion_date(self, activity_id: int, 
                               hours_per_week: float = 4.0) -> Dict:
        """
        Prédit la date de complétion d'une activité.
        
        Args:
            activity_id: ID de l'activité
            hours_per_week: Heures par semaine prévues
            
        Returns:
            Dictionnaire avec la prédiction
        """
        activity = self.activity_repo.get_by_id(activity_id)
        
        if not activity:
            return {'error': 'Activité introuvable'}
        
        remaining_hours = activity.volume_hours - activity.hours_done
        
        if remaining_hours <= 0:
            return {
                'activity_id': activity_id,
                'status': 'Terminée',
                'remaining_hours': 0
            }
        
        # Calculer le nombre de semaines nécessaires
        weeks_needed = remaining_hours / hours_per_week
        
        # Estimer la date de complétion
        from datetime import timedelta
        estimated_date = date.today() + timedelta(weeks=int(weeks_needed))
        
        return {
            'activity_id': activity_id,
            'activity_name': activity.name,
            'remaining_hours': remaining_hours,
            'hours_per_week': hours_per_week,
            'weeks_needed': weeks_needed,
            'estimated_completion_date': estimated_date.isoformat(),
            'deadline': activity.deadline.isoformat() if activity.deadline else None,
            'will_meet_deadline': estimated_date <= activity.deadline if activity.deadline else True
        }
    
    def get_delay_summary(self) -> Dict:
        """
        Génère un résumé global des retards.
        
        Returns:
            Dictionnaire avec les statistiques globales
        """
        all_activities = self.activity_repo.get_in_progress_activities()
        
        if not all_activities:
            return {
                'total_activities': 0,
                'message': 'Aucune activité en cours'
            }
        
        total_delay = 0.0
        critical_count = 0
        urgent_count = 0
        normal_count = 0
        
        for activity in all_activities:
            delay_info = self.calculate_activity_delay(activity)
            
            if delay_info['delay'] > 0:
                total_delay += delay_info['delay']
            
            if delay_info['urgency'] == 'Critique':
                critical_count += 1
            elif delay_info['urgency'] == 'Urgent':
                urgent_count += 1
            else:
                normal_count += 1
        
        return {
            'total_activities': len(all_activities),
            'total_delay_hours': total_delay,
            'critical_activities': critical_count,
            'urgent_activities': urgent_count,
            'normal_activities': normal_count,
            'average_delay': total_delay / len(all_activities) if all_activities else 0.0
        }