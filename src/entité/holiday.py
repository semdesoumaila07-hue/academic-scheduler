"""
Entité Holiday (Jour Férié).
"""
from typing import Optional
from datetime import datetime, date


class Holiday:
    """
    Représente un jour férié.
    
    Attributes:
        id: Identifiant unique
        name: Nom du jour férié
        date: Date du jour férié
        is_recurring: Indique si le jour férié se répète chaque année
        calendar_id: ID du calendrier académique
        description: Description optionnelle
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        date: date,
        calendar_id: int,
        is_recurring: bool = False,
        description: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un jour férié.
        
        Args:
            name: Nom du jour férié
            date: Date
            calendar_id: ID du calendrier académique
            is_recurring: Récurrent chaque année
            description: Description
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.date = date
        self.is_recurring = is_recurring
        self.calendar_id = calendar_id
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def is_today(self) -> bool:
        """
        Vérifie si le jour férié est aujourd'hui.
        
        Returns:
            True si aujourd'hui, False sinon
        """
        today = date.today()
        
        if self.is_recurring:
            # Comparer seulement le jour et le mois
            return (self.date.day == today.day and 
                   self.date.month == today.month)
        else:
            # Comparer la date complète
            return self.date == today
    
    def occurs_on(self, check_date: date) -> bool:
        """
        Vérifie si le jour férié tombe à une date donnée.
        
        Args:
            check_date: Date à vérifier
            
        Returns:
            True si le jour férié tombe à cette date, False sinon
        """
        if self.is_recurring:
            # Comparer seulement le jour et le mois
            return (self.date.day == check_date.day and 
                   self.date.month == check_date.month)
        else:
            # Comparer la date complète
            return self.date == check_date
    
    def get_next_occurrence(self, from_date: date = None) -> date:
        """
        Retourne la prochaine occurrence du jour férié.
        
        Args:
            from_date: Date de référence (aujourd'hui par défaut)
            
        Returns:
            Date de la prochaine occurrence
        """
        if from_date is None:
            from_date = date.today()
        
        if not self.is_recurring:
            # Si non récurrent, retourner la date si elle est future
            if self.date >= from_date:
                return self.date
            return None
        
        # Pour les jours récurrents, trouver la prochaine occurrence
        next_year = from_date.year
        next_occurrence = date(next_year, self.date.month, self.date.day)
        
        if next_occurrence < from_date:
            # Si déjà passé cette année, prendre l'année prochaine
            next_occurrence = date(next_year + 1, self.date.month, self.date.day)
        
        return next_occurrence
    
    def to_dict(self) -> dict:
        """
        Convertit le jour férié en dictionnaire.
        
        Returns:
            Dictionnaire représentant le jour férié
        """
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'is_recurring': self.is_recurring,
            'calendar_id': self.calendar_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Holiday':
        """
        Crée un jour férié depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de Holiday
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            date=date.fromisoformat(data['date']) if data.get('date') else None,
            is_recurring=data.get('is_recurring', False),
            calendar_id=data['calendar_id'],
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du jour férié."""
        recurring_str = " (récurrent)" if self.is_recurring else ""
        return f"{self.name} - {self.date.strftime('%d/%m')}{recurring_str}"
    
    def __repr__(self) -> str:
        """Représentation technique du jour férié."""
        return f"Holiday(id={self.id}, name='{self.name}', date={self.date})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données du jour férié.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom du jour férié est requis"
        
        if not self.date:
            return False, "La date est requise"
        
        if not self.calendar_id or self.calendar_id <= 0:
            return False, "L'ID du calendrier est requis"
        
        return True, None