"""
Repository pour les Étudiants.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import StudentModel


class StudentRepository(BaseRepository[StudentModel]):
    """Repository pour les opérations sur les étudiants."""
    
    def __init__(self, session: Session):
        super().__init__(StudentModel, session)
    
    def get_by_student_id(self, student_id: str) -> Optional[StudentModel]:
        """Récupère un étudiant par son matricule."""
        return self.first_by(student_id=student_id)
    
    def get_by_email(self, email: str) -> Optional[StudentModel]:
        """Récupère un étudiant par son email."""
        return self.first_by(email=email)
    
    def get_by_cohort(self, cohort_id: int) -> List[StudentModel]:
        """Récupère tous les étudiants d'une cohorte."""
        return self.filter_by(cohort_id=cohort_id)
    
    def search_by_name(self, name: str) -> List[StudentModel]:
        """Recherche des étudiants par nom (partiel)."""
        return self.session.query(self.model).filter(
            self.model.full_name.like(f"%{name}%")
        ).all()
    
    def get_student_schedule(self, student_id: int, start_date: date, end_date: date):
        """Récupère l'emploi du temps d'un étudiant via sa cohorte."""
        from ..models import ScheduleSlotModel
        from sqlalchemy import and_
        
        student = self.get_by_id(student_id)
        if not student:
            return []
        
        return self.session.query(ScheduleSlotModel).filter(
            and_(
                ScheduleSlotModel.cohort_id == student.cohort_id,
                ScheduleSlotModel.date >= start_date,
                ScheduleSlotModel.date <= end_date
            )
        ).order_by(ScheduleSlotModel.date, ScheduleSlotModel.start_time).all()