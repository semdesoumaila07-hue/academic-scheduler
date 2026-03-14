"""
Repository pour les Calendriers Académiques.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import AcademicCalendarModel


class CalendarRepository(BaseRepository[AcademicCalendarModel]):
    """Repository pour les opérations sur les calendriers académiques."""
    
    def __init__(self, session: Session):
        super().__init__(AcademicCalendarModel, session)
    
    def get_by_academic_year(self, academic_year: str) -> Optional[AcademicCalendarModel]:
        """Récupère un calendrier par année académique."""
        return self.first_by(academic_year=academic_year)
    
    def get_current_calendar(self, reference_date: date = None) -> Optional[AcademicCalendarModel]:
        """Récupère le calendrier actif à une date donnée."""
        from sqlalchemy import and_
        
        if reference_date is None:
            reference_date = date.today()
        
        return self.session.query(self.model).filter(
            and_(
                self.model.start_date <= reference_date,
                self.model.end_date >= reference_date
            )
        ).first()
    
    def get_with_holidays(self, calendar_id: int) -> Optional[AcademicCalendarModel]:
        """Récupère un calendrier avec tous ses jours fériés."""
        from sqlalchemy.orm import joinedload
        
        return self.session.query(self.model).options(
            joinedload(self.model.holidays)
        ).filter(self.model.id == calendar_id).first()
    
    def get_with_vacations(self, calendar_id: int) -> Optional[AcademicCalendarModel]:
        """Récupère un calendrier avec toutes ses périodes de vacances."""
        from sqlalchemy.orm import joinedload
        
        return self.session.query(self.model).options(
            joinedload(self.model.vacation_periods)
        ).filter(self.model.id == calendar_id).first()
    
    def get_complete_calendar(self, calendar_id: int) -> Optional[AcademicCalendarModel]:
        """Récupère un calendrier avec tous ses jours fériés et périodes de vacances."""
        from sqlalchemy.orm import joinedload
        
        return self.session.query(self.model).options(
            joinedload(self.model.holidays),
            joinedload(self.model.vacation_periods)
        ).filter(self.model.id == calendar_id).first()