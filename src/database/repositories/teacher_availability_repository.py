"""
Repository pour les créneaux de disponibilité des enseignants.
"""
from typing import List
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import TeacherAvailabilityModel


class TeacherAvailabilityRepository(BaseRepository[TeacherAvailabilityModel]):
    """Repository pour les disponibilités hebdomadaires des enseignants."""

    def __init__(self, session: Session):
        super().__init__(TeacherAvailabilityModel, session)

    def get_by_teacher(self, teacher_id: int) -> List[TeacherAvailabilityModel]:
        """Récupère tous les créneaux de disponibilité d'un enseignant."""
        return self.session.query(self.model).filter(
            self.model.teacher_id == teacher_id
        ).order_by(self.model.day_of_week, self.model.start_time).all()

    def delete_by_teacher(self, teacher_id: int) -> int:
        """Supprime toutes les disponibilités d'un enseignant. Retourne le nombre supprimé."""
        count = self.session.query(self.model).filter(
            self.model.teacher_id == teacher_id
        ).delete()
        self.session.commit()
        return count
