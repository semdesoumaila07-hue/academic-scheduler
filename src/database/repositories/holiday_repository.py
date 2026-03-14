"""
Repository pour les Jours Fériés.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base_repository import BaseRepository
from ..models import HolidayModel


class HolidayRepository(BaseRepository[HolidayModel]):
    """Repository pour les opérations sur les jours fériés."""
    
    def __init__(self, session: Session):
        super().__init__(HolidayModel, session)
    
    def get_by_calendar(self, calendar_id: int) -> List[HolidayModel]:
        """Récupère tous les jours fériés d'un calendrier."""
        return self.filter_by(calendar_id=calendar_id)
    
    def get_recurring_holidays(self, calendar_id: int = None) -> List[HolidayModel]:
        """Récupère les jours fériés récurrents."""
        query = self.session.query(self.model).filter(self.model.is_recurring == True)
        
        if calendar_id:
            query = query.filter(self.model.calendar_id == calendar_id)
        
        return query.all()
    
    def get_holidays_in_range(self, calendar_id: int, start_date: date, end_date: date) -> List[HolidayModel]:
        """Récupère les jours fériés dans une période."""
        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        ).order_by(self.model.date).all()
    
    def is_holiday(self, check_date: date, calendar_id: int) -> bool:
        """Vérifie si une date est un jour férié."""
        # Vérifier les jours fériés exacts
        exact_holiday = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.date == check_date
            )
        ).first()
        
        if exact_holiday:
            return True
        
        # Vérifier les jours fériés récurrents (même jour/mois)
        recurring_holiday = self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                self.model.is_recurring == True
            )
        ).all()
        
        for holiday in recurring_holiday:
            if holiday.date.day == check_date.day and holiday.date.month == check_date.month:
                return True
        
        return False
    
    def get_holidays_by_month(self, calendar_id: int, year: int, month: int) -> List[HolidayModel]:
        """Récupère les jours fériés d'un mois donné."""
        from sqlalchemy import extract
        
        return self.session.query(self.model).filter(
            and_(
                self.model.calendar_id == calendar_id,
                extract('year', self.model.date) == year,
                extract('month', self.model.date) == month
            )
        ).order_by(self.model.date).all()