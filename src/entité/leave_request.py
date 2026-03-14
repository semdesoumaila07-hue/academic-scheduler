"""
Entité LeaveRequest (Demande de Congé).
"""
from typing import Optional
from datetime import datetime, date
from ..utils.constants import LeaveStatus, LeaveType
from ..utils.helpers import count_workdays


class LeaveRequest:
    """
    Représente une demande de congé d'un enseignant.
    
    Attributes:
        id: Identifiant unique
        teacher_id: ID de l'enseignant
        start_date: Date de début du congé
        end_date: Date de fin du congé
        leave_type: Type de congé
        reason: Raison du congé
        status: Statut de la demande
        working_days: Nombre de jours ouvrés
        approver_email: Email de l'approbateur
        approved_at: Date d'approbation
        rejected_at: Date de rejet
        rejection_reason: Raison du rejet
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        teacher_id: int,
        start_date: date,
        end_date: date,
        leave_type: LeaveType,
        reason: str,
        status: LeaveStatus = LeaveStatus.PENDING,
        working_days: Optional[int] = None,
        approver_email: Optional[str] = None,
        approved_at: Optional[datetime] = None,
        rejected_at: Optional[datetime] = None,
        rejection_reason: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une demande de congé.
        
        Args:
            teacher_id: ID de l'enseignant
            start_date: Date de début
            end_date: Date de fin
            leave_type: Type de congé
            reason: Raison
            status: Statut
            working_days: Jours ouvrés
            approver_email: Email approbateur
            approved_at: Date d'approbation
            rejected_at: Date de rejet
            rejection_reason: Raison du rejet
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.teacher_id = teacher_id
        self.start_date = start_date
        self.end_date = end_date
        self.leave_type = leave_type
        self.reason = reason
        self.status = status
        self.working_days = working_days or self._calculate_working_days()
        self.approver_email = approver_email
        self.approved_at = approved_at
        self.rejected_at = rejected_at
        self.rejection_reason = rejection_reason
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def _calculate_working_days(self) -> int:
        """
        Calcule le nombre de jours ouvrés.
        
        Returns:
            Nombre de jours ouvrés
        """
        return count_workdays(self.start_date, self.end_date)
    
    def approve(self, approver_email: str) -> None:
        """
        Approuve la demande de congé.
        
        Args:
            approver_email: Email de l'approbateur
        """
        self.status = LeaveStatus.APPROVED
        self.approver_email = approver_email
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()
    
    def reject(self, approver_email: str, reason: str) -> None:
        """
        Rejette la demande de congé.
        
        Args:
            approver_email: Email de l'approbateur
            reason: Raison du rejet
        """
        self.status = LeaveStatus.REJECTED
        self.approver_email = approver_email
        self.rejection_reason = reason
        self.rejected_at = datetime.now()
        self.updated_at = datetime.now()
    
    def cancel(self) -> None:
        """Annule la demande de congé."""
        self.status = LeaveStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def block_schedule_slots(self, schedule_slots: list) -> list:
        """
        Bloque les créneaux horaires pendant la période de congé.
        
        Args:
            schedule_slots: Liste des créneaux à vérifier
            
        Returns:
            Liste des créneaux bloqués
        """
        blocked_slots = []
        
        for slot in schedule_slots:
            if (slot.teacher_id == self.teacher_id and 
                self.start_date <= slot.date <= self.end_date):
                slot.blocked_by_leave = True
                slot.notes = f"Enseignant en congé ({self.leave_type.value})"
                blocked_slots.append(slot)
        
        return blocked_slots
    
    def overlaps_with(self, other: 'LeaveRequest') -> bool:
        """
        Vérifie si cette demande chevauche une autre demande.
        
        Args:
            other: Autre demande de congé
            
        Returns:
            True si chevauchement, False sinon
        """
        if self.teacher_id != other.teacher_id:
            return False
        
        return (self.start_date <= other.end_date and 
                self.end_date >= other.start_date)
    
    def is_active(self, check_date: date = None) -> bool:
        """
        Vérifie si le congé est actif à une date donnée.
        
        Args:
            check_date: Date à vérifier (aujourd'hui par défaut)
            
        Returns:
            True si actif, False sinon
        """
        if self.status != LeaveStatus.APPROVED:
            return False
        
        if check_date is None:
            check_date = date.today()
        
        return self.start_date <= check_date <= self.end_date
    
    def to_dict(self) -> dict:
        """
        Convertit la demande en dictionnaire.
        
        Returns:
            Dictionnaire représentant la demande
        """
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'leave_type': self.leave_type.value if isinstance(self.leave_type, LeaveType) else self.leave_type,
            'reason': self.reason,
            'status': self.status.value if isinstance(self.status, LeaveStatus) else self.status,
            'working_days': self.working_days,
            'approver_email': self.approver_email,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LeaveRequest':
        """
        Crée une demande depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de LeaveRequest
        """
        # Convertir les enums
        leave_type = data['leave_type']
        if isinstance(leave_type, str):
            leave_type = LeaveType(leave_type)
        
        status = data.get('status', 'En attente')
        if isinstance(status, str):
            status = LeaveStatus(status)
        
        return cls(
            id=data.get('id'),
            teacher_id=data['teacher_id'],
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            leave_type=leave_type,
            reason=data['reason'],
            status=status,
            working_days=data.get('working_days'),
            approver_email=data.get('approver_email'),
            approved_at=datetime.fromisoformat(data['approved_at']) if data.get('approved_at') else None,
            rejected_at=datetime.fromisoformat(data['rejected_at']) if data.get('rejected_at') else None,
            rejection_reason=data.get('rejection_reason'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de la demande."""
        return f"Congé {self.leave_type.value} du {self.start_date} au {self.end_date} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Représentation technique de la demande."""
        return f"LeaveRequest(id={self.id}, teacher_id={self.teacher_id}, status={self.status})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de la demande.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.teacher_id or self.teacher_id <= 0:
            return False, "L'ID de l'enseignant est requis"
        
        if not self.start_date:
            return False, "La date de début est requise"
        
        if not self.end_date:
            return False, "La date de fin est requise"
        
        if self.start_date > self.end_date:
            return False, "La date de fin doit être après la date de début"
        
        if not isinstance(self.leave_type, LeaveType):
            return False, "Le type de congé doit être un LeaveType valide"
        
        if not self.reason or len(self.reason.strip()) == 0:
            return False, "La raison est requise"
        
        if not isinstance(self.status, LeaveStatus):
            return False, "Le statut doit être un LeaveStatus valide"
        
        # Vérifier que la durée est raisonnable (max 365 jours)
        duration = (self.end_date - self.start_date).days
        if duration > 365:
            return False, "La durée du congé ne peut pas dépasser 365 jours"
        
        return True, None