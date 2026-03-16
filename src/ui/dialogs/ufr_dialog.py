"""
Dialogue pour la gestion des UFR.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from sqlalchemy.orm import Session

from ...database.repositories import UFRRepository, UniversityRepository


class UFRDialog(QDialog):
    """Dialogue pour créer/modifier une UFR."""
    
    def __init__(self, parent=None, session: Session = None, ufr_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.ufr_id = ufr_id
        self.ufr_repo = UFRRepository(session) if session else None
        self.university_repo = UniversityRepository(session) if session else None
        
        self.init_ui()
        
        if ufr_id:
            self.load_ufr_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Nouvelle UFR" if not self.ufr_id else "Modifier UFR"
        )
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Université
        self.university_combo = QComboBox()
        self.university_combo.addItem("-- Sélectionner une université --", None)
        if self.university_repo and self.session:
            try:
                universities = self.university_repo.get_all()
                for u in universities:
                    self.university_combo.addItem(u.name, u.id)
            except Exception:
                pass
        form_layout.addRow("Université *:", self.university_combo)
        
        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: UFR Sciences Exactes et Appliquées")
        form_layout.addRow("Nom *:", self.name_edit)
        
        # Code
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Ex: UFR-SEA")
        form_layout.addRow("Code *:", self.code_edit)
        
        # Directeur
        self.director_edit = QLineEdit()
        self.director_edit.setPlaceholderText("Ex: Pr. Jean-Baptiste OUEDRAOGO")
        form_layout.addRow("Directeur:", self.director_edit)
        
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
    
    def load_ufr_data(self):
        """Charge les données de l'UFR."""
        if self.ufr_repo:
            try:
                ufr = self.ufr_repo.get_by_id(self.ufr_id)
                if ufr:
                    self.name_edit.setText(ufr.name)
                    self.code_edit.setText(ufr.code)
                    self.director_edit.setText(ufr.director or "")
                    
                    # Sélectionner l'université
                    for i in range(self.university_combo.count()):
                        if self.university_combo.itemData(i) == ufr.university_id:
                            self.university_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger l'UFR: {e}")
    
    def on_save(self):
        """Enregistre l'UFR."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        if not self.code_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le code est obligatoire")
            return
        
        university_id = self.university_combo.currentData()
        if not university_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une université")
            return
        
        if not self.ufr_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        try:
            if self.ufr_id:
                self.ufr_repo.update(
                    self.ufr_id,
                    name=self.name_edit.text().strip(),
                    code=self.code_edit.text().strip(),
                    director=self.director_edit.text().strip() or None,
                    university_id=university_id
                )
                QMessageBox.information(self, "Succès", "UFR modifiée avec succès")
            else:
                self.ufr_repo.create(
                    name=self.name_edit.text().strip(),
                    code=self.code_edit.text().strip(),
                    director=self.director_edit.text().strip() or None,
                    university_id=university_id
                )
                QMessageBox.information(self, "Succès", "UFR créée avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
