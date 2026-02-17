"""
Implémentation de l'algorithme Pfair pour l'ordonnancement académique.

L'algorithme Pfair (Proportionate Fair) garantit un ordonnancement équitable
en maintenant la proportionnalité entre le temps écoulé et le travail effectué.

Concepts clés :
- Ci : Volume horaire total d'une activité
- H(t) : Heures réalisées jusqu'au temps t
- U(τi) : Facteur de charge = Ci / D_effectif
- lag(τi, t) : Retard = U(τi) × t - H(t)
- α(τi, t) : Ratio = lag(τi, t) / U(τi)
"""
from typing import List, Optional, Dict, Tuple
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session

from ..database.models import (
    AcademicActivityModel, ScheduleSlotModel, TeacherModel,
    CohortModel, ActivityStatusEnum
)
from ..database.repositories import (
    ActivityRepository, ScheduleRepository, TeacherRepository,
    CohortRepository, CalendarRepository
)
from .calendar_service import CalendarService


class PfairScheduler:
    """
    Ordonnanceur Pfair pour les activités académiques.
    
    Attributes:
        session: Session de base de données
        calendar_service: Service de gestion du calendrier
    """
    
    def __init__(self, session: Session):
        """
        Initialise l'ordonnanceur Pfair.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.calendar_repo = CalendarRepository(session)
        self.calendar_service = CalendarService(session)
    
    def schedule_cohort(self, cohort_id: int, start_date: date, end_date: date,
                       available_rooms: List[str] = None) -> Dict:
        """
        Génère l'emploi du temps d'une cohorte avec l'algorithme Pfair.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début de la période
            end_date: Date de fin de la période
            available_rooms: Liste des salles disponibles
            
        Returns:
            Dictionnaire avec les statistiques de l'ordonnancement
        """
        # Récupérer la cohorte
        cohort = self.cohort_repo.get_by_id(cohort_id)
        if not cohort:
            raise ValueError(f"Cohorte {cohort_id} introuvable")
        
        # Récupérer toutes les activités de la cohorte
        activities = self.activity_repo.get_by_cohort(cohort_id)
        
        if not activities:
            return {
                'success': False,
                'message': 'Aucune activité à planifier',
                'scheduled_slots': 0
            }
        
        # Calculer D_effectif (nombre de jours ouvrables)
        d_effective = self.calendar_service.calculate_effective_days(
            start_date, end_date
        )
        
        if d_effective <= 0:
            return {
                'success': False,
                'message': 'Aucun jour ouvrable dans la période',
                'scheduled_slots': 0
            }
        
        # Calculer les facteurs de charge U(τi) pour toutes les activités
        total_charge = 0.0
        for activity in activities:
            remaining_hours = activity.volume_hours - activity.hours_done
            activity.charge_factor = remaining_hours / d_effective
            total_charge += activity.charge_factor
        
        # Vérifier la faisabilité (U ≤ 1.0)
        U = total_charge  # Facteur de charge global
        
        if U > 1.0:
            return {
                'success': False,
                'message': f'Charge totale trop élevée: {U:.2f} > 1.0',
                'total_charge': U,
                'effective_days': d_effective,
                'schedulable': False
            }
        
        # Initialiser le temps t = 0
        t = 0
        current_date = start_date
        scheduled_slots = []
        conflicts = []
        
        # Boucle principale de l'algorithme Pfair
        while current_date <= end_date:
            # Vérifier si c'est un jour ouvrable
            if not self.calendar_service.is_workday(current_date):
                current_date += timedelta(days=1)
                continue
            
            # Incrémenter le temps
            t += 1
            
            # 1. Identifier les activités urgentes (α ≥ 1)
            urgent_activities = []
            possible_activities = []
            
            for activity in activities:
                if activity.status in [ActivityStatusEnum.COMPLETED, ActivityStatusEnum.CANCELLED]:
                    continue
                
                remaining = activity.volume_hours - activity.hours_done
                if remaining <= 0:
                    activity.status = ActivityStatusEnum.COMPLETED
                    continue
                
                # Calculer α(τi, t)
                expected_hours = activity.charge_factor * t
                delay = expected_hours - activity.hours_done
                
                if activity.charge_factor > 0:
                    alpha = delay / activity.charge_factor
                    
                    if alpha >= 1.0:
                        urgent_activities.append((activity, alpha, delay))
                    elif alpha >= 0:
                        possible_activities.append((activity, alpha, delay))
            
            # 2. Trier les activités urgentes par α décroissant
            urgent_activities.sort(key=lambda x: x[1], reverse=True)
            
            # 3. Ordonnancer les activités urgentes
            daily_slots = []
            start_hour = 8  # 8h00
            slot_duration = 2  # 2 heures par créneau
            
            for activity, alpha, delay in urgent_activities:
                # Vérifier disponibilité de l'enseignant
                teacher = self.teacher_repo.get_by_id(activity.teacher_id)
                if not teacher:
                    continue
                
                # Créer un créneau
                slot_start = time(hour=start_hour)
                slot_end = time(hour=start_hour + slot_duration)
                
                # Vérifier les conflits
                if self.schedule_repo.check_conflict(
                    current_date, slot_start, slot_end,
                    teacher_id=teacher.id,
                    cohort_id=cohort_id
                ):
                    conflicts.append({
                        'date': current_date,
                        'activity': activity.name,
                        'reason': 'Conflit horaire'
                    })
                    continue
                
                # Assigner une salle disponible
                room = None
                if available_rooms:
                    available = self.schedule_repo.get_available_rooms(
                        current_date, slot_start, slot_end, available_rooms
                    )
                    if available:
                        room = available[0]
                
                # Créer le créneau
                slot = ScheduleSlotModel(
                    date=current_date,
                    start_time=slot_start,
                    end_time=slot_end,
                    room=room,
                    activity_id=activity.id,
                    teacher_id=teacher.id,
                    cohort_id=cohort_id,
                    delay_value=delay
                )
                
                daily_slots.append(slot)
                scheduled_slots.append(slot)
                
                # Mettre à jour les heures réalisées
                activity.hours_done += slot_duration
                activity.status = ActivityStatusEnum.IN_PROGRESS
                
                # Passer au créneau suivant
                start_hour += slot_duration
                
                # Maximum 4 créneaux par jour (8h de cours)
                if start_hour >= 16:  # 16h00
                    break
            
            # Sauvegarder les créneaux du jour
            for slot in daily_slots:
                self.session.add(slot)
            
            # Passer au jour suivant
            current_date += timedelta(days=1)
        
        # Sauvegarder toutes les modifications
        self.session.commit()
        
        # Calculer les statistiques
        total_scheduled_hours = len(scheduled_slots) * 2  # 2h par créneau
        
        return {
            'success': True,
            'scheduled_slots': len(scheduled_slots),
            'total_hours': total_scheduled_hours,
            'conflicts': len(conflicts),
            'total_charge': U,
            'effective_days': d_effective,
            'schedulable': True,
            'period': f"{start_date} à {end_date}",
            'conflicts_details': conflicts
        }
    
    def calculate_activity_priority(self, activity: AcademicActivityModel, t: int) -> Tuple[float, float]:
        """
        Calcule la priorité d'ordonnancement d'une activité.
        
        Args:
            activity: Activité académique
            t: Temps actuel (nombre de jours depuis le début)
            
        Returns:
            Tuple (alpha, delay)
        """
        if activity.charge_factor == 0:
            return (0.0, 0.0)
        
        expected_hours = activity.charge_factor * t
        delay = expected_hours - activity.hours_done
        alpha = delay / activity.charge_factor
        
        return (alpha, delay)
    
    def is_schedulable(self, cohort_id: int, start_date: date, end_date: date) -> Dict:
        """
        Vérifie si une cohorte peut être ordonnancée (test de faisabilité).
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec le résultat du test
        """
        activities = self.activity_repo.get_by_cohort(cohort_id)
        
        if not activities:
            return {
                'schedulable': False,
                'reason': 'Aucune activité',
                'total_charge': 0.0
            }
        
        d_effective = self.calendar_service.calculate_effective_days(start_date, end_date)
        
        if d_effective <= 0:
            return {
                'schedulable': False,
                'reason': 'Aucun jour ouvrable',
                'total_charge': 0.0,
                'effective_days': 0
            }
        
        # Calculer la charge totale
        total_charge = 0.0
        for activity in activities:
            remaining = activity.volume_hours - activity.hours_done
            if remaining > 0:
                total_charge += remaining / d_effective
        
        schedulable = total_charge <= 1.0
        
        return {
            'schedulable': schedulable,
            'total_charge': total_charge,
            'effective_days': d_effective,
            'reason': 'OK' if schedulable else f'Charge trop élevée: {total_charge:.2f} > 1.0',
            'max_charge': 1.0
        }
    
    def rebalance_schedule(self, cohort_id: int, start_date: date, end_date: date) -> Dict:
        """
        Réajuste l'emploi du temps pour minimiser les retards.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec les statistiques du réajustement
        """
        # Supprimer l'emploi du temps existant
        deleted_count = self.schedule_repo.delete_by_cohort(cohort_id, start_date, end_date)
        
        # Régénérer l'emploi du temps
        result = self.schedule_cohort(cohort_id, start_date, end_date)
        result['deleted_slots'] = deleted_count
        result['rebalanced'] = True
        
        return result
