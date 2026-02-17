"""
Repository pour les signalements de conflits/contraintes par les enseignants.
"""
from typing import List
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import TeacherConstraintReportModel, ConstraintReportStatusEnum


class ConstraintReportRepository(BaseRepository[TeacherConstraintReportModel]):
    """Repository pour les signalements enseignants."""

    def __init__(self, session: Session):
        super().__init__(TeacherConstraintReportModel, session)

    def get_by_teacher(self, teacher_id: int) -> List[TeacherConstraintReportModel]:
        """Récupère tous les signalements d'un enseignant."""
        return self.session.query(self.model).filter(
            self.model.teacher_id == teacher_id
        ).order_by(self.model.reported_at.desc()).all()

    def get_pending(self) -> List[TeacherConstraintReportModel]:
        """Récupère tous les signalements en attente (pour l'admin)."""
        return self.session.query(self.model).filter(
            self.model.status == ConstraintReportStatusEnum.PENDING
        ).order_by(self.model.reported_at.desc()).all()
