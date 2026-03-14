"""
Repository pour les Universités.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from .base_repository import BaseRepository
from ..models import UniversityModel


class UniversityRepository(BaseRepository[UniversityModel]):
    """Repository pour les opérations sur les universités."""

    def __init__(self, session: Session):
        super().__init__(UniversityModel, session)

    def get_by_code(self, code: str) -> Optional[UniversityModel]:
        """Récupère une université par son code."""
        return self.first_by(code=code)

    def get_with_ufrs(self, university_id: int) -> Optional[UniversityModel]:
        """Récupère une université avec tous ses UFR."""
        return self.session.query(self.model).options(
            joinedload(self.model.ufrs)
        ).filter(self.model.id == university_id).first()

    def search_by_name(self, name: str) -> List[UniversityModel]:
        """Recherche des universités par nom."""
        return self.session.query(self.model).filter(
            self.model.name.like(f"%{name}%")
        ).all()
