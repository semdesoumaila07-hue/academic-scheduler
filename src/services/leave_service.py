"""
Service de gestion des demandes de congés.

Gère la soumission, validation, approbation et rejet des demandes de congés.
"""
from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session

from ..database.repositories import LeaveRequestRepository, ScheduleRepository, TeacherRepository
from ..database.models import LeaveRequestModel, LeaveStatusEnum, LeaveTypeEnum
from .calendar_service import CalendarService
<<<<<<< HEAD
from .auth_service import require_permission
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f


class LeaveService:
    """
    Service pour la gestion des demandes de congés.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le service de gestion des congés.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.leave_repo = LeaveRequestRepository(session)
        self.schedule_repo = ScheduleRepository(session)
        self.teacher_repo = TeacherRepository(session)
        self.calendar_service = CalendarService(session)
    
<<<<<<< HEAD
    @require_permission('submit_leave')
    def submit_leave_request(self, teacher_id: int, start_date: date, end_date: date,
                            leave_type: LeaveTypeEnum, reason: str, current_user=None) -> Dict:
=======
    def submit_leave_request(self, teacher_id: int, start_date: date, end_date: date,
                            leave_type: LeaveTypeEnum, reason: str) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Soumet une nouvelle demande de congé.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début du congé
            end_date: Date de fin du congé
            leave_type: Type de congé
            reason: Raison du congé
            
        Returns:
            Dictionnaire avec le résultat de la soumission
        """
        # Vérifier que l'enseignant existe
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return {
                'success': False,
                'error': 'Enseignant introuvable'
            }
        
        # Vérifier les dates
        if start_date > end_date:
            return {
                'success': False,
                'error': 'La date de fin doit être après la date de début'
            }
        
        # Vérifier les chevauchements avec d'autres congés
        if self.leave_repo.check_overlap(teacher_id, start_date, end_date):
            return {
                'success': False,
                'error': 'Cette période chevauche un autre congé existant'
            }
        
        # Calculer le nombre de jours ouvrables
        working_days = self.calendar_service.calculate_effective_days(start_date, end_date)
        
        # Créer la demande
        leave_request = self.leave_repo.create(
            teacher_id=teacher_id,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason,
            status=LeaveStatusEnum.PENDING,
            working_days=working_days
        )
        
        return {
            'success': True,
            'leave_request_id': leave_request.id,
            'working_days': working_days,
            'status': LeaveStatusEnum.PENDING.value,
            'message': 'Demande de congé soumise avec succès'
        }
    
<<<<<<< HEAD
    @require_permission('approve_leave')
    def approve_leave_request(self, request_id: int, approver_email: str, current_user=None) -> Dict:
=======
    def approve_leave_request(self, request_id: int, approver_email: str) -> Dict:
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        """
        Approuve une demande de congé et bloque les créneaux concernés.
        
        Args:
            request_id: ID de la demande
            approver_email: Email de l'approbateur
            
        Returns:
            Dictionnaire avec le résultat de l'approbation
        """
        # Récupérer la demande
        leave_request = self.leave_repo.get_by_id(request_id)
        
        if not leave_request:
            return {
                'success': False,
                'error': 'Demande introuvable'
            }
        
        if leave_request.status != LeaveStatusEnum.PENDING:
            return {
                'success': False,
                'error': f'La demande est déjà {leave_request.status.value}'
            }
        
        # Approuver la demande
        leave_request = self.leave_repo.approve_request(request_id, approver_email)
        
        # Bloquer tous les créneaux de l'enseignant pendant cette période
        blocked_count = self.schedule_repo.block_slots_by_leave(
            leave_request.teacher_id,
            leave_request.start_date,
            leave_request.end_date
        )
        
        return {
            'success': True,
            'leave_request_id': request_id,
            'status': LeaveStatusEnum.APPROVED.value,
            'blocked_slots': blocked_count,
            'message': f'Demande approuvée. {blocked_count} créneaux bloqués.'
        }
    
    def reject_leave_request(self, request_id: int, approver_email: str, 
                           rejection_reason: str) -> Dict:
        """
        Rejette une demande de congé.
        
        Args:
            request_id: ID de la demande
            approver_email: Email de l'approbateur
            rejection_reason: Raison du rejet
            
        Returns:
            Dictionnaire avec le résultat du rejet
        """
        # Récupérer la demande
        leave_request = self.leave_repo.get_by_id(request_id)
        
        if not leave_request:
            return {
                'success': False,
                'error': 'Demande introuvable'
            }
        
        if leave_request.status != LeaveStatusEnum.PENDING:
            return {
                'success': False,
                'error': f'La demande est déjà {leave_request.status.value}'
            }
        
        # Rejeter la demande
        leave_request = self.leave_repo.reject_request(
            request_id, 
            approver_email, 
            rejection_reason
        )
        
        return {
            'success': True,
            'leave_request_id': request_id,
            'status': LeaveStatusEnum.REJECTED.value,
            'message': 'Demande rejetée'
        }
    
    def cancel_leave_request(self, request_id: int) -> Dict:
        """
        Annule une demande de congé (par l'enseignant lui-même).
        
        Args:
            request_id: ID de la demande
            
        Returns:
            Dictionnaire avec le résultat de l'annulation
        """
        leave_request = self.leave_repo.get_by_id(request_id)
        
        if not leave_request:
            return {
                'success': False,
                'error': 'Demande introuvable'
            }
        
        # Si la demande était approuvée, débloquer les créneaux
        unblocked_count = 0
        if leave_request.status == LeaveStatusEnum.APPROVED:
            unblocked_count = self.schedule_repo.unblock_slots_by_leave(
                leave_request.teacher_id,
                leave_request.start_date,
                leave_request.end_date
            )
        
        # Mettre à jour le statut
        leave_request.status = LeaveStatusEnum.CANCELLED
        self.session.commit()
        
        return {
            'success': True,
            'leave_request_id': request_id,
            'status': LeaveStatusEnum.CANCELLED.value,
            'unblocked_slots': unblocked_count,
            'message': 'Demande annulée'
        }
    
