"""
Repository pour les Programmes/Parcours.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import ProgramModel, ProgramLevelEnum


class ProgramRepository(BaseRepository[ProgramModel]):
    """Repository pour les opérations sur les programmes."""
    
    def __init__(self, session: Session):
        super().__init__(ProgramModel, session)
    
    def get_by_code(self, code: str) -> Optional[ProgramModel]:
        """
        Récupère un programme par son code.
        
        Args:
            code: Code du programme
            
        Returns:
            Programme ou None
        """
        return self.first_by(code=code)
    
    def get_by_ufr(self, ufr_id: int) -> List[ProgramModel]:
        """
        Récupère tous les programmes d'une UFR.
        
        Args:
            ufr_id: ID de l'UFR
            
        Returns:
            Liste des programmes
        """
        return self.filter_by(ufr_id=ufr_id)
    
    def get_by_level(self, level: ProgramLevelEnum) -> List[ProgramModel]:
        """
        Récupère les programmes par niveau.
        
        Args:
            level: Niveau (enum ProgramLevelEnum)
            
        Returns:
            Liste des programmes
        """
        return self.filter_by(level=level)
    
    def search_by_name(self, name: str) -> List[ProgramModel]:
        """
        Recherche des programmes par nom (partiel).
        
        Args:
            name: Nom ou partie du nom
            
        Returns:
            Liste des programmes correspondants
        """
        return self.session.query(self.model).filter(
            self.model.name.like(f"%{name}%")
        ).all()
    
    def get_with_cohorts(self, program_id: int) -> Optional[ProgramModel]:
        """
        Récupère un programme avec toutes ses cohortes.
        
        Args:
            program_id: ID du programme
            
        Returns:
            Programme avec cohortes chargées ou None
        """
        from sqlalchemy.orm import joinedload
        
        return self.session.query(self.model).options(
            joinedload(self.model.cohorts)
        ).filter(self.model.id == program_id).first()
    
    def get_licence_programs(self) -> List[ProgramModel]:
        """
        Récupère tous les programmes de niveau Licence.
        
        Returns:
            Liste des programmes Licence
        """
        return self.session.query(self.model).filter(
            self.model.level.in_([
                ProgramLevelEnum.LICENCE_1,
                ProgramLevelEnum.LICENCE_2,
                ProgramLevelEnum.LICENCE_3
            ])
        ).all()
    
    def get_master_programs(self) -> List[ProgramModel]:
        """
        Récupère tous les programmes de niveau Master.
        
        Returns:
            Liste des programmes Master
        """
        return self.session.query(self.model).filter(
            self.model.level.in_([
                ProgramLevelEnum.MASTER_1,
                ProgramLevelEnum.MASTER_2
            ])
        ).all()