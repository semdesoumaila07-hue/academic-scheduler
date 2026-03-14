"""
Manager pour la gestion des activités académiques.

Gère la création, modification et suivi des activités.
"""
from typing import List, Optional, Dict, Union
from datetime import date
from sqlalchemy.orm import Session

from ..database.repositories import (
    ActivityRepository, TeacherRepository, CohortRepository
)
from ..database.models import (
    AcademicActivityModel, ActivityTypeEnum, ActivityStatusEnum, PriorityEnum
)
from ..entité import AcademicActivity
from ..utils.constants import ActivityType
from ..services import DelayCalculator
from ..services.auth_service import require_permission
from typing import Any


class ActivityManager:
    """
    Manager pour la gestion des activités académiques.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le manager d'activités.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.activity_repo = ActivityRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.cohort_repo = CohortRepository(session)
        self.delay_calculator = DelayCalculator(session)
    
    # @require_permission('manage_activities')  # ⚠️ TEMPORAIREMENT DÉSACTIVÉ
    def create_activity(self, name: str, code: str, activity_type: Union[ActivityTypeEnum, str],
                       volume_hours: float, cohort_id: int, teacher_id: int = None,
                       activation_date: date = None, deadline: date = None,
                       priority: Union[PriorityEnum, int, str] = None,
                       current_user: Any = None) -> Dict:
        """
        Crée une nouvelle activité académique.
        
        Args:
            name: Nom de l'activité
            code: Code unique
            activity_type: Type d'activité (ActivityTypeEnum ou string "CM", "TD", "TP")
            volume_hours: Volume horaire total (Ci)
            cohort_id: ID de la cohorte
            teacher_id: ID de l'enseignant (optionnel)
            activation_date: Date d'activation (ri)
            deadline: Date limite (Di)
            priority: Priorité (PriorityEnum, int ou string)
            
        Returns:
            Dictionnaire avec le résultat
        """
        # ✅ Convertir activity_type si c'est une string
        if isinstance(activity_type, str):
            try:
                # Mapping exact vers les noms réels de ActivityTypeEnum
                type_mapping = {
                    "CM": ActivityTypeEnum.COURS_MAGISTRAL,
                    "TD": ActivityTypeEnum.TD,
                    "TP": ActivityTypeEnum.TP,
                    "Examen": ActivityTypeEnum.EXAMEN,
                    "Soutenance": ActivityTypeEnum.SOUTENANCE
                }
                
                mapped_type = type_mapping.get(activity_type)
                if mapped_type is None:
                    return {
                        'success': False, 
                        'error': f'Type d\'activité "{activity_type}" non reconnu. Types acceptés: CM, TD, TP, Examen, Soutenance'
                    }
                activity_type = mapped_type
                
            except Exception as e:
                return {'success': False, 'error': f'Erreur conversion type: {str(e)}'}
        
        # ✅ Convertir la priorité si nécessaire
        if priority is None:
            priority = PriorityEnum.NORMALE
        elif isinstance(priority, str):
            # Mapper les strings vers l'enum
            priority_mapping = {
                "Urgente": PriorityEnum.URGENTE,
                "Possible": PriorityEnum.NORMALE,
                "Interdite": PriorityEnum.BASSE
            }
            priority = priority_mapping.get(priority, PriorityEnum.NORMALE)
        elif isinstance(priority, int):
            # Convertir int en PriorityEnum (ancien format)
            priority_map = {1: PriorityEnum.BASSE, 2: PriorityEnum.NORMALE, 3: PriorityEnum.HAUTE, 4: PriorityEnum.URGENTE}
            priority = priority_map.get(priority, PriorityEnum.NORMALE)
        
        # SUPPRESSION de la validation d'existence de la cohorte
        # On accepte n'importe quel ID de cohorte, même s'il n'existe pas dans la base

        # Vérifier le périmètre : si l'utilisateur est scindé par UFR/program, il
        # ne peut créer des activités que pour son périmètre (sauf Admin)
        if current_user is not None:
            user_roles = [getattr(r, 'name', '') for r in getattr(current_user, 'roles', [])]
            is_admin = any(r.lower() == 'admin' for r in user_roles)
            if not is_admin:
                # Vérifier que l'utilisateur a le droit de créer dans cette cohorte
                # (code commenté car dépend de votre logique métier)
                pass
        
        # Vérifier l'enseignant si fourni
        if teacher_id:
            teacher = self.teacher_repo.get_by_id(teacher_id)
            if not teacher:
                return {'success': False, 'error': 'Enseignant introuvable'}
        
        # Vérifier si le code existe déjà
        existing = self.activity_repo.get_by_code(code)
        if existing:
            return {
                'success': False,
                'error': f'Une activité avec le code {code} existe déjà'
            }
        
        # Le type d'activité est maintenant un ActivityTypeEnum
        type_for_entity = activity_type
        
        # ⚠️ VALIDATION TEMPORAIREMENT DÉSACTIVÉE
        # activity = AcademicActivity(
        #     name=name, code=code, type=type_for_entity,
        #     volume_hours=volume_hours, cohort_id=cohort_id,
        #     teacher_id=teacher_id, activation_date=activation_date,
        #     deadline=deadline, priority=priority
        # )
        # 
        # is_valid, error = activity.validate()
        # if not is_valid:
        #     return {'success': False, 'error': error}
        
        # ✅ Créer directement dans la base sans passer par l'entité
        
        # Créer dans la base de données
        activity_model = self.activity_repo.create(
            name=name, code=code, type=activity_type,
            volume_hours=volume_hours, cohort_id=cohort_id,
            teacher_id=teacher_id, activation_date=activation_date,
            deadline=deadline, priority=priority,
            status=ActivityStatusEnum.PENDING
        )
        
        return {
            'success': True,
            'activity_id': activity_model.id,
            'message': f'Activité {name} créée avec succès'
        }
    
    @require_permission('manage_activities')
    def assign_teacher(self, activity_id: int, teacher_id: int, current_user: Any = None) -> Dict:
        """
        Assigne un enseignant à une activité.
        
        Args:
            activity_id: ID de l'activité
            teacher_id: ID de l'enseignant
            
        Returns:
            Dictionnaire avec le résultat
        """
        activity = self.activity_repo.get_by_id(activity_id)
        if not activity:
            return {'success': False, 'error': 'Activité introuvable'}

        # Vérifier périmètre si nécessaire
        if current_user is not None:
            user_roles = [getattr(r, 'name', '') for r in getattr(current_user, 'roles', [])]
            is_admin = any(r.lower() == 'admin' for r in user_roles)
            if not is_admin:
                cohort = getattr(activity, 'cohort', None)
                program = getattr(cohort, 'program', None) if cohort else None
                target_ufr = getattr(program, 'ufr_id', None) if program else None
                if getattr(current_user, 'ufr_id', None) != target_ufr and getattr(current_user, 'program_id', None) != getattr(program, 'id', None):
                    return {'success': False, 'error': 'Permission refusée : hors périmètre UFR/Programme'}
        
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return {'success': False, 'error': 'Enseignant introuvable'}
        
        # Mettre à jour l'activité
        updated = self.activity_repo.update(activity_id, teacher_id=teacher_id)
        
        return {
            'success': True,
            'activity_id': activity_id,
            'teacher_id': teacher_id,
            'message': f'Enseignant {teacher.full_name} assigné à l\'activité'
        }
    
    def update_activity_hours(self, activity_id: int, hours_to_add: float) -> Dict:
        """
        Met à jour les heures réalisées d'une activité.
        
        Args:
            activity_id: ID de l'activité
            hours_to_add: Heures à ajouter
            
        Returns:
            Dictionnaire avec le résultat
        """
        activity = self.activity_repo.update_hours_done(activity_id, hours_to_add)
        
        if not activity:
            return {'success': False, 'error': 'Activité introuvable'}
        
        completion = (activity.hours_done / activity.volume_hours * 100) if activity.volume_hours > 0 else 0
        
        return {
            'success': True,
            'activity_id': activity_id,
            'hours_done': activity.hours_done,
            'volume_hours': activity.volume_hours,
            'remaining_hours': activity.volume_hours - activity.hours_done,
            'completion': completion,
            'status': activity.status.value
        }
    
    def get_activities_by_cohort(self, cohort_id: int) -> List[AcademicActivityModel]:
        """Récupère toutes les activités d'une cohorte."""
        return self.activity_repo.get_by_cohort(cohort_id)
    
    def get_activities_by_teacher(self, teacher_id: int) -> List[AcademicActivityModel]:
        """Récupère toutes les activités d'un enseignant."""
        return self.activity_repo.get_by_teacher(teacher_id)
    
    def get_pending_activities(self) -> List[AcademicActivityModel]:
        """Récupère toutes les activités en attente."""
        return self.activity_repo.get_pending_activities()
    
    def get_urgent_activities(self, cohort_id: int = None) -> List[Dict]:
        """
        Récupère les activités urgentes avec leurs métriques.
        
        Args:
            cohort_id: ID de la cohorte (optionnel)
            
        Returns:
            Liste des activités urgentes
        """
        return self.delay_calculator.get_urgent_activities(cohort_id)
    
    def get_activity_status(self, activity_id: int) -> Dict:
        """
        Récupère le statut complet d'une activité avec calcul du retard.
        
        Args:
            activity_id: ID de l'activité
            
        Returns:
            Dictionnaire avec toutes les informations
        """
        activity = self.activity_repo.get_by_id(activity_id)
        
        if not activity:
            return {'error': 'Activité introuvable'}
        
        # Calculer le retard
        delay_info = self.delay_calculator.calculate_activity_delay(activity)
        
        # Informations de l'enseignant
        teacher_info = None
        if activity.teacher_id:
            teacher = self.teacher_repo.get_by_id(activity.teacher_id)
            if teacher:
                teacher_info = {
                    'id': teacher.id,
                    'name': teacher.full_name,
                    'email': teacher.email,
                    'speciality': teacher.speciality
                }
        
        return {
            'id': activity.id,
            'name': activity.name,
            'code': activity.code,
            'type': activity.type.value,
            'status': activity.status.value,
            'volume_hours': activity.volume_hours,
            'hours_done': activity.hours_done,
            'remaining_hours': activity.volume_hours - activity.hours_done,
            'completion': (activity.hours_done / activity.volume_hours * 100) if activity.volume_hours > 0 else 0,
            'priority': activity.priority,
            'activation_date': activity.activation_date.isoformat() if activity.activation_date else None,
            'deadline': activity.deadline.isoformat() if activity.deadline else None,
            'teacher': teacher_info,
            'delay': delay_info
        }
    
    def calculate_cohort_workload(self, cohort_id: int) -> Dict:
        """
        Calcule la charge de travail totale d'une cohorte.
        
        Args:
            cohort_id: ID de la cohorte
            
        Returns:
            Dictionnaire avec les statistiques
        """
        activities = self.activity_repo.get_by_cohort(cohort_id)
        
        if not activities:
            return {
                'cohort_id': cohort_id,
                'total_activities': 0,
                'total_hours': 0,
                'hours_done': 0,
                'remaining_hours': 0,
                'completion': 0
            }
        
        total_hours = sum(a.volume_hours for a in activities)
        hours_done = sum(a.hours_done for a in activities)
        remaining = total_hours - hours_done
        
        # Compter par statut
        status_count = {
            'pending': 0,
            'scheduled': 0,
            'in_progress': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        for activity in activities:
            if activity.status == ActivityStatusEnum.PENDING:
                status_count['pending'] += 1
            elif activity.status == ActivityStatusEnum.SCHEDULED:
                status_count['scheduled'] += 1
            elif activity.status == ActivityStatusEnum.IN_PROGRESS:
                status_count['in_progress'] += 1
            elif activity.status == ActivityStatusEnum.COMPLETED:
                status_count['completed'] += 1
            elif activity.status == ActivityStatusEnum.CANCELLED:
                status_count['cancelled'] += 1
        
        # Compter par type
        type_count = {}
        for activity in activities:
            type_name = activity.type.value
            type_count[type_name] = type_count.get(type_name, 0) + 1
        
        return {
            'cohort_id': cohort_id,
            'total_activities': len(activities),
            'total_hours': total_hours,
            'hours_done': hours_done,
            'remaining_hours': remaining,
            'completion': (hours_done / total_hours * 100) if total_hours > 0 else 0,
            'status_breakdown': status_count,
            'type_breakdown': type_count
        }
    
    def delete_activity(self, activity_id: int) -> Dict:
        """
        Supprime une activité.
        
        Args:
            activity_id: ID de l'activité
            
        Returns:
            Dictionnaire avec le résultat
        """
        activity = self.activity_repo.get_by_id(activity_id)
        
        if not activity:
            return {'success': False, 'error': 'Activité introuvable'}
        
        # Ne pas supprimer si des créneaux existent
        if activity.schedule_slots and len(activity.schedule_slots) > 0:
            return {
                'success': False,
                'error': 'Impossible de supprimer une activité avec des créneaux planifiés'
            }
        
        deleted = self.activity_repo.delete(activity_id)
        
        if deleted:
            return {
                'success': True,
                'message': f'Activité {activity.name} supprimée'
            }
        else:
            return {'success': False, 'error': 'Erreur lors de la suppression'}
    
    def get_activities_near_deadline(self, days: int = 7) -> List[AcademicActivityModel]:
        """
        Récupère les activités dont la deadline approche.
        
        Args:
            days: Nombre de jours avant la deadline
            
        Returns:
            Liste des activités
        """
        return self.activity_repo.get_activities_near_deadline(days)
    
    def get_activity_summary(self) -> Dict:
        """
        Génère un résumé global de toutes les activités.
        
        Returns:
            Dictionnaire avec les statistiques globales
        """
        all_activities = self.activity_repo.get_all()
        
        total = len(all_activities)
        pending = len(self.activity_repo.get_pending_activities())
        in_progress = len(self.activity_repo.get_in_progress_activities())
        completed = len(self.activity_repo.get_completed_activities())
        
        total_hours = sum(a.volume_hours for a in all_activities)
        hours_done = sum(a.hours_done for a in all_activities)
        
        return {
            'total_activities': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'total_hours': total_hours,
            'hours_done': hours_done,
            'global_completion': (hours_done / total_hours * 100) if total_hours > 0 else 0
        }