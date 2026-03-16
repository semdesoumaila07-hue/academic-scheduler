"""
Dialogue pour la gestion des cohortes.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel, QMessageBox,
    QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import CohortRepository, ProgramRepository


class CohortDialog(QDialog):
    """Dialogue pour créer/modifier une cohorte."""
    
    def __init__(self, parent=None, session: Session = None, cohort_id: int = None):
        super().__init__(parent)
        
        self.session = session
        self.cohort_id = cohort_id
        self.cohort_repo = CohortRepository(session) if session else None
        self.program_repo = ProgramRepository(session) if session else None
        
        self.init_ui()
        
        if cohort_id:
            self.load_cohort_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Nouvelle Cohorte" if not self.cohort_id else "Modifier Cohorte"
        )
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Programme
        self.program_combo = QComboBox()
        self.program_combo.addItem("-- Sélectionner un programme --", None)
        if self.program_repo and self.session:
            try:
                programs = self.program_repo.get_all()
                for p in programs:
                    self.program_combo.addItem(p.name, p.id)
            except Exception:
                pass
        form_layout.addRow("Programme *:", self.program_combo)
        
        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: L3 Info 2025-2026")
        form_layout.addRow("Nom *:", self.name_edit)
        
        # Année académique
        self.academic_year_edit = QLineEdit()
        self.academic_year_edit.setPlaceholderText("Ex: 2025-2026")
        form_layout.addRow("Année académique *:", self.academic_year_edit)
        
        # Semestre
        self.semester_combo = QComboBox()
        self.semester_combo.addItem("Semestre 1", 1)
        self.semester_combo.addItem("Semestre 2", 2)
        form_layout.addRow("Semestre *:", self.semester_combo)
        
        # Nombre d'étudiants
        self.student_count_spin = QSpinBox()
        self.student_count_spin.setRange(1, 500)
        self.student_count_spin.setValue(45)
        form_layout.addRow("Nombre d'étudiants:", self.student_count_spin)
        
        # Date de début
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de début *:", self.start_date_edit)
        
        # Date de fin
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(6))
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
    
    def load_cohort_data(self):
        """Charge les données de la cohorte."""
        if self.cohort_repo:
            try:
                cohort = self.cohort_repo.get_by_id(self.cohort_id)
                if cohort:
                    self.name_edit.setText(cohort.name)
                    self.academic_year_edit.setText(cohort.academic_year)
                    self.student_count_spin.setValue(cohort.student_count)
                    self.start_date_edit.setDate(QDate(cohort.start_date.year, cohort.start_date.month, cohort.start_date.day))
                    self.end_date_edit.setDate(QDate(cohort.end_date.year, cohort.end_date.month, cohort.end_date.day))
                    
                    # Sélectionner le semestre
                    self.semester_combo.setCurrentIndex(cohort.semester - 1)
                    
                    # Sélectionner le programme
                    for i in range(self.program_combo.count()):
                        if self.program_combo.itemData(i) == cohort.program_id:
                            self.program_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger la cohorte: {e}")
    
    def on_save(self):
        """Enregistre la cohorte."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return
        
        if not self.academic_year_edit.text().strip():
            QMessageBox.warning(self, "Validation", "L'année académique est obligatoire")
            return
        
        program_id = self.program_combo.currentData()
        if not program_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un programme")
            return
        
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        if start_date >= end_date:
            QMessageBox.warning(self, "Validation", "La date de début doit être avant la date de fin")
            return
        
        if not self.cohort_repo:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return
        
        try:
            if self.cohort_id:
                self.cohort_repo.update(
                    self.cohort_id,
                    name=self.name_edit.text().strip(),
                    academic_year=self.academic_year_edit.text().strip(),
                    semester=self.semester_combo.currentData(),
                    student_count=self.student_count_spin.value(),
                    program_id=program_id,
                    start_date=start_date,
                    end_date=end_date
                )
                QMessageBox.information(self, "Succès", "Cohorte modifiée avec succès")
            else:
                self.cohort_repo.create(
                    name=self.name_edit.text().strip(),
                    academic_year=self.academic_year_edit.text().strip(),
                    semester=self.semester_combo.currentData(),
                    student_count=self.student_count_spin.value(),
                    program_id=program_id,
                    start_date=start_date,
                    end_date=end_date
                )
                QMessageBox.information(self, "Succès", "Cohorte créée avec succès")
            
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")