<<<<<<< HEAD
    def get_all_requests(self) -> List[LeaveRequestModel]:
        """
        Récupère toutes les demandes de congé (pour affichage dans l'onglet).
        
        Returns:
            Liste de toutes les demandes
        """
        return self.leave_repo.get_all(skip=0, limit=500)

=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
    def get_pending_requests(self) -> List[LeaveRequestModel]:
        """
        Récupère toutes les demandes en attente.
        
        Returns:
            Liste des demandes en attente
        """
        return self.leave_repo.get_pending_requests()
    
    def get_teacher_leaves(self, teacher_id: int, start_date: date = None, 
                          end_date: date = None) -> List[LeaveRequestModel]:
        """
        Récupère les congés d'un enseignant.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Liste des demandes de congés
        """
        if start_date and end_date:
            return self.leave_repo.get_teacher_leaves(teacher_id, start_date, end_date)
        else:
            return self.leave_repo.get_by_teacher(teacher_id)
    
    def get_active_leaves(self, reference_date: date = None) -> List[LeaveRequestModel]:
        """
        Récupère tous les congés actifs.
        
        Args:
            reference_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Liste des congés actifs
        """
        return self.leave_repo.get_active_leaves(reference_date)
    
    def check_teacher_availability(self, teacher_id: int, check_date: date) -> Dict:
        """
        Vérifie si un enseignant est disponible à une date donnée.
        
        Args:
            teacher_id: ID de l'enseignant
            check_date: Date à vérifier
            
        Returns:
            Dictionnaire avec le statut de disponibilité
        """
        # Vérifier s'il y a un congé actif
        leaves = self.leave_repo.get_teacher_leaves(
            teacher_id, 
            check_date, 
            check_date
        )
        
        if leaves:
            leave = leaves[0]
            return {
                'available': False,
                'reason': 'En congé',
                'leave_type': leave.leave_type.value,
                'start_date': leave.start_date,
                'end_date': leave.end_date
            }
        
        return {
            'available': True
        }
    
    def get_leave_statistics(self, teacher_id: int = None) -> Dict:
        """
        Calcule les statistiques sur les congés.
        
        Args:
            teacher_id: ID de l'enseignant (optionnel, sinon tous)
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if teacher_id:
            leaves = self.leave_repo.get_by_teacher(teacher_id)
        else:
            leaves = self.leave_repo.get_all()
        
        stats = {
            'total': len(leaves),
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'cancelled': 0,
            'total_days': 0
        }
        
        for leave in leaves:
            if leave.status == LeaveStatusEnum.PENDING:
                stats['pending'] += 1
            elif leave.status == LeaveStatusEnum.APPROVED:
                stats['approved'] += 1
                stats['total_days'] += leave.working_days or 0
            elif leave.status == LeaveStatusEnum.REJECTED:
                stats['rejected'] += 1
            elif leave.status == LeaveStatusEnum.CANCELLED:
                stats['cancelled'] += 1
        
        return stats