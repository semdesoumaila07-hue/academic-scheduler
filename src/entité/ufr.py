"""
Entité UFR (Unité de Formation et de Recherche).
"""
from typing import Optional
from datetime import datetime


class UFR:
    """
    Représente une UFR (Unité de Formation et de Recherche).
    
    Attributes:
        id: Identifiant unique
        name: Nom de l'UFR
        code: Code court de l'UFR
        director: Nom du directeur
        university_id: ID de l'université parente
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        code: str,
        university_id: int,
        director: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une UFR.
        
        Args:
            name: Nom de l'UFR
            code: Code court
            university_id: ID de l'université
            director: Nom du directeur
            id: Identifiant (None pour nouvelle UFR)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.code = code
        self.director = director
        self.university_id = university_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convertit l'UFR en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'UFR
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'director': self.director,
            'university_id': self.university_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UFR':
        """
        Crée une UFR depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de UFR
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            code=data['code'],
            university_id=data['university_id'],
            director=data.get('director'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'UFR."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self) -> str:
        """Représentation technique de l'UFR."""
        return f"UFR(id={self.id}, name='{self.name}', code='{self.code}')"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de l'UFR.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de l'UFR est requis"
        
        if not self.code or len(self.code.strip()) == 0:
            return False, "Le code de l'UFR est requis"
        
        if len(self.code) > 10:
            return False, "Le code ne peut pas dépasser 10 caractères"
        
        if not self.university_id or self.university_id <= 0:
            return False, "L'ID de l'université est requis"
        
        return True, None