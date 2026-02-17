"""
Repository pour les UFR (Unités de Formation et de Recherche).
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import UFRModel


class UFRRepository(BaseRepository[UFRModel]):
    """Repository pour les opérations sur les UFR."""
    
    def __init__(self, session: Session):
        super().__init__(UFRModel, session)
    
    def get_by_code(self, code: str) -> Optional[UFRModel]:
        """
        Récupère une UFR par son code.
        
        Args:
            code: Code de l'UFR
            
        Returns:
            UFR ou None
        """
        return self.first_by(code=code)
    
    def get_by_university(self, university_id: int) -> List[UFRModel]:
        """
        Récupère toutes les UFR d'une université.
        
        Args:
            university_id: ID de l'université
            
        Returns:
            Liste des UFR
        """
        return self.filter_by(university_id=university_id)
    
    def search_by_name(self, name: str) -> List[UFRModel]:
        """
        Recherche des UFR par nom (partiel).
        
        Args:
            name: Nom ou partie du nom
            
        Returns:
            Liste des UFR correspondantes
        """
        return self.session.query(self.model).filter(
            self.model.name.like(f"%{name}%")
        ).all()
    
    def get_with_programs(self, ufr_id: int) -> Optional[UFRModel]:
        """
        Récupère une UFR avec tous ses programmes.
        
        Args:
            ufr_id: ID de l'UFR
            
        Returns:
            UFR avec programmes chargés ou None
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(self.model).options(
            joinedload(self.model.programs)
        ).filter(self.model.id == ufr_id).first()
    
    def get_by_director(self, director: str) -> List[UFRModel]:
        """
        Récupère les UFR par directeur.
        
        Args:
            director: Nom du directeur
            
        Returns:
            Liste des UFR
        """
        return self.session.query(self.model).filter(
            self.model.director.like(f"%{director}%")
        ).all()