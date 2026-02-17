"""
Entité Cohort (Classe/Promotion).
"""
from typing import Optional
from datetime import datetime, date


class Cohort:
    """
    Représente une cohorte/classe/promotion d'étudiants.
    
    Attributes:
        id: Identifiant unique
        name: Nom de la cohorte
        academic_year: Année académique (ex: "2025-2026")
        semester: Numéro du semestre
        student_count: Nombre d'étudiants
        program_id: ID du programme
        start_date: Date de début
        end_date: Date de fin
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        academic_year: str,
        semester: int,
        student_count: int,
        program_id: int,
        start_date: date,
        end_date: date,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise une cohorte.
        
        Args:
            name: Nom de la cohorte
            academic_year: Année académique
            semester: Numéro du semestre (1-2)
            student_count: Nombre d'étudiants
            program_id: ID du programme
            start_date: Date de début
            end_date: Date de fin
            id: Identifiant (None pour nouvelle cohorte)
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.academic_year = academic_year
        self.semester = semester
        self.student_count = student_count
        self.program_id = program_id
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def calculate_global_delay(self) -> float:
        """
        Calcule le retard global de la cohorte.
        À implémenter avec les activités académiques.
        
        Returns:
            Retard global en heures
        """
        # TODO: Implémenter avec les activités
        return 0.0
    
    def to_dict(self) -> dict:
        """
        Convertit la cohorte en dictionnaire.
        
        Returns:
            Dictionnaire représentant la cohorte
        """
        return {
            'id': self.id,
            'name': self.name,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'student_count': self.student_count,
            'program_id': self.program_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cohort':
        """
        Crée une cohorte depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de Cohort
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            academic_year=data['academic_year'],
            semester=data['semester'],
            student_count=data['student_count'],
            program_id=data['program_id'],
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de la cohorte."""
        return f"{self.name} - {self.academic_year} S{self.semester}"
    
    def __repr__(self) -> str:
        """Représentation technique de la cohorte."""
        return f"Cohort(id={self.id}, name='{self.name}', semester={self.semester})"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données de la cohorte.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de la cohorte est requis"
        
        if not self.academic_year:
            return False, "L'année académique est requise"
        
        if self.semester not in [1, 2]:
            return False, "Le semestre doit être 1 ou 2"
        
        if not self.student_count or self.student_count <= 0:
            return False, "Le nombre d'étudiants doit être supérieur à 0"
        
        if not self.program_id or self.program_id <= 0:
            return False, "L'ID du programme est requis"
        
        if not self.start_date:
            return False, "La date de début est requise"
        
        if not self.end_date:
            return False, "La date de fin est requise"
        
        if self.start_date >= self.end_date:
            return False, "La date de fin doit être après la date de début"
        
        return True, None