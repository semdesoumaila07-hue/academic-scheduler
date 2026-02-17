"""
Repository pour les Cohortes/Classes.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base_repository import BaseRepository
from ..models import CohortModel


class CohortRepository(BaseRepository[CohortModel]):
    """Repository pour les opérations sur les cohortes."""
    
    def __init__(self, session: Session):
        super().__init__(CohortModel, session)
    
    def get_by_program(self, program_id: int) -> List[CohortModel]:
        """Récupère toutes les cohortes d'un programme."""
        return self.filter_by(program_id=program_id)
    
    def get_by_academic_year(self, academic_year: str) -> List[CohortModel]:
        """Récupère les cohortes d'une année académique."""
        return self.filter_by(academic_year=academic_year)
    
    def get_active_cohorts(self, reference_date: date = None) -> List[CohortModel]:
        """Récupère les cohortes actives à une date donnée."""
        if reference_date is None:
            reference_date = date.today()
        
        return self.session.query(self.model).filter(
            and_(
                self.model.start_date <= reference_date,
                self.model.end_date >= reference_date
            )
        ).all()
    
    def get_with_students(self, cohort_id: int) -> Optional[CohortModel]:
        """Récupère une cohorte avec tous ses étudiants."""
        from sqlalchemy.orm import joinedload
        return self.session.query(self.model).options(
            joinedload(self.model.students)
        ).filter(self.model.id == cohort_id).first()