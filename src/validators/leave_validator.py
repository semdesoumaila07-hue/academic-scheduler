"""
Validateur pour les demandes de congés.

Vérifie la validité et la cohérence des demandes de congés.
"""
from typing import Tuple, Optional, List
from datetime import date, timedelta

from ..database.models import (
    LeaveRequestModel, LeaveTypeEnum, LeaveStatusEnum, 
    TeacherModel, ScheduleSlotModel
)


class LeaveValidator:
    """
    Validateur pour les demandes de congés.
    
    Vérifie :
    - Validité des dates
    - Durée du congé
    - Chevauchements
    - Impact sur l'emploi du temps
    """
    
    # Durées maximales par type de congé (en jours)
    MAX_DURATIONS = {
        LeaveTypeEnum.MALADIE: 90,
        LeaveTypeEnum.CONGE_ANNUEL: 30,
        LeaveTypeEnum.FORMATION: 15,
        LeaveTypeEnum.MATERNITE: 120,
        LeaveTypeEnum.SANS_SOLDE: 365,
        LeaveTypeEnum.AUTRE: 30,
    }
    
    @staticmethod
    def validate_dates(start_date: date, end_date: date) -> Tuple[bool, Optional[str]]:
        """
        Valide les dates d'une demande de congé.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier l'ordre des dates
        if end_date < start_date:
            return False, "La date de fin doit être après la date de début"
        
        # Vérifier que le début n'est pas dans le passé (sauf urgence)
        today = date.today()
        if start_date < today - timedelta(days=1):
            return False, "Impossible de demander un congé pour une date passée"
        
        # Vérifier que le congé ne commence pas trop loin dans le futur (> 6 mois)
        max_advance = today + timedelta(days=180)
        if start_date > max_advance:
            return False, "Impossible de planifier un congé plus de 6 mois à l'avance"
        
        return True, None
    
    @staticmethod
    def validate_duration(start_date: date, end_date: date, 
                         leave_type: LeaveTypeEnum) -> Tuple[bool, Optional[str]]:
        """
        Valide la durée d'un congé.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            leave_type: Type de congé
            
        Returns:
            Tuple (valide, message_erreur)
        """
        duration = (end_date - start_date).days + 1
        
        # Vérifier la durée minimale (1 jour)
        if duration < 1:
            return False, "La durée minimale d'un congé est d'1 jour"
        
        # Vérifier la durée maximale selon le type
        max_duration = LeaveValidator.MAX_DURATIONS.get(leave_type, 30)
        
        if duration > max_duration:
            return False, f"La durée maximale pour ce type de congé est de {max_duration} jours"
        
        return True, None
    
    @staticmethod
    def validate_reason(reason: str) -> Tuple[bool, Optional[str]]:
        """
        Valide la raison d'une demande.
        
        Args:
            reason: Raison du congé
            
        Returns:
            Tuple (valide, message_erreur)
        """
        if not reason or not reason.strip():
            return False, "La raison est obligatoire"
        
        if len(reason) < 10:
            return False, "La raison doit contenir au moins 10 caractères"
        
        if len(reason) > 500:
            return False, "La raison ne peut pas dépasser 500 caractères"
        
        return True, None
    
    @staticmethod
    def check_overlap(teacher_id: int, start_date: date, end_date: date,
                     existing_leaves: List[LeaveRequestModel],
                     exclude_id: int = None) -> Tuple[bool, Optional[str]]:
        """
        Vérifie les chevauchements avec d'autres congés.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début
            end_date: Date de fin
            existing_leaves: Congés existants
            exclude_id: ID à exclure (pour modification)
            
        Returns:
            Tuple (pas_de_conflit, message_erreur)
        """
        for leave in existing_leaves:
            # Ignorer sa propre demande (en cas de modification)
            if exclude_id and leave.id == exclude_id:
                continue
            
            # Ignorer les congés rejetés ou annulés
            if leave.status in [LeaveStatusEnum.REJECTED, LeaveStatusEnum.CANCELLED]:
                continue
            
            # Vérifier le chevauchement
            if (start_date <= leave.end_date and end_date >= leave.start_date):
                return False, (
                    f"Chevauchement avec un congé existant "
                    f"({leave.start_date} - {leave.end_date})"
                )
        
        return True, None
    
    @staticmethod
    def check_schedule_impact(teacher_id: int, start_date: date, end_date: date,
                             scheduled_slots: List[ScheduleSlotModel]) -> Tuple[bool, int, List[str]]:
        """
        Vérifie l'impact sur l'emploi du temps.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début du congé
            end_date: Date de fin du congé
            scheduled_slots: Créneaux planifiés
            
        Returns:
            Tuple (a_impact, nombre_créneaux_affectés, détails)
        """
        affected_slots = []
        details = []
        
        for slot in scheduled_slots:
            if start_date <= slot.date <= end_date:
                affected_slots.append(slot)
                details.append(
                    f"{slot.date} {slot.start_time}-{slot.end_time}"
                )
        
        has_impact = len(affected_slots) > 0
        
        return has_impact, len(affected_slots), details
    
    @staticmethod
    def validate_approval(leave_request: LeaveRequestModel,
                         approver_email: str) -> Tuple[bool, Optional[str]]:
        """
        Valide une approbation de congé.
        
        Args:
            leave_request: Demande de congé
            approver_email: Email de l'approbateur
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier le statut
        if leave_request.status != LeaveStatusEnum.PENDING:
            return False, f"La demande est déjà {leave_request.status.value}"
        
        # Vérifier l'email de l'approbateur
        if not approver_email or '@' not in approver_email:
            return False, "Email de l'approbateur invalide"
        
        # Vérifier que le congé n'est pas déjà passé
        if leave_request.end_date < date.today():
            return False, "Impossible d'approuver un congé déjà terminé"
        
        return True, None
    
    @staticmethod
    def validate_rejection(leave_request: LeaveRequestModel,
                          rejection_reason: str) -> Tuple[bool, Optional[str]]:
        """
        Valide un rejet de congé.
        
        Args:
            leave_request: Demande de congé
            rejection_reason: Raison du rejet
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier le statut
        if leave_request.status != LeaveStatusEnum.PENDING:
            return False, f"La demande est déjà {leave_request.status.value}"
        
        # Vérifier la raison du rejet
        if not rejection_reason or not rejection_reason.strip():
            return False, "La raison du rejet est obligatoire"
        
        if len(rejection_reason) < 10:
            return False, "La raison du rejet doit contenir au moins 10 caractères"
        
        return True, None
    
    @staticmethod
    def validate_cancellation(leave_request: LeaveRequestModel) -> Tuple[bool, Optional[str]]:
        """
        Valide une annulation de congé.
        
        Args:
            leave_request: Demande de congé
            
        Returns:
            Tuple (valide, message_erreur)
        """
        # Vérifier le statut
        if leave_request.status == LeaveStatusEnum.CANCELLED:
            return False, "La demande est déjà annulée"
        
        if leave_request.status == LeaveStatusEnum.REJECTED:
            return False, "Impossible d'annuler une demande rejetée"
        
        # Vérifier que le congé n'est pas déjà commencé
        if leave_request.start_date < date.today():
            return False, "Impossible d'annuler un congé déjà commencé"
        
        return True, None
    
    @staticmethod
    def validate_complete_request(start_date: date, end_date: date,
                                 leave_type: LeaveTypeEnum, reason: str,
                                 teacher: TeacherModel,
                                 existing_leaves: List[LeaveRequestModel],
                                 scheduled_slots: List[ScheduleSlotModel]) -> Tuple[bool, List[str], dict]:
        """
        Validation complète d'une demande de congé.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            leave_type: Type de congé
            reason: Raison
            teacher: Enseignant
            existing_leaves: Congés existants
            scheduled_slots: Créneaux planifiés
            
        Returns:
            Tuple (valide, liste_erreurs, informations_impact)
        """
        errors = []
        
        # Valider les dates
        valid, error = LeaveValidator.validate_dates(start_date, end_date)
        if not valid:
            errors.append(error)
        
        # Valider la durée
        valid, error = LeaveValidator.validate_duration(start_date, end_date, leave_type)
        if not valid:
            errors.append(error)
        
        # Valider la raison
        valid, error = LeaveValidator.validate_reason(reason)
        if not valid:
            errors.append(error)
        
        # Vérifier les chevauchements
        valid, error = LeaveValidator.check_overlap(
            teacher.id, start_date, end_date, existing_leaves
        )
        if not valid:
            errors.append(error)
        
        # Vérifier l'impact sur l'emploi du temps
        has_impact, affected_count, details = LeaveValidator.check_schedule_impact(
            teacher.id, start_date, end_date, scheduled_slots
        )
        
        impact_info = {
            'has_impact': has_impact,
            'affected_slots_count': affected_count,
            'affected_slots_details': details
        }
        
        return len(errors) == 0, errors, impact_info