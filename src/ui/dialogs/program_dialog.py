"""
Dialogue pour la gestion des programmes.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from sqlalchemy.orm import Session

from ...database.repositories import ProgramRepository, UFRRepository
from ...database.models import ProgramLevelEnum


class ProgramDialog(QDialog):
    """Dialogue pour créer/modifier un programme."""
    
    def __init__(self, parent=None, session: Session = None, program_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.program_id = program_id
        self.program_repo = ProgramRepository(session) if session else None
        self.ufr_repo = UFRRepository(session) if session else None
        
        self.init_ui()
        
        if program_id:
            self.load_program_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Nouveau Programme" if not self.program_id else "Modifier Programme"
        )
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # UFR
        self.ufr_combo = QComboBox()
        self.ufr_combo.addItem("-- Sélectionner une UFR --", None)
        if self.ufr_repo and self.session:
            try:
                ufrs = self.ufr_repo.get_all()
                for u in ufrs:
                    self.ufr_combo.addItem(u.name, u.id)
            except Exception:
                pass
        form_layout.addRow("UFR *:", self.ufr_combo)
        
        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Licence Informatique")
        form_layout.addRow("Nom *:", self.name_edit)
        
        # Code
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Ex: L3-INFO")
        form_layout.addRow("Code *:", self.code_edit)
        
        # Niveau
        self.level_combo = QComboBox()
        for level in ProgramLevelEnum:
            self.level_combo.addItem(level.value, level)
        form_layout.addRow("Niveau *:", self.level_combo)
        
        # Durée (années)
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 5)
        self.duration_spin.setValue(1)
        form_layout.addRow("Durée (années) *:", self.duration_spin)
        
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
    
    def load_program_data(self):
        """Charge les données du programme."""
        if self.program_repo:
            try:
                program = self.program_repo.get_by_id(self.program_id)
                if program:
                    self.name_edit.setText(program.name)
                    self.code_edit.setText(program.code)
                    self.duration_spin.setValue(program.duration_years)
                    
                    # Sélectionner l'UFR
                    for i in range(self.ufr_combo.count()):
                        if self.ufr_combo.itemData(i) == program.ufr_id:
                            self.ufr_combo.setCurrentIndex(i)
                            break
                    
                    # Sélectionner le niveau
                    for i in range(self.level_combo.count()):
                        if self.level_combo.itemData(i) == program.level:
                            self.level_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger le programme: {e}")
    
    def on_save(self):
        """Enregistre le programme."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        if not self.code_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le code est obligatoire")
            return
        
        ufr_id = self.ufr_combo.currentData()
        if not ufr_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une UFR")
            return
        
        if not self.program_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        try:
            if self.program_id:
                self.program_repo.update(
                    self.program_id,
                    name=self.name_edit.text().strip(),
                    code=self.code_edit.text().strip(),
                    level=self.level_combo.currentData(),
                    duration_years=self.duration_spin.value(),
                    ufr_id=ufr_id
                )
                QMessageBox.information(self, "Succès", "Programme modifié avec succès")
            else:
                self.program_repo.create(
                    name=self.name_edit.text().strip(),
                    code=self.code_edit.text().strip(),
                    level=self.level_combo.currentData(),
                    duration_years=self.duration_spin.value(),
                    ufr_id=ufr_id
                )
                QMessageBox.information(self, "Succès", "Programme créé avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
