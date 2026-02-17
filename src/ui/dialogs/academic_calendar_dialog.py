"""
Dialogue pour créer un calendrier académique.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QDateEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import CalendarRepository


class AcademicCalendarDialog(QDialog):
    """Dialogue pour créer/modifier un calendrier académique."""
    
    def __init__(self, parent=None, session: Session = None, calendar_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.calendar_id = calendar_id
        print(f"DEBUG AcademicCalendarDialog: session = {self.session}")
        self.calendar_repo = CalendarRepository(session) if session else None
        print(f"DEBUG AcademicCalendarDialog: calendar_repo = {self.calendar_repo}")
        
        self.init_ui()
        
        if calendar_id:
            self.load_calendar_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Nouveau Calendrier Académique" if not self.calendar_id else "Modifier Calendrier"
        )
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Calendrier 2025-2026")
        form_layout.addRow("Nom *:", self.name_edit)
        
        # Année académique
        self.academic_year_edit = QLineEdit()
        self.academic_year_edit.setPlaceholderText("Ex: 2025-2026")
        form_layout.addRow("Année académique *:", self.academic_year_edit)
        
        # Date de début
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de début *:", self.start_date_edit)
        
        # Date de fin
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(9))
        self.end_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de fin *:", self.end_date_edit)
        
        # Heures par jour
        self.hours_per_day_spin = QSpinBox()
        self.hours_per_day_spin.setRange(1, 12)
        self.hours_per_day_spin.setValue(8)
        self.hours_per_day_spin.setSuffix(" h")
        form_layout.addRow("Heures par jour:", self.hours_per_day_spin)
        
        layout.addLayout(form_layout)
        
        note = QLabel("* Champs obligatoires")
        note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)
        
        buttons_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.clicked.connect(self.on_save)
        btn_save.setDefault(True)
        buttons_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        layout.addLayout(buttons_layout)
    
    def load_calendar_data(self):
        """Charge les données du calendrier."""
        if self.calendar_repo:
            try:
                calendar = self.calendar_repo.get_by_id(self.calendar_id)
                if calendar:
                    self.name_edit.setText(calendar.name)
                    self.academic_year_edit.setText(calendar.academic_year)
                    self.start_date_edit.setDate(QDate(calendar.start_date.year, calendar.start_date.month, calendar.start_date.day))
                    self.end_date_edit.setDate(QDate(calendar.end_date.year, calendar.end_date.month, calendar.end_date.day))
                    self.hours_per_day_spin.setValue(calendar.hours_per_day)
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger le calendrier: {e}")
    
    def on_save(self):
        """Enregistre le calendrier."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        if not self.academic_year_edit.text().strip():
            QMessageBox.warning(self, "Validation", "L'année académique est obligatoire")
            return
        
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        if start_date >= end_date:
            QMessageBox.warning(self, "Validation", "La date de début doit être avant la date de fin")
            return
        
        print(f"DEBUG on_save: session = {self.session}, calendar_repo = {self.calendar_repo}")
        
        if not self.session:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        if not self.calendar_repo:
            QMessageBox.warning(self, "Erreur", "Repository calendrier non disponible")
            return
        
        try:
            if self.calendar_id:
                self.calendar_repo.update(
                    self.calendar_id,
                    name=self.name_edit.text().strip(),
                    academic_year=self.academic_year_edit.text().strip(),
                    start_date=start_date,
                    end_date=end_date,
                    hours_per_day=self.hours_per_day_spin.value()
                )
                QMessageBox.information(self, "Succès", "Calendrier modifié avec succès")
            else:
                self.calendar_repo.create(
                    name=self.name_edit.text().strip(),
                    academic_year=self.academic_year_edit.text().strip(),
                    start_date=start_date,
                    end_date=end_date,
                    hours_per_day=self.hours_per_day_spin.value()
                )
                QMessageBox.information(self, "Succès", "Calendrier créé avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
