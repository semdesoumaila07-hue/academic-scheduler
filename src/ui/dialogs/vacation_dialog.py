"""
Dialogue pour l'ajout de périodes de vacances.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import VacationPeriodRepository, CalendarRepository
from ...database.models import VacationTypeEnum


class VacationDialog(QDialog):
    """Dialogue pour ajouter/modifier une période de vacances."""
    
    def __init__(self, parent=None, session: Session = None, vacation_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.vacation_id = vacation_id
        self.vacation_repo = VacationPeriodRepository(session) if session else None
        self.calendar_repo = CalendarRepository(session) if session else None
        
        self.init_ui()
        
        if vacation_id:
            self.load_vacation_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Ajouter Période de Vacances" if not self.vacation_id else "Modifier Période de Vacances"
        )
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Sélectionner le calendrier
        self.calendar_combo = QComboBox()
        self.calendar_combo.addItem("-- Sélectionner un calendrier --", None)
        if self.calendar_repo and self.session:
            try:
                calendars = self.calendar_repo.get_all()
                print(f"DEBUG: Calendriers trouvés: {len(calendars) if calendars else 0}")
                if calendars:
                    for c in calendars:
                        print(f"DEBUG: Ajout calendrier: {c.name} (id: {c.id})")
                        self.calendar_combo.addItem(c.name, c.id)
                else:
                    self.calendar_combo.setToolTip("⚠️ Aucun calendrier disponible. Créez d'abord un calendrier.")
            except Exception as e:
                print(f"DEBUG: Erreur lors du chargement des calendriers: {e}")
                self.calendar_combo.setToolTip(f"❌ Erreur: {str(e)}")
        form_layout.addRow("Calendrier *:", self.calendar_combo)
        
        # Nom de la période
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Vacances de Noël")
        form_layout.addRow("Nom de la période *:", self.name_edit)
        
        # Type de vacances
        self.type_combo = QComboBox()
        for vac_type in VacationTypeEnum:
            self.type_combo.addItem(vac_type.value, vac_type)
        form_layout.addRow("Type *:", self.type_combo)
        
        # Date de début
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de début *:", self.start_date_edit)
        
        # Date de fin
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        self.end_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de fin *:", self.end_date_edit)
        
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
    
    def load_vacation_data(self):
        """Charge les données de la période de vacances."""
        if self.vacation_repo:
            try:
                vacation = self.vacation_repo.get_by_id(self.vacation_id)
                if vacation:
                    self.name_edit.setText(vacation.name)
                    self.start_date_edit.setDate(QDate(vacation.start_date.year, vacation.start_date.month, vacation.start_date.day))
                    self.end_date_edit.setDate(QDate(vacation.end_date.year, vacation.end_date.month, vacation.end_date.day))
                    
                    # Sélectionner le type
                    for i in range(self.type_combo.count()):
                        if self.type_combo.itemData(i) == vacation.type:
                            self.type_combo.setCurrentIndex(i)
                            break
                    
                    # Sélectionner le calendrier
                    for i in range(self.calendar_combo.count()):
                        if self.calendar_combo.itemData(i) == vacation.calendar_id:
                            self.calendar_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger la période de vacances: {e}")
    
    def on_save(self):
        """Enregistre la période de vacances."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        calendar_id = self.calendar_combo.currentData()
        if not calendar_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un calendrier")
            return
        
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        if start_date >= end_date:
            QMessageBox.warning(self, "Validation", "La date de début doit être avant la date de fin")
            return
        
        if not self.vacation_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        try:
            if self.vacation_id:
                self.vacation_repo.update(
                    self.vacation_id,
                    name=self.name_edit.text().strip(),
                    start_date=start_date,
                    end_date=end_date,
                    type=self.type_combo.currentData(),
                    calendar_id=calendar_id
                )
                QMessageBox.information(self, "Succès", "Période de vacances modifiée avec succès")
            else:
                self.vacation_repo.create(
                    name=self.name_edit.text().strip(),
                    start_date=start_date,
                    end_date=end_date,
                    type=self.type_combo.currentData(),
                    calendar_id=calendar_id
                )
                QMessageBox.information(self, "Succès", "Période de vacances ajoutée avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
