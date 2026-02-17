"""
Repository pour les Périodes de Vacances.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .base_repository import BaseRepository
from ..models import VacationPeriodModel, VacationTypeEnum


class VacationPeriodRepository(BaseRepository[VacationPeriodModel]):
    """Repository pour les opérations sur les périodes de vacances."""
    
    def __init__(self, session: Session):
        super().__init__(VacationPeriodModel, session)
    
    def get_by_calendar(self, calendar_id: int) -> List[VacationPeriodModel]:
        """Récupère toutes les périodes de vacances d'un calendrier."""
        return self.filter_by(calendar_id=calendar_id)
    
    def get_by_type(self, vacation_type: VacationTypeEnum, calendar_id: int = None) -> List[VacationPeriodModel]:
        """Récupère les périodes de vacances par type."""
        query = self.session.query(self.model).filter(self.model.type == vacation_type)
        
        if calendar_id:
            query = query.filter(self.model.calendar_id == calendar_id)
        
        return query.all()
    
    def get_active_vacations(self, reference_date: date = None, calendar_id: int = None) -> List[VacationPeriodModel]:
        """Récupère les périodes de vacances actives à une date donnée."""
        if reference_date is None:
            reference_date = date.today()
        
        query = self.session.query(self.model).filter(
            and_(
                self.model.start_date <= reference_date,
                self.model.end_date >= reference_date
            )
        )
        
        if calendar_id:
            query = query.filter(self.model.calendar_id == calendar_id)
        
        return query.all()
    
    def get_vacations_in_range(self, calendar_id: int, start_date: date, end_date: date) -> List[VacationPeriodModel]:
        """Récupère les périodes de vacances dans une plage de dates."""
        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                or_(
                    # La période de vacances commence dans la plage
                    and_(self.model.start_date >= start_date, self.model.start_date <= end_date),
                    # La période de vacances se termine dans la plage
                    and_(self.model.end_date >= start_date, self.model.end_date <= end_date),
                    # La période de vacances englobe toute la plage
                    and_(self.model.start_date <= start_date, self.model.end_date >= end_date)
                )
            )
        ).order_by(self.model.start_date).all()
    
    def is_vacation(self, check_date: date, calendar_id: int) -> bool:
        """Vérifie si une date est dans une période de vacances."""
        count = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.start_date <= check_date,
                self.model.end_date >= check_date
            )
        ).count()
        
        return count > 0
    
    def check_overlap(self, calendar_id: int, start_date: date, end_date: date, exclude_id: int = None) -> bool:
        """Vérifie si une période chevauche d'autres périodes de vacances."""
        query = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
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
    
    def get_next_vacation(self, calendar_id: int, reference_date: date = None) -> Optional[VacationPeriodModel]:
        """Récupère la prochaine période de vacances."""
        if reference_date is None:
            reference_date = date.today()
        
        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.start_date > reference_date
            )
        ).order_by(self.model.start_date).first()