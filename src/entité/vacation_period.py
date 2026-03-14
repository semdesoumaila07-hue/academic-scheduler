"""
Entité VacationPeriod (Période de Vacances).
"""
from typing import Optional
from datetime import datetime, date
from ..utils.constants import VacationType


class VacationPeriod:
    """
    Représente une période de vacances.
    
    Attributes:
        id: Identifiant unique
        name: Nom de la période de vacances
        start_date: Date de début
        end_date: Date de fin
        type: Type de vacances
        calendar_id: ID du calendrier académique
        description: Description optionnelle
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        start_date: date,
        end_date: date,
        type: VacationType,
        calendar_id: int,
        description: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une période de vacances.
        
        Args:
            name: Nom de la période
            start_date: Date de début
            end_date: Date de fin
            type: Type de vacances
            calendar_id: ID du calendrier académique
            description: Description
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.type = type
        self.calendar_id = calendar_id
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def contains_date(self, check_date: date) -> bool:
        """
        Vérifie si une date est dans la période de vacances.
        
        Args:
            check_date: Date à vérifier
            
        Returns:
            True si dans la période, False sinon
        """
        return self.start_date <= check_date <= self.end_date
    
    def get_duration_days(self) -> int:
        """
        Calcule la durée de la période en jours.
        
        Returns:
            Nombre de jours
        """
        return (self.end_date - self.start_date).days + 1
    
    def is_active(self, check_date: date = None) -> bool:
        """
        Vérifie si la période de vacances est active.
        
        Args:
            check_date: Date à vérifier (aujourd'hui par défaut)
            
        Returns:
            True si active, False sinon
        """
        if check_date is None:
            check_date = date.today()
        
        return self.contains_date(check_date)
    
    def overlaps_with(self, other: 'VacationPeriod') -> bool:
        """
        Vérifie si cette période chevauche une autre période.
        
        Args:
            other: Autre période de vacances
            
        Returns:
            True si chevauchement, False sinon
        """
        return (self.start_date <= other.end_date and 
                self.end_date >= other.start_date)
    
    def is_before(self, check_date: date) -> bool:
        """
        Vérifie si la période est avant une date donnée.
        
        Args:
            check_date: Date de référence
            
        Returns:
            True si avant, False sinon
        """
        return self.end_date < check_date
    
    def is_after(self, check_date: date) -> bool:
        """
        Vérifie si la période est après une date donnée.
        
        Args:
            check_date: Date de référence
            
        Returns:
            True si après, False sinon
        """
        return self.start_date > check_date
    
    def get_dates_list(self) -> list[date]:
        """
        Retourne la liste de toutes les dates de la période.
        
        Returns:
            Liste des dates
        """
        dates = []
        current = self.start_date
        
        while current <= self.end_date:
            dates.append(current)
            current = date.fromordinal(current.toordinal() + 1)
        
        return dates
    
    def to_dict(self) -> dict:
        """
        Convertit la période en dictionnaire.
        
        Returns:
            Dictionnaire représentant la période
        """
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'type': self.type.value if isinstance(self.type, VacationType) else self.type,
            'calendar_id': self.calendar_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VacationPeriod':
        """
        Crée une période depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de VacationPeriod
        """
        # Convertir le type en enum
        vacation_type = data['type']
        if isinstance(vacation_type, str):
            vacation_type = VacationType(vacation_type)
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            type=vacation_type,
            calendar_id=data['calendar_id'],
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de la période."""
        duration = self.get_duration_days()
        return f"{self.name} ({self.start_date} - {self.end_date}) - {duration} jours"
    
    def __repr__(self) -> str:
        """Représentation technique de la période."""
        return f"VacationPeriod(id={self.id}, name='{self.name}', type={self.type})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de la période.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de la période est requis"
        
        if not self.start_date:
            return False, "La date de début est requise"
        
        if not self.end_date:
            return False, "La date de fin est requise"
        
        if self.start_date > self.end_date:
            return False, "La date de fin doit être après la date de début"
        
        if not isinstance(self.type, VacationType):
            return False, "Le type doit être un VacationType valide"
        
        if not self.calendar_id or self.calendar_id <= 0:
            return False, "L'ID du calendrier est requis"
        
        # Vérifier que la durée est raisonnable (max 90 jours)
        duration = self.get_duration_days()
        if duration > 90:
            return False, "La période de vacances ne peut pas dépasser 90 jours"
        
        return True, None