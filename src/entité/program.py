"""
Entité Program (Parcours/Filière).
"""
from typing import Optional
from datetime import datetime
from ..utils.constants import ProgramLevel


class Program:
    """
    Représente un programme/parcours académique.
    
    Attributes:
        id: Identifiant unique
        name: Nom du programme
        code: Code court du programme
        level: Niveau (Licence 1, Master 2, etc.)
        duration_years: Durée en années
        ufr_id: ID de l'UFR parente
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        code: str,
        level: ProgramLevel,
        duration_years: int,
        ufr_id: int,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un programme.
        
        Args:
            name: Nom du programme
            code: Code court
            level: Niveau du programme
            duration_years: Durée en années
            ufr_id: ID de l'UFR
            id: Identifiant (None pour nouveau programme)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.code = code
        self.level = level
        self.duration_years = duration_years
        self.ufr_id = ufr_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convertit le programme en dictionnaire.
        
        Returns:
            Dictionnaire représentant le programme
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'level': self.level.value if isinstance(self.level, ProgramLevel) else self.level,
            'duration_years': self.duration_years,
            'ufr_id': self.ufr_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Program':
        """
        Crée un programme depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de Program
        """
        # Convertir le niveau en enum si c'est une chaîne
        level = data['level']
        if isinstance(level, str):
            level = ProgramLevel(level)
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            code=data['code'],
            level=level,
            duration_years=data['duration_years'],
            ufr_id=data['ufr_id'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du programme."""
        return f"{self.name} - {self.level.value} ({self.code})"
    
    def __repr__(self) -> str:
        """Représentation technique du programme."""
        return f"Program(id={self.id}, name='{self.name}', level={self.level})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données du programme.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom du programme est requis"
        
        if not self.code or len(self.code.strip()) == 0:
            return False, "Le code du programme est requis"
        
        if len(self.code) > 10:
            return False, "Le code ne peut pas dépasser 10 caractères"
        
        if not isinstance(self.level, ProgramLevel):
            return False, "Le niveau doit être un ProgramLevel valide"
        
        if not self.duration_years or self.duration_years <= 0:
            return False, "La durée doit être supérieure à 0"
        
        if self.duration_years > 10:
            return False, "La durée ne peut pas dépasser 10 ans"
        
        if not self.ufr_id or self.ufr_id <= 0:
            return False, "L'ID de l'UFR est requis"
        
        return True, None