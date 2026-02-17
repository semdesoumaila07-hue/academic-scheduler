"""
Service de gestion du calendrier académique.

Gère les jours ouvrables, jours fériés, et périodes de vacances.
"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from ..database.repositories import (
    CalendarRepository, HolidayRepository, VacationPeriodRepository
)
from ..database.models import AcademicCalendarModel, HolidayModel, VacationPeriodModel


class CalendarService:
    """
    Service pour la gestion du calendrier académique.
    
    Attributes:
        session: Session de base de données
    """
    
    def __init__(self, session: Session):
        """
        Initialise le service de calendrier.
        
        Args:
            session: Session de base de données
        """
        self.session = session
        self.calendar_repo = CalendarRepository(session)
        self.holiday_repo = HolidayRepository(session)
        self.vacation_repo = VacationPeriodRepository(session)
    
    def is_workday(self, check_date: date, calendar_id: int = None) -> bool:
        """
        Vérifie si une date est un jour ouvrable.
        
        Un jour ouvrable est un jour qui n'est ni :
        - Un weekend (samedi/dimanche)
        - Un jour férié
        - Dans une période de vacances
        
        Args:
            check_date: Date à vérifier
            calendar_id: ID du calendrier (utilise le calendrier actuel si None)
            
        Returns:
            True si jour ouvrable, False sinon
        """
        # Vérifier le weekend
        if check_date.weekday() >= 5:  # Samedi = 5, Dimanche = 6
            return False
        
        # Récupérer le calendrier
        if calendar_id is None:
            calendar = self.calendar_repo.get_current_calendar(check_date)
            if not calendar:
                return True  # Par défaut, considérer comme ouvrable
            calendar_id = calendar.id
        
        # Vérifier les jours fériés
        if self.holiday_repo.is_holiday(check_date, calendar_id):
            return False
        
        # Vérifier les périodes de vacances
        if self.vacation_repo.is_vacation(check_date, calendar_id):
            return False
        
        return True
    
    def calculate_effective_days(self, start_date: date, end_date: date, 
                                 calendar_id: int = None) -> int:
        """
        Calcule le nombre de jours effectifs (D_effectif) entre deux dates.
        
        D_effectif = jours ouvrables - jours fériés - jours de vacances
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            calendar_id: ID du calendrier
            
        Returns:
            Nombre de jours effectifs
        """
        if start_date > end_date:
            return 0
        
        effective_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_workday(current_date, calendar_id):
                effective_days += 1
            current_date += timedelta(days=1)
        
        return effective_days
    
    def get_workdays_list(self, start_date: date, end_date: date,
                         calendar_id: int = None) -> List[date]:
        """
        Retourne la liste de tous les jours ouvrables entre deux dates.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            calendar_id: ID du calendrier
            
        Returns:
            Liste des dates de jours ouvrables
        """
        workdays = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_workday(current_date, calendar_id):
                workdays.append(current_date)
            current_date += timedelta(days=1)
        
        return workdays
    
    def get_holidays_in_period(self, start_date: date, end_date: date,
                               calendar_id: int = None) -> List[HolidayModel]:
        """
        Récupère tous les jours fériés dans une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            calendar_id: ID du calendrier
            
        Returns:
            Liste des jours fériés
        """
        if calendar_id is None:
            calendar = self.calendar_repo.get_current_calendar(start_date)
            if not calendar:
                return []
            calendar_id = calendar.id
        
        return self.holiday_repo.get_holidays_in_range(calendar_id, start_date, end_date)
    
    def get_vacations_in_period(self, start_date: date, end_date: date,
                                calendar_id: int = None) -> List[VacationPeriodModel]:
        """
        Récupère toutes les périodes de vacances dans une période.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            calendar_id: ID du calendrier
            
        Returns:
            Liste des périodes de vacances
        """
        if calendar_id is None:
            calendar = self.calendar_repo.get_current_calendar(start_date)
            if not calendar:
                return []
            calendar_id = calendar.id
        
        return self.vacation_repo.get_vacations_in_range(calendar_id, start_date, end_date)
    
    def get_current_calendar(self) -> Optional[AcademicCalendarModel]:
        """
        Récupère le calendrier académique actuel.
        
        Returns:
            Calendrier actuel ou None
        """
        return self.calendar_repo.get_current_calendar()
    
    def validate_date_range(self, start_date: date, end_date: date) -> dict:
        """
        Valide une plage de dates pour l'ordonnancement.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec le résultat de la validation
        """
        if start_date > end_date:
            return {
                'valid': False,
                'reason': 'La date de fin doit être après la date de début'
            }
        
        # Vérifier qu'il y a au moins un jour ouvrable
        effective_days = self.calculate_effective_days(start_date, end_date)
        
        if effective_days == 0:
            return {
                'valid': False,
                'reason': 'Aucun jour ouvrable dans la période',
                'effective_days': 0
            }
        
        return {
            'valid': True,
            'effective_days': effective_days,
            'total_days': (end_date - start_date).days + 1
        }
    
    def get_next_workday(self, reference_date: date, calendar_id: int = None) -> Optional[date]:
        """
        Retourne le prochain jour ouvrable après une date donnée.
        
        Args:
            reference_date: Date de référence
            calendar_id: ID du calendrier
            
        Returns:
            Prochain jour ouvrable ou None si non trouvé dans les 30 prochains jours
        """
        current_date = reference_date + timedelta(days=1)
        max_date = reference_date + timedelta(days=30)
        
        while current_date <= max_date:
            if self.is_workday(current_date, calendar_id):
                return current_date
            current_date += timedelta(days=1)
        
        return None
    
    def get_calendar_summary(self, calendar_id: int) -> dict:
        """
        Retourne un résumé du calendrier académique.
        
        Args:
            calendar_id: ID du calendrier
            
        Returns:
            Dictionnaire avec les informations du calendrier
        """
        calendar = self.calendar_repo.get_complete_calendar(calendar_id)
        
        if not calendar:
            return {'error': 'Calendrier introuvable'}
        
        total_days = (calendar.end_date - calendar.start_date).days + 1
        effective_days = self.calculate_effective_days(
            calendar.start_date,
            calendar.end_date,
            calendar_id
        )
        
        return {
            'name': calendar.name,
            'academic_year': calendar.academic_year,
            'start_date': calendar.start_date,
            'end_date': calendar.end_date,
            'total_days': total_days,
            'effective_days': effective_days,
            'hours_per_day': calendar.hours_per_day,
            'total_hours': effective_days * calendar.hours_per_day,
            'holidays_count': len(calendar.holidays),
            'vacation_periods_count': len(calendar.vacation_periods),
            'weekends_count': total_days - effective_days - len(calendar.holidays)
        }