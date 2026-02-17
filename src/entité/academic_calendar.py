"""
Entité AcademicCalendar (Calendrier Académique).
"""
from typing import Optional, List
from datetime import datetime, date, timedelta
from ..utils.helpers import is_workday, count_workdays


class AcademicCalendar:
    """
    Représente un calendrier académique.
    
    Attributes:
        id: Identifiant unique
        name: Nom du calendrier
        academic_year: Année académique (ex: "2025-2026")
        start_date: Date de début de l'année académique
        end_date: Date de fin de l'année académique
        hours_per_day: Nombre d'heures de cours par jour
        semester_count: Nombre de semestres
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    def __init__(
        self,
        name: str,
        academic_year: str,
        start_date: date,
        end_date: date,
        hours_per_day: int = 8,
        semester_count: int = 2,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un calendrier académique.
        
        Args:
            name: Nom du calendrier
            academic_year: Année académique
            start_date: Date de début
            end_date: Date de fin
            hours_per_day: Heures par jour
            semester_count: Nombre de semestres
            id: Identifiant
            created_at: Date de création
            updated_at: Date de modification
        """
        self.id = id
        self.name = name
        self.academic_year = academic_year
        self.start_date = start_date
        self.end_date = end_date
        self.hours_per_day = hours_per_day
        self.semester_count = semester_count
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def is_workday(self, check_date: date, holidays: List[date] = None) -> bool:
        """
        Vérifie si une date est un jour ouvrable.
        
        Args:
            check_date: Date à vérifier
            holidays: Liste des jours fériés
            
        Returns:
            True si jour ouvrable, False sinon
        """
        # Vérifier si la date est dans l'année académique
        if check_date < self.start_date or check_date > self.end_date:
            return False
        
        return is_workday(check_date, holidays)
    
    def calculate_effective_days(self, holidays: List[date] = None, 
                                vacation_periods: List[tuple] = None) -> int:
        """
        Calcule le nombre de jours effectifs (D_effectif) dans l'année académique.
        
        D_effectif = jours ouvrables - jours fériés - périodes de vacances
        
        Args:
            holidays: Liste des dates de jours fériés
            vacation_periods: Liste de tuples (start_date, end_date) des vacances
            
        Returns:
            Nombre de jours effectifs
        """
        # Compter tous les jours ouvrables
        total_workdays = count_workdays(self.start_date, self.end_date, holidays)
        
        # Soustraire les jours de vacances
        if vacation_periods:
            vacation_days = 0
            for start, end in vacation_periods:
                vacation_days += count_workdays(start, end, holidays)
            total_workdays -= vacation_days
        
        return total_workdays
    
    def get_semester_dates(self, semester: int) -> tuple[date, date]:
        """
        Retourne les dates de début et fin d'un semestre.
        
        Args:
            semester: Numéro du semestre (1 ou 2)
            
        Returns:
            Tuple (date_début, date_fin)
        """
        if semester not in [1, 2]:
            raise ValueError("Le semestre doit être 1 ou 2")
        
        total_days = (self.end_date - self.start_date).days
        semester_duration = total_days // self.semester_count
        
        if semester == 1:
            start = self.start_date
            end = start + timedelta(days=semester_duration)
        else:
            start = self.start_date + timedelta(days=semester_duration + 1)
            end = self.end_date
        
        return start, end
    
    def is_in_academic_year(self, check_date: date) -> bool:
        """
        Vérifie si une date est dans l'année académique.
        
        Args:
            check_date: Date à vérifier
            
        Returns:
            True si dans l'année académique, False sinon
        """
        return self.start_date <= check_date <= self.end_date
    
    def get_week_number(self, check_date: date) -> int:
        """
        Retourne le numéro de la semaine académique.
        
        Args:
            check_date: Date
            
        Returns:
            Numéro de semaine (1-based)
        """
        if not self.is_in_academic_year(check_date):
            return 0
        
        days_since_start = (check_date - self.start_date).days
        return (days_since_start // 7) + 1
    
    def get_total_hours(self) -> int:
        """
        Calcule le nombre total d'heures disponibles dans l'année académique.
        
        Returns:
            Nombre total d'heures
        """
        effective_days = self.calculate_effective_days()
        return effective_days * self.hours_per_day
    
    def validate_leave_request(self, start_date: date, end_date: date) -> tuple[bool, Optional[str]]:
        """
        Valide une demande de congé par rapport au calendrier.
        
        Args:
            start_date: Date de début du congé
            end_date: Date de fin du congé
            
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.is_in_academic_year(start_date):
            return False, "La date de début est en dehors de l'année académique"
        
        if not self.is_in_academic_year(end_date):
            return False, "La date de fin est en dehors de l'année académique"
        
        return True, None
    
    def to_dict(self) -> dict:
        """
        Convertit le calendrier en dictionnaire.
        
        Returns:
            Dictionnaire représentant le calendrier
        """
        return {
            'id': self.id,
            'name': self.name,
            'academic_year': self.academic_year,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'hours_per_day': self.hours_per_day,
            'semester_count': self.semester_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AcademicCalendar':
        """
        Crée un calendrier depuis un dictionnaire.
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance de AcademicCalendar
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            academic_year=data['academic_year'],
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            hours_per_day=data.get('hours_per_day', 8),
            semester_count=data.get('semester_count', 2),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du calendrier."""
        return f"{self.name} ({self.academic_year})"
    
    def __repr__(self) -> str:
        """Représentation technique du calendrier."""
        return f"AcademicCalendar(id={self.id}, year='{self.academic_year}')"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Valide les données du calendrier.
        
        Returns:
            Tuple (valide, message d'erreur)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom du calendrier est requis"
        
        if not self.academic_year:
            return False, "L'année académique est requise"
        
        if not self.start_date:
            return False, "La date de début est requise"
        
        if not self.end_date:
            return False, "La date de fin est requise"
        
        if self.start_date >= self.end_date:
            return False, "La date de fin doit être après la date de début"
        
        # Vérifier que la durée est raisonnable (entre 6 mois et 2 ans)
        duration_days = (self.end_date - self.start_date).days
        if duration_days < 180:
            return False, "L'année académique doit durer au moins 6 mois"
        if duration_days > 730:
            return False, "L'année académique ne peut pas dépasser 2 ans"
        
        if self.hours_per_day <= 0 or self.hours_per_day > 12:
            return False, "Les heures par jour doivent être entre 1 et 12"
        
        if self.semester_count <= 0 or self.semester_count > 4:
            return False, "Le nombre de semestres doit être entre 1 et 4"
        
        return True, None