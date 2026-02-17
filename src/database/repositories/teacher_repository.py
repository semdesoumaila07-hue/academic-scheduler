"""
Repository pour les Enseignants.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import TeacherModel, TeacherStatusEnum


class TeacherRepository(BaseRepository[TeacherModel]):
    """Repository pour les opérations sur les enseignants."""

    def __init__(self, session: Session):
        super().__init__(TeacherModel, session)

    def get_by_email(self, email: str) -> Optional[TeacherModel]:
        """Récupère un enseignant par son email."""
        return self.first_by(email=email)

    def get_by_status(self, status: TeacherStatusEnum) -> List[TeacherModel]:
        """Récupère les enseignants par statut."""
        return self.filter_by(status=status)

    def search_by_name(self, name: str) -> List[TeacherModel]:
        """Recherche des enseignants par nom."""
        return self.session.query(self.model).filter(
            self.model.full_name.like(f"%{name}%")
        ).all()
