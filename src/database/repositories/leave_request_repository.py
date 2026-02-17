"""
Repository pour les Demandes de Congé.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .base_repository import BaseRepository
from ..models import LeaveRequestModel, LeaveStatusEnum


class LeaveRequestRepository(BaseRepository[LeaveRequestModel]):
    """Repository pour les opérations sur les demandes de congé."""
    
    def __init__(self, session: Session):
        super().__init__(LeaveRequestModel, session)
    
    def get_by_teacher(self, teacher_id: int) -> List[LeaveRequestModel]:
        """Récupère toutes les demandes d'un enseignant."""
        return self.filter_by(teacher_id=teacher_id)
    
    def get_by_status(self, status: LeaveStatusEnum) -> List[LeaveRequestModel]:
        """Récupère les demandes par statut."""
        return self.filter_by(status=status)
    
    def get_pending_requests(self) -> List[LeaveRequestModel]:
        """Récupère toutes les demandes en attente."""
        return self.filter_by(status=LeaveStatusEnum.PENDING)
    
    def get_approved_requests(self) -> List[LeaveRequestModel]:
        """Récupère toutes les demandes approuvées."""
        return self.filter_by(status=LeaveStatusEnum.APPROVED)
    
    def get_active_leaves(self, reference_date: date = None) -> List[LeaveRequestModel]:
        """Récupère les congés actifs à une date donnée."""
        if reference_date is None:
            reference_date = date.today()
        
        return self.session.query(self.model).filter(
            and_(
                self.model.status == LeaveStatusEnum.APPROVED,
                self.model.start_date <= reference_date,
                self.model.end_date >= reference_date
            )
        ).all()
    
    def get_teacher_leaves(self, teacher_id: int, start_date: date, end_date: date) -> List[LeaveRequestModel]:
        """Récupère les congés d'un enseignant sur une période."""
        return self.session.query(self.model).filter(
            and_(
                self.model.teacher_id == teacher_id,
                self.model.status == LeaveStatusEnum.APPROVED,
                or_(
                    and_(self.model.start_date >= start_date, self.model.start_date <= end_date),
                    and_(self.model.end_date >= start_date, self.model.end_date <= end_date),
                    and_(self.model.start_date <= start_date, self.model.end_date >= end_date)
                )
            )
        ).all()
    
    def check_overlap(self, teacher_id: int, start_date: date, end_date: date, exclude_id: int = None) -> bool:
        """Vérifie si une demande chevauche d'autres congés."""
        query = self.session.query(self.model).filter(
            and_(
                self.model.teacher_id == teacher_id,
                self.model.status.in_([LeaveStatusEnum.PENDING, LeaveStatusEnum.APPROVED]),
                or_(
                    and_(self.model.start_date >= start_date, self.model.start_date <= end_date),
                    and_(self.model.end_date >= start_date, self.model.end_date <= end_date),
                    and_(self.model.start_date <= start_date, self.model.end_date >= end_date)
                )
            )
        )
        
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        
        return query.count() > 0
    
    def approve_request(self, request_id: int, approver_email: str) -> Optional[LeaveRequestModel]:
        """Approuve une demande de congé."""
        from datetime import datetime
        
        request = self.get_by_id(request_id)
        if not request or request.status != LeaveStatusEnum.PENDING:
            return None
        
        request.status = LeaveStatusEnum.APPROVED
        request.approver_email = approver_email
        request.approved_at = datetime.now()
        
        self.session.commit()
        self.session.refresh(request)
        
        return request
    
    def reject_request(self, request_id: int, approver_email: str, reason: str) -> Optional[LeaveRequestModel]:
        """Rejette une demande de congé."""
        from datetime import datetime
        
        request = self.get_by_id(request_id)
        if not request or request.status != LeaveStatusEnum.PENDING:
            return None
        
        request.status = LeaveStatusEnum.REJECTED
        request.approver_email = approver_email
        request.rejection_reason = reason
        request.rejected_at = datetime.now()
        
        self.session.commit()
        self.session.refresh(request)
        
        return request