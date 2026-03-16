"""
Dialogue pour la gestion des enseignants.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QSpinBox
)
from PyQt5.QtCore import Qt
from sqlalchemy.orm import Session

from ...database.repositories import TeacherRepository
from ...database.models import TeacherStatusEnum


class TeacherDialog(QDialog):
    """
    Dialogue pour créer/modifier un enseignant.
    """
    
    def __init__(self, parent=None, session: Session = None, teacher_id: int = None):
        """
        Initialise le dialogue.
        
        Args:
            parent: Widget parent
            session: Session de base de données
            teacher_id: ID de l'enseignant (None pour création)
        """
        super().__init__(parent)
        
        self.session = session
        self.teacher_id = teacher_id
        self.teacher_repo = TeacherRepository(session) if session else None
        
        self.init_ui()
        
        if teacher_id:
            self.load_teacher_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Nouvel Enseignant" if not self.teacher_id else "Modifier Enseignant")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom complet
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Dr. Marie KABORE")
        form_layout.addRow("Nom complet *:", self.name_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Ex: marie.kabore@univ.bf")
        form_layout.addRow("Email *:", self.email_edit)
        
        # Téléphone
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Ex: +226 70 12 34 56")
        form_layout.addRow("Téléphone:", self.phone_edit)
        
        # Spécialité
        self.speciality_edit = QLineEdit()
        self.speciality_edit.setPlaceholderText("Ex: Algorithmique")
        form_layout.addRow("Spécialité *:", self.speciality_edit)
        
        # Statut
        self.status_combo = QComboBox()
        for status in TeacherStatusEnum:
            self.status_combo.addItem(status.value, status)
        form_layout.addRow("Statut *:", self.status_combo)
        
        # Heures max par semaine
        self.max_hours_week_spin = QSpinBox()
        self.max_hours_week_spin.setRange(1, 60)
        self.max_hours_week_spin.setValue(40)
        form_layout.addRow("Heures max/semaine:", self.max_hours_week_spin)
        
        # Heures max par jour
        self.max_hours_day_spin = QSpinBox()
        self.max_hours_day_spin.setRange(1, 12)
        self.max_hours_day_spin.setValue(8)
        form_layout.addRow("Heures max/jour:", self.max_hours_day_spin)
        
        layout.addLayout(form_layout)
        
        # Note
        note = QLabel("* Champs obligatoires")
        note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.clicked.connect(self.on_save)
        btn_save.setDefault(True)
        buttons_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        layout.addLayout(buttons_layout)
    
    def load_teacher_data(self):
        """Charge les données de l'enseignant."""
        if not self.teacher_repo or not self.teacher_id:
            return
        try:
            teacher = self.teacher_repo.get_by_id(self.teacher_id)
            if teacher:
                self.name_edit.setText(teacher.full_name)
                self.email_edit.setText(teacher.email)
                self.phone_edit.setText(teacher.phone or "")
                self.speciality_edit.setText(teacher.speciality)
                idx = self.status_combo.findData(teacher.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)
                self.max_hours_week_spin.setValue(teacher.max_hours_per_week)
                self.max_hours_day_spin.setValue(teacher.max_hours_per_day)
        except Exception:
            pass
    
    def on_save(self):
        """Enregistre l'enseignant."""
        if not self.teacher_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return

        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        if not self.email_edit.text().strip():
            QMessageBox.warning(self, "Validation", "L'email est obligatoire")
            return
        
        if not self.speciality_edit.text().strip():
            QMessageBox.warning(self, "Validation", "La spécialité est obligatoire")
            return
        
        try:
            if self.teacher_id:
                self.teacher_repo.update(
                    self.teacher_id,
                    full_name=self.name_edit.text().strip(),
                    email=self.email_edit.text().strip(),
                    phone=self.phone_edit.text().strip() or None,
                    speciality=self.speciality_edit.text().strip(),
                    status=self.status_combo.currentData(),
                    max_hours_per_week=self.max_hours_week_spin.value(),
                    max_hours_per_day=self.max_hours_day_spin.value(),
                )
                msg = "Enseignant mis à jour avec succès"
            else:
                self.teacher_repo.create(
                    full_name=self.name_edit.text().strip(),
                    email=self.email_edit.text().strip(),
                    phone=self.phone_edit.text().strip() or None,
                    speciality=self.speciality_edit.text().strip(),
                    status=self.status_combo.currentData(),
                    max_hours_per_week=self.max_hours_week_spin.value(),
                    max_hours_per_day=self.max_hours_day_spin.value(),
                )
                msg = f"Enseignant {self.name_edit.text()} créé avec succès"
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")