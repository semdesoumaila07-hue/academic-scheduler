"""
Dialogue pour l'ajout de jours fériés.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox, QDateEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import HolidayRepository, CalendarRepository


class HolidayDialog(QDialog):
    """Dialogue pour ajouter/modifier un jour férié."""
    
    def __init__(self, parent=None, session: Session = None, holiday_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.holiday_id = holiday_id
        self.holiday_repo = HolidayRepository(session) if session else None
        self.calendar_repo = CalendarRepository(session) if session else None
        
        self.init_ui()
        
        if holiday_id:
            self.load_holiday_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Ajouter Jour Férié" if not self.holiday_id else "Modifier Jour Férié"
        )
        self.setMinimumWidth(500)
        
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
        
        # Nom du jour férié
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Jour de l'An")
        form_layout.addRow("Nom du jour *:", self.name_edit)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date *:", self.date_edit)
        
        # Récurrent (tous les ans)
        self.recurring_check = QCheckBox("Récurrent (tous les ans)")
        self.recurring_check.setChecked(True)
        form_layout.addRow("", self.recurring_check)
        
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
    
    def load_holiday_data(self):
        """Charge les données du jour férié."""
        if self.holiday_repo:
            try:
                holiday = self.holiday_repo.get_by_id(self.holiday_id)
                if holiday:
                    self.name_edit.setText(holiday.name)
                    self.date_edit.setDate(QDate(holiday.date.year, holiday.date.month, holiday.date.day))
                    self.recurring_check.setChecked(holiday.is_recurring)
                    
                    # Sélectionner le calendrier
                    for i in range(self.calendar_combo.count()):
                        if self.calendar_combo.itemData(i) == holiday.calendar_id:
                            self.calendar_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger le jour férié: {e}")
    
    def on_save(self):
        """Enregistre le jour férié."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        calendar_id = self.calendar_combo.currentData()
        if not calendar_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un calendrier")
            return
        
        if not self.holiday_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        try:
            if self.holiday_id:
                self.holiday_repo.update(
                    self.holiday_id,
                    name=self.name_edit.text().strip(),
                    date=self.date_edit.date().toPyDate(),
                    is_recurring=self.recurring_check.isChecked(),
                    calendar_id=calendar_id
                )
                QMessageBox.information(self, "Succès", "Jour férié modifié avec succès")
            else:
                self.holiday_repo.create(
                    name=self.name_edit.text().strip(),
                    date=self.date_edit.date().toPyDate(),
                    is_recurring=self.recurring_check.isChecked(),
                    calendar_id=calendar_id
                )
                QMessageBox.information(self, "Succès", "Jour férié ajouté avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
