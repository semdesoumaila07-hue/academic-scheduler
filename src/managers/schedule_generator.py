"""
Manager pour la génération et gestion des emplois du temps.

Coordonne l'algorithme Pfair et la gestion des créneaux horaires.
"""
from typing import List, Dict, Optional
from datetime import date, time, timedelta
from sqlalchemy.orm import Session

from ..database.repositories import (
    ScheduleRepository, ActivityRepository, TeacherRepository,
    CohortRepository
)
from ..database.models import ScheduleSlotModel
from ..services import PfairScheduler, CalendarService, LeaveService
from ..entité import ScheduleSlot
from ..services.auth_service import require_permission
from typing import Any


class ScheduleGenerator:
    """
    Manager pour la génération d'emplois du temps.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le générateur d'emplois du temps.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.schedule_repo = ScheduleRepository(session)
        self.activity_repo = ActivityRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.pfair_scheduler = PfairScheduler(session)
        self.calendar_service = CalendarService(session)
        self.leave_service = LeaveService(session)
    
    @require_permission('launch_scheduling')
    def generate_schedule(self, cohort_id: int, start_date: date, end_date: date,
                         available_rooms: List[str] = None, 
                         replace_existing: bool = False,
                         current_user: Any = None) -> Dict:
        """
        Génère l'emploi du temps d'une cohorte avec l'algorithme Pfair.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début
            end_date: Date de fin
            available_rooms: Liste des salles disponibles
            replace_existing: Si True, supprime l'emploi du temps existant
            
        Returns:
            Dictionnaire avec le résultat de la génération
        """
        # Vérifier que la cohorte existe
        cohort = self.cohort_repo.get_by_id(cohort_id)
        if not cohort:
            return {'success': False, 'error': 'Cohorte introuvable'}

        # Vérifier le périmètre UFR/program si current_user fourni
        if current_user is not None:
            user_roles = [getattr(r, 'name', '') for r in getattr(current_user, 'roles', [])]
            is_admin = any(r.lower() == 'admin' for r in user_roles)
            if not is_admin:
                program = getattr(cohort, 'program', None)
                target_ufr = getattr(program, 'ufr_id', None) if program else None
                if getattr(current_user, 'ufr_id', None) != target_ufr and getattr(current_user, 'program_id', None) != getattr(program, 'id', None):
                    return {'success': False, 'error': 'Permission refusée : hors périmètre UFR/Programme'}
        
        # Vérifier la validité des dates
        validation = self.calendar_service.validate_date_range(start_date, end_date)
        if not validation['valid']:
            return {'success': False, 'error': validation['reason']}
        
        # Test de faisabilité
        feasibility = self.pfair_scheduler.is_schedulable(cohort_id, start_date, end_date)
        if not feasibility['schedulable']:
            return {
                'success': False,
                'error': feasibility['reason'],
                'total_charge': feasibility['total_charge'],
                'effective_days': feasibility.get('effective_days', 0)
            }
        
        # Supprimer l'emploi du temps existant si demandé
        if replace_existing:
            deleted_count = self.schedule_repo.delete_by_cohort(cohort_id, start_date, end_date)
        
        # Générer l'emploi du temps avec Pfair
        result = self.pfair_scheduler.schedule_cohort(
            cohort_id, start_date, end_date, available_rooms
        )
        
        return result
    
    def get_cohort_schedule(self, cohort_id: int, start_date: date = None,
                           end_date: date = None) -> List[ScheduleSlotModel]:
        """
        Récupère l'emploi du temps d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Liste des créneaux horaires
        """
        return self.schedule_repo.get_by_cohort(cohort_id, start_date, end_date)
    
    def get_teacher_schedule(self, teacher_id: int, start_date: date = None,
                            end_date: date = None) -> List[ScheduleSlotModel]:
        """
        Récupère l'emploi du temps d'un enseignant.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Liste des créneaux horaires
        """
        return self.schedule_repo.get_by_teacher(teacher_id, start_date, end_date)
    
    def get_daily_schedule(self, target_date: date, cohort_id: int = None) -> List[ScheduleSlotModel]:
        """
        Récupère l'emploi du temps d'une journée.
        
        Args:
            target_date: Date
            cohort_id: ID de la cohorte (optionnel, sinon tous)
            
        Returns:
            Liste des créneaux du jour
        """
        if cohort_id:
            return self.schedule_repo.get_by_cohort(cohort_id, target_date, target_date)
        else:
            return self.schedule_repo.get_by_date(target_date)
    
    @require_permission('adjust_schedule')
    def create_manual_slot(self, cohort_id: int, activity_id: int, teacher_id: int,
                          target_date: date, start_time: time, end_time: time,
                          room: str = None, current_user: Any = None) -> Dict:
        """
        Crée manuellement un créneau horaire.
        
        Args:
            cohort_id: ID de la cohorte
            activity_id: ID de l'activité
            teacher_id: ID de l'enseignant
            target_date: Date
            start_time: Heure de début
            end_time: Heure de fin
            room: Salle (optionnel)
            
        Returns:
            Dictionnaire avec le résultat
        """
        # Vérifier que tout existe
        cohort = self.cohort_repo.get_by_id(cohort_id)
        if not cohort:
            return {'success': False, 'error': 'Cohorte introuvable'}

        # Vérifier périmètre pour user si fourni
        if current_user is not None:
            user_roles = [getattr(r, 'name', '') for r in getattr(current_user, 'roles', [])]
            is_admin = any(r.lower() == 'admin' for r in user_roles)
            if not is_admin:
                program = getattr(cohort, 'program', None)
                target_ufr = getattr(program, 'ufr_id', None) if program else None
                if getattr(current_user, 'ufr_id', None) != target_ufr and getattr(current_user, 'program_id', None) != getattr(program, 'id', None):
                    return {'success': False, 'error': 'Permission refusée : hors périmètre UFR/Programme'}
        
        activity = self.activity_repo.get_by_id(activity_id)
        if not activity:
            return {'success': False, 'error': 'Activité introuvable'}
        
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return {'success': False, 'error': 'Enseignant introuvable'}
        
        # Vérifier que c'est un jour ouvrable
        if not self.calendar_service.is_workday(target_date):
            return {'success': False, 'error': 'Ce jour n\'est pas un jour ouvrable'}
        
        # Vérifier la disponibilité de l'enseignant
        availability = self.leave_service.check_teacher_availability(teacher_id, target_date)
        if not availability['available']:
            return {
                'success': False,
                'error': f'Enseignant non disponible: {availability["reason"]}'
            }
        
        # Vérifier les conflits
        if self.schedule_repo.check_conflict(
            target_date, start_time, end_time,
            teacher_id=teacher_id, cohort_id=cohort_id, room=room
        ):
            return {
                'success': False,
                'error': 'Conflit détecté (enseignant, cohorte ou salle déjà occupé)'
            }
        
        # Créer le créneau
        slot = ScheduleSlot(
            date=target_date, start_time=start_time, end_time=end_time,
            room=room, activity_id=activity_id, teacher_id=teacher_id,
            cohort_id=cohort_id
        )
        
        is_valid, error = slot.validate()
        if not is_valid:
            return {'success': False, 'error': error}
        
        slot_model = self.schedule_repo.create(
            date=target_date, start_time=start_time, end_time=end_time,
            room=room, activity_id=activity_id, teacher_id=teacher_id,
            cohort_id=cohort_id
        )
        
        # Mettre à jour les heures de l'activité
        duration_hours = slot.get_duration_hours()
        self.activity_repo.update_hours_done(activity_id, duration_hours)
        
        return {
            'success': True,
            'slot_id': slot_model.id,
            'message': 'Créneau créé avec succès'
        }
    
    def delete_slot(self, slot_id: int) -> Dict:
        """
        Supprime un créneau horaire.
        
        Args:
            slot_id: ID du créneau
            
        Returns:
            Dictionnaire avec le résultat
        """
        slot = self.schedule_repo.get_by_id(slot_id)
        
        if not slot:
            return {'success': False, 'error': 'Créneau introuvable'}
        
        # Soustraire les heures de l'activité
        duration_hours = (
            datetime.combine(date.today(), slot.end_time) -
            datetime.combine(date.today(), slot.start_time)
        ).total_seconds() / 3600
        
        activity = self.activity_repo.get_by_id(slot.activity_id)
        if activity and activity.hours_done >= duration_hours:
            activity.hours_done -= duration_hours
            self.session.commit()
        
        # Supprimer le créneau
        deleted = self.schedule_repo.delete(slot_id)
        
        if deleted:
            return {'success': True, 'message': 'Créneau supprimé'}
        else:
            return {'success': False, 'error': 'Erreur lors de la suppression'}
    
    def check_conflicts(self, target_date: date, start_time: time, end_time: time,
                       teacher_id: int = None, cohort_id: int = None,
                       room: str = None) -> Dict:
        """
        Vérifie les conflits pour un créneau potentiel.
        
        Args:
            target_date: Date
            start_time: Heure de début
            end_time: Heure de fin
            teacher_id: ID de l'enseignant (optionnel)
            cohort_id: ID de la cohorte (optionnel)
            room: Salle (optionnel)
            
        Returns:
            Dictionnaire avec les informations sur les conflits
        """
        has_conflict = self.schedule_repo.check_conflict(
            target_date, start_time, end_time,
            teacher_id=teacher_id, cohort_id=cohort_id, room=room
        )
        
        conflicts_details = []
        
        if teacher_id:
            teacher_slots = self.schedule_repo.get_by_teacher(teacher_id, target_date, target_date)
            for slot in teacher_slots:
                if (slot.start_time < end_time and slot.end_time > start_time):
                    conflicts_details.append({
                        'type': 'enseignant',
                        'slot_id': slot.id,
                        'time': f"{slot.start_time} - {slot.end_time}"
                    })
        
        if cohort_id:
            cohort_slots = self.schedule_repo.get_by_cohort(cohort_id, target_date, target_date)
            for slot in cohort_slots:
                if (slot.start_time < end_time and slot.end_time > start_time):
                    conflicts_details.append({
                        'type': 'cohorte',
                        'slot_id': slot.id,
                        'time': f"{slot.start_time} - {slot.end_time}"
                    })
        
        return {
            'has_conflict': has_conflict,
            'conflicts': conflicts_details,
            'conflict_count': len(conflicts_details)
        }
    
    def get_available_rooms(self, target_date: date, start_time: time,
                           end_time: time, all_rooms: List[str]) -> List[str]:
        """
        Retourne les salles disponibles pour un créneau.
        
        Args:
            target_date: Date
            start_time: Heure de début
            end_time: Heure de fin
            all_rooms: Liste de toutes les salles
            
        Returns:
            Liste des salles disponibles
        """
        return self.schedule_repo.get_available_rooms(
            target_date, start_time, end_time, all_rooms
        )
    
    def get_schedule_statistics(self, cohort_id: int = None,
                               start_date: date = None,
                               end_date: date = None) -> Dict:
        """
        Calcule les statistiques d'un emploi du temps.
        
        Args:
            cohort_id: ID de la cohorte (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if cohort_id:
            slots = self.schedule_repo.get_by_cohort(cohort_id, start_date, end_date)
        else:
            slots = self.schedule_repo.get_by_date_range(start_date, end_date) if start_date and end_date else []
        
        if not slots:
            return {
                'total_slots': 0,
                'total_hours': 0,
                'blocked_slots': 0
            }
        
        total_hours = 0.0
        blocked_count = 0
        rooms_used = set()
        teachers_involved = set()
        
        for slot in slots:
            # Calculer la durée
            duration = (
                datetime.combine(date.today(), slot.end_time) -
                datetime.combine(date.today(), slot.start_time)
            ).total_seconds() / 3600
            total_hours += duration
            
            if slot.blocked_by_leave:
                blocked_count += 1
            
            if slot.room:
                rooms_used.add(slot.room)
            
            teachers_involved.add(slot.teacher_id)
        
        return {
            'total_slots': len(slots),
            'total_hours': total_hours,
            'blocked_slots': blocked_count,
            'active_slots': len(slots) - blocked_count,
            'rooms_used': len(rooms_used),
            'teachers_involved': len(teachers_involved),
            'average_hours_per_slot': total_hours / len(slots) if slots else 0
        }
    
    def export_schedule(self, cohort_id: int, start_date: date, end_date: date) -> Dict:
        """
        Prépare l'emploi du temps pour l'exportation.
        
        Args:
            cohort_id: ID de la cohorte
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire formaté pour l'export
        """
        slots = self.schedule_repo.get_by_cohort(cohort_id, start_date, end_date)
        cohort = self.cohort_repo.get_by_id(cohort_id)
        
        export_data = {
            'cohort': {
                'id': cohort.id,
                'name': cohort.name,
                'academic_year': cohort.academic_year
            } if cohort else None,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'schedule': []
        }
        
        for slot in slots:
            activity = self.activity_repo.get_by_id(slot.activity_id)
            teacher = self.teacher_repo.get_by_id(slot.teacher_id)
            
            export_data['schedule'].append({
                'date': slot.date.isoformat(),
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'activity': activity.name if activity else 'Inconnu',
                'activity_type': activity.type.value if activity else '',
                'teacher': teacher.full_name if teacher else 'Non assigné',
                'room': slot.room or 'Non spécifiée',
                'blocked': slot.blocked_by_leave
            })
        
        return export_data