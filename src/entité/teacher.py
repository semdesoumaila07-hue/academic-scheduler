"""
Entité Teacher (Enseignant).
"""
from typing import Optional, List
from datetime import datetime
from ..utils.constants import TeacherStatus


class Teacher:
    """
    Représente un enseignant.
    
    Attributes:
        id: Identifiant unique
        full_name: Nom complet
        email: Adresse email
        phone: Numéro de téléphone
        speciality: Spécialité/domaine
        max_hours_per_week: Nombre max d'heures par semaine
        max_hours_per_day: Nombre max d'heures par jour
        status: Statut (permanent, vacataire, etc.)
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        full_name: str,
        email: str,
        speciality: str,
        status: TeacherStatus,
        phone: Optional[str] = None,
        max_hours_per_week: int = 40,
        max_hours_per_day: int = 8,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un enseignant.
        
        Args:
            full_name: Nom complet
            email: Adresse email
            speciality: Spécialité
            status: Statut de l'enseignant
            phone: Téléphone
            max_hours_per_week: Heures max par semaine
            max_hours_per_day: Heures max par jour
            id: Identifiant (None pour nouvel enseignant)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.speciality = speciality
        self.max_hours_per_week = max_hours_per_week
        self.max_hours_per_day = max_hours_per_day
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def request_leave(self, start_date, end_date, leave_type, reason):
        """
        Soumet une demande de congé.
        À implémenter avec LeaveRequest.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            leave_type: Type de congé
            reason: Raison
            
        Returns:
            LeaveRequest créé
        """
        # TODO: Implémenter avec LeaveRequest
        pass
    
    def get_disponibilities(self, start_date, end_date):
        """
        Récupère les disponibilités de l'enseignant.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des disponibilités
        """
        # TODO: Implémenter avec la base de données
        pass
    
    def to_dict(self) -> dict:
        """
        Convertit l'enseignant en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'enseignant
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'speciality': self.speciality,
            'max_hours_per_week': self.max_hours_per_week,
            'max_hours_per_day': self.max_hours_per_day,
            'status': self.status.value if isinstance(self.status, TeacherStatus) else self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Teacher':
        """
        Crée un enseignant depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de Teacher
        """
        # Convertir le statut en enum si c'est une chaîne
        status = data['status']
        if isinstance(status, str):
            status = TeacherStatus(status)
        
        return cls(
            id=data.get('id'),
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone'),
            speciality=data['speciality'],
            max_hours_per_week=data.get('max_hours_per_week', 40),
            max_hours_per_day=data.get('max_hours_per_day', 8),
            status=status,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'enseignant."""
        return f"{self.full_name} ({self.speciality})"
    
    def __repr__(self) -> str:
        """Représentation technique de l'enseignant."""
        return f"Teacher(id={self.id}, name='{self.full_name}', status={self.status})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de l'enseignant.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.full_name or len(self.full_name.strip()) == 0:
            return False, "Le nom complet est requis"
        
        if not self.email or len(self.email.strip()) == 0:
            return False, "L'email est requis"
        
        # Validation basique de l'email
        if '@' not in self.email:
            return False, "L'email n'est pas valide"
        
        if not self.speciality or len(self.speciality.strip()) == 0:
            return False, "La spécialité est requise"
        
        if not isinstance(self.status, TeacherStatus):
            return False, "Le statut doit être un TeacherStatus valide"
        
        if self.max_hours_per_week <= 0 or self.max_hours_per_week > 80:
            return False, "Les heures max par semaine doivent être entre 1 et 80"
        
        if self.max_hours_per_day <= 0 or self.max_hours_per_day > 24:
            return False, "Les heures max par jour doivent être entre 1 et 24"
        
        return True, None