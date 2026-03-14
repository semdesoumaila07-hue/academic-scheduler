"""
Entité Université.
"""
from typing import Optional, List
from datetime import datetime


class University:
    """
    Représente une université.
    
    Attributes:
        id: Identifiant unique
        name: Nom de l'université
        code: Code court de l'université
        address: Adresse complète
        city: Ville
        country: Pays
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        code: str,
        address: str,
        city: str,
        country: str = "Burkina Faso",
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une université.
        
        Args:
            name: Nom de l'université
            code: Code court
            address: Adresse
            city: Ville
            country: Pays (défaut: Burkina Faso)
            id: Identifiant (None pour nouvelle université)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.code = code
        self.address = address
        self.city = city
        self.country = country
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convertit l'université en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'université
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'University':
        """
        Crée une université depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de University
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            code=data['code'],
            address=data['address'],
            city=data['city'],
            country=data.get('country', 'Burkina Faso'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'université."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self) -> str:
        """Représentation technique de l'université."""
        return f"University(id={self.id}, name='{self.name}', code='{self.code}')"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de l'université.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de l'université est requis"
        
        if not self.code or len(self.code.strip()) == 0:
            return False, "Le code de l'université est requis"
        
        if len(self.code) > 10:
            return False, "Le code ne peut pas dépasser 10 caractères"
        
        if not self.address or len(self.address.strip()) == 0:
            return False, "L'adresse est requise"
        
        if not self.city or len(self.city.strip()) == 0:
            return False, "La ville est requise"
        
        return True, None