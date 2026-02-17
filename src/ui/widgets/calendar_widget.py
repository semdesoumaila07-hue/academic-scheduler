"""
Widget de calendrier académique.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QPushButton, QLabel, QListWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextCharFormat, QColor
from sqlalchemy.orm import Session


class CalendarWidget(QWidget):
    """
    Widget pour afficher et gérer le calendrier académique.
    """
    
    def __init__(self, parent=None, session: Session = None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
    
    def set_session(self, session: Session):
        """Définit la session après la création du widget."""
        self.session = session
        print(f"DEBUG CalendarWidget.set_session: session = {self.session}")
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QHBoxLayout(self)
        
        # Calendrier
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
        
        # Boutons de gestion
        buttons = QHBoxLayout()
        
        self.btn_add_calendar = QPushButton("📅 Créer Calendrier")
        self.btn_add_calendar.clicked.connect(self.on_add_calendar)
        buttons.addWidget(self.btn_add_calendar)
        
        self.btn_add_holiday = QPushButton("➕ Ajouter Jour Férié")
        self.btn_add_holiday.clicked.connect(self.on_add_holiday)
        buttons.addWidget(self.btn_add_holiday)
        
        self.btn_add_vacation = QPushButton("🏖️ Ajouter Vacances")
        self.btn_add_vacation.clicked.connect(self.on_add_vacation)
        buttons.addWidget(self.btn_add_vacation)
        
        buttons.addStretch()
        
        calendar_layout.addLayout(buttons)
        
        layout.addLayout(calendar_layout, 2)
        
        # Liste des événements
        events_layout = QVBoxLayout()
        
        events_title = QLabel("Événements")
        events_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        events_layout.addWidget(events_title)
        
        self.events_list = QListWidget()
        events_layout.addWidget(self.events_list)
        
        layout.addLayout(events_layout, 1)
        
        # Marquer les jours spéciaux
        self.mark_special_days()
    
    def mark_special_days(self):
        """Marque les jours fériés et vacances."""
        # Jours fériés en rouge
        holiday_format = QTextCharFormat()
        holiday_format.setBackground(QColor("#e74c3c"))
        holiday_format.setForeground(QColor("white"))
        
        # Exemple: 1er janvier
        self.calendar.setDateTextFormat(QDate(2026, 1, 1), holiday_format)
        
        # Weekends en gris clair
        weekend_format = QTextCharFormat()
        weekend_format.setBackground(QColor("#ecf0f1"))
        
        # Appliquer aux samedis et dimanches
        # TODO: Implémenter pour tous les weekends
    
    def on_add_calendar(self):
        """Ouvre le dialogue pour créer un calendrier académique."""
        from ..dialogs.academic_calendar_dialog import AcademicCalendarDialog
        dialog = AcademicCalendarDialog(self, self.session)
        if dialog.exec_():
            self.mark_special_days()
            self.update_events_list()
    
    def on_add_holiday(self):
        """Ouvre le dialogue pour ajouter un jour férié."""
        from ..dialogs.holiday_dialog import HolidayDialog
        dialog = HolidayDialog(self, self.session)
        if dialog.exec_():
            self.mark_special_days()
            self.update_events_list()
    
    def on_add_vacation(self):
        """Ouvre le dialogue pour ajouter une période de vacances."""
        from ..dialogs.vacation_dialog import VacationDialog
        dialog = VacationDialog(self, self.session)
        if dialog.exec_():
            self.mark_special_days()
            self.update_events_list()
    
    def update_events_list(self):
        """Met à jour la liste des événements."""
        if self.session:
            try:
                from ...database.repositories import HolidayRepository, VacationPeriodRepository
                
                self.events_list.clear()
                
                # Charger les jours fériés
                holiday_repo = HolidayRepository(self.session)
                holidays = holiday_repo.get_all()
                for holiday in holidays:
                    self.events_list.addItem(f"🚫 {holiday.name} - {holiday.date.strftime('%d/%m/%Y')}")
                
                # Charger les périodes de vacances
                vacation_repo = VacationPeriodRepository(self.session)
                vacations = vacation_repo.get_all()
                for vacation in vacations:
                    self.events_list.addItem(
                        f"🏖️ {vacation.name} - {vacation.start_date.strftime('%d/%m/%Y')} "
                        f"à {vacation.end_date.strftime('%d/%m/%Y')}"
                    )
            except Exception:
                pass
    
    def on_date_selected(self, date: QDate):
        """Appelé quand une date est sélectionnée."""
        self.events_list.clear()
        
        # TODO: Charger les événements de cette date
        self.events_list.addItem(f"Jour sélectionné: {date.toString('dd/MM/yyyy')}")
