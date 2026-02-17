"""
Entité Student (Étudiant).
"""
from typing import Optional
from datetime import datetime, date


class Student:
    """
    Représente un étudiant.
    
    Attributes:
        id: Identifiant unique
        full_name: Nom complet
        student_id: Numéro d'étudiant/matricule
        email: Adresse email
        phone: Numéro de téléphone
        birth_date: Date de naissance
        cohort_id: ID de la cohorte/classe
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        full_name: str,
        student_id: str,
        email: str,
        cohort_id: int,
        phone: Optional[str] = None,
        birth_date: Optional[date] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un étudiant.
        
        Args:
            full_name: Nom complet
            student_id: Numéro d'étudiant
            email: Adresse email
            cohort_id: ID de la cohorte
            phone: Téléphone
            birth_date: Date de naissance
            id: Identifiant (None pour nouvel étudiant)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.full_name = full_name
        self.student_id = student_id
        self.email = email
        self.phone = phone
        self.birth_date = birth_date
        self.cohort_id = cohort_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def get_schedule(self, start_date, end_date):
        """
        Récupère l'emploi du temps de l'étudiant.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des créneaux
        """
        # TODO: Implémenter avec la base de données
        pass
    
    def view_academic_delay(self):
        """
        Visualise le retard académique de l'étudiant.
        
        Returns:
            Retard académique en heures
        """
        # TODO: Implémenter avec les activités de la cohorte
        pass
    
    def to_dict(self) -> dict:
        """
        Convertit l'étudiant en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'étudiant
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'student_id': self.student_id,
            'email': self.email,
            'phone': self.phone,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'cohort_id': self.cohort_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """
        Crée un étudiant depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de Student
        """
        return cls(
            id=data.get('id'),
            full_name=data['full_name'],
            student_id=data['student_id'],
            email=data['email'],
            phone=data.get('phone'),
            birth_date=date.fromisoformat(data['birth_date']) if data.get('birth_date') else None,
            cohort_id=data['cohort_id'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'étudiant."""
        return f"{self.full_name} ({self.student_id})"
    
    def __repr__(self) -> str:
        """Représentation technique de l'étudiant."""
        return f"Student(id={self.id}, name='{self.full_name}', student_id='{self.student_id}')"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de l'étudiant.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.full_name or len(self.full_name.strip()) == 0:
            return False, "Le nom complet est requis"
        
        if not self.student_id or len(self.student_id.strip()) == 0:
            return False, "Le numéro d'étudiant est requis"
        
        if not self.email or len(self.email.strip()) == 0:
            return False, "L'email est requis"
        
        # Validation basique de l'email
        if '@' not in self.email:
            return False, "L'email n'est pas valide"
        
        if not self.cohort_id or self.cohort_id <= 0:
            return False, "L'ID de la cohorte est requis"
        
        # Validation de la date de naissance si fournie
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if age < 15 or age > 100:
                return False, "La date de naissance n'est pas valide"
        
        return True, None