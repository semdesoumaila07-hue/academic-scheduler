"""
Repository pour les UFR (Unités de Formation et de Recherche).
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import UFRModel, ProgramModel


class UFRRepository(BaseRepository[UFRModel]):
    """Repository pour les opérations sur les UFR."""

    def __init__(self, session: Session):
        super().__init__(UFRModel, session)

    def get_by_code(self, code: str) -> Optional[UFRModel]:
        """Récupère une UFR par son code."""
        return self.first_by(code=code)

    def get_by_university(self, university_id: int) -> List[UFRModel]:
        """Récupère toutes les UFR d'une université."""
        return self.filter_by(university_id=university_id)

    def search_by_name(self, name: str) -> List[UFRModel]:
        """Recherche des UFR par nom (partiel)."""
        return self.session.query(self.model).filter(
            self.model.name.like(f"%{name}%")
        ).all()

    def get_with_programs(self, ufr_id: int) -> Optional[UFRModel]:
        """Récupère une UFR avec tous ses programmes."""
        from sqlalchemy.orm import joinedload
        return self.session.query(self.model).options(
            joinedload(self.model.programs)
        ).filter(self.model.id == ufr_id).first()

    def get_by_director(self, director: str) -> List[UFRModel]:
        """Récupère les UFR par directeur."""
        return self.session.query(self.model).filter(
            self.model.director.like(f"%{director}%")
        ).all()

    def delete(self, id: int) -> bool:
        """
        Supprime une UFR.
        ⚠️  Lève ValueError si des programmes sont encore rattachés à cette UFR.
        """
        # Vérifier s'il existe des programmes liés
        programmes_count = (
            self.session.query(ProgramModel)
            .filter(ProgramModel.ufr_id == id)
            .count()
        )
        if programmes_count > 0:
            raise ValueError(
                f"Impossible de supprimer l'UFR {id} : "
                f"{programmes_count} programme(s) y sont rattaché(s). "
                f"Supprimez d'abord les programmes."
            )

        return super().delete(id)