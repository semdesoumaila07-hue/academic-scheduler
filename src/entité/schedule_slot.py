"""
Entité ScheduleSlot (Créneau Horaire).
"""
from typing import Optional
from datetime import datetime, date, time


class ScheduleSlot:
    """
    Représente un créneau horaire dans l'emploi du temps.
    
    Attributes:
        id: Identifiant unique
        date: Date du créneau
        start_time: Heure de début
        end_time: Heure de fin
        room: Salle
        activity_id: ID de l'activité académique
        teacher_id: ID de l'enseignant
        cohort_id: ID de la cohorte
        delay_value: Valeur du retard au moment de la planification
        blocked_by_leave: Indique si le créneau est bloqué par un congé
        notes: Notes/remarques
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        date: date,
        start_time: time,
        end_time: time,
        activity_id: int,
        teacher_id: int,
        cohort_id: int,
        room: Optional[str] = None,
        delay_value: float = 0.0,
        blocked_by_leave: bool = False,
        notes: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un créneau horaire.
        
        Args:
            date: Date du créneau
            start_time: Heure de début
            end_time: Heure de fin
            activity_id: ID de l'activité
            teacher_id: ID de l'enseignant
            cohort_id: ID de la cohorte
            room: Salle
            delay_value: Retard au moment de la planification
            blocked_by_leave: Bloqué par congé
            notes: Notes
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.activity_id = activity_id
        self.teacher_id = teacher_id
        self.cohort_id = cohort_id
        self.delay_value = delay_value
        self.blocked_by_leave = blocked_by_leave
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def get_duration_hours(self) -> float:
        """
        Calcule la durée du créneau en heures.
        
        Returns:
            Durée en heures
        """
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        duration_minutes = end_minutes - start_minutes
        return duration_minutes / 60.0
    
    def cancel(self, reason: str = None) -> None:
        """
        Annule le créneau.
        
        Args:
            reason: Raison de l'annulation
        """
        self.blocked_by_leave = True
        if reason:
            self.notes = f"Annulé: {reason}"
    
    def is_available(self) -> bool:
        """
        Vérifie si le créneau est disponible.
        
        Returns:
            True si disponible, False sinon
        """
        return not self.blocked_by_leave
    
    def overlaps_with(self, other: 'ScheduleSlot') -> bool:
        """
        Vérifie si ce créneau chevauche un autre créneau.
        
        Args:
            other: Autre créneau
            
        Returns:
            True si chevauchement, False sinon
        """
        # Même date
        if self.date != other.date:
            return False
        
        # Vérifier le chevauchement temporel
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)
    
    def conflicts_with(self, other: 'ScheduleSlot') -> bool:
        """
        Vérifie s'il y a un conflit avec un autre créneau.
        Un conflit existe si :
        - Même enseignant, chevauchement temporel
        - Même cohorte, chevauchement temporel
        - Même salle, chevauchement temporel
        
        Args:
            other: Autre créneau
            
        Returns:
            True si conflit, False sinon
        """
        if not self.overlaps_with(other):
            return False
        
        # Conflit enseignant
        if self.teacher_id == other.teacher_id:
            return True
        
        # Conflit cohorte
        if self.cohort_id == other.cohort_id:
            return True
        
        # Conflit salle
        if self.room and other.room and self.room == other.room:
            return True
        
        return False
    
    def to_dict(self) -> dict:
        """
        Convertit le créneau en dictionnaire.
        
        Returns:
            Dictionnaire représentant le créneau
        """
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'room': self.room,
            'activity_id': self.activity_id,
            'teacher_id': self.teacher_id,
            'cohort_id': self.cohort_id,
            'delay_value': self.delay_value,
            'blocked_by_leave': self.blocked_by_leave,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduleSlot':
        """
        Crée un créneau depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de ScheduleSlot
        """
        return cls(
            id=data.get('id'),
            date=date.fromisoformat(data['date']) if data.get('date') else None,
            start_time=time.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=time.fromisoformat(data['end_time']) if data.get('end_time') else None,
            room=data.get('room'),
            activity_id=data['activity_id'],
            teacher_id=data['teacher_id'],
            cohort_id=data['cohort_id'],
            delay_value=data.get('delay_value', 0.0),
            blocked_by_leave=data.get('blocked_by_leave', False),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du créneau."""
        return f"{self.date} {self.start_time}-{self.end_time} (Salle: {self.room or 'N/A'})"
    
    def __repr__(self) -> str:
        """Représentation technique du créneau."""
        return f"ScheduleSlot(id={self.id}, date={self.date}, time={self.start_time}-{self.end_time})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données du créneau.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.date:
            return False, "La date est requise"
        
        if not self.start_time:
            return False, "L'heure de début est requise"
        
        if not self.end_time:
            return False, "L'heure de fin est requise"
        
        if self.start_time >= self.end_time:
            return False, "L'heure de fin doit être après l'heure de début"
        
        # Vérifier que la durée est raisonnable (max 8 heures)
        duration = self.get_duration_hours()
        if duration > 8:
            return False, "La durée ne peut pas dépasser 8 heures"
        
        if not self.activity_id or self.activity_id <= 0:
            return False, "L'ID de l'activité est requis"
        
        if not self.teacher_id or self.teacher_id <= 0:
            return False, "L'ID de l'enseignant est requis"
        
        if not self.cohort_id or self.cohort_id <= 0:
            return False, "L'ID de la cohorte est requis"
        
        return True, None