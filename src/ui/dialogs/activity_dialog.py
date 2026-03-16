"""
Dialogue pour la gestion des activités académiques.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QSpinBox, QDoubleSpinBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...managers import ActivityManager, StructureManager
from ...database.models import ActivityTypeEnum, PriorityEnum


class ActivityDialog(QDialog):
    """Dialogue pour créer/modifier une activité académique."""

    def __init__(self, parent=None, session: Session = None, activity_id: int = None):
        super().__init__(parent)

        self.session = session
        self.activity_id = activity_id
        self.activity_manager = ActivityManager(session) if session else None
        self.structure_manager = StructureManager(session) if session else None

        self.init_ui()

        if activity_id:
            self.load_activity_data()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(
            "Nouvelle Activité" if not self.activity_id else "Modifier Activité"
        )
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ex: Algorithmique et structures de données")
        form_layout.addRow("Nom *:", self.name_edit)

        # Code
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Ex: ALGO-101")
        form_layout.addRow("Code *:", self.code_edit)

        # Type
        self.type_combo = QComboBox()
        for act_type in ActivityTypeEnum:
            self.type_combo.addItem(act_type.value, act_type)
        form_layout.addRow("Type *:", self.type_combo)

        # Volume horaire
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0.5, 200)
        self.volume_spin.setValue(24)
        self.volume_spin.setSuffix(" h")
        form_layout.addRow("Volume horaire *:", self.volume_spin)

        # Cohorte
        self.cohort_combo = QComboBox()
        self.cohort_combo.addItem("-- Sélectionner une cohorte --", None)
        self.load_cohorts()
        form_layout.addRow("Cohorte *:", self.cohort_combo)

        # Enseignant (optionnel)
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("-- Aucun --", None)
        self.load_teachers()
        form_layout.addRow("Enseignant:", self.teacher_combo)

        # Date d'activation
        self.activation_date = QDateEdit()
        self.activation_date.setDate(QDate.currentDate())
        self.activation_date.setCalendarPopup(True)
        form_layout.addRow("Date d'activation:", self.activation_date)

        # Deadline
        self.deadline_date = QDateEdit()
        self.deadline_date.setDate(QDate.currentDate().addMonths(2))
        self.deadline_date.setCalendarPopup(True)
        form_layout.addRow("Date limite:", self.deadline_date)

        # Priorité
        self.priority_combo = QComboBox()
        for priority in PriorityEnum:
            self.priority_combo.addItem(priority.value, priority)
        self.priority_combo.setCurrentText("Normale")
        form_layout.addRow("Priorité:", self.priority_combo)

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

    def load_cohorts(self):
        """Charge les cohortes disponibles."""
        if not self.structure_manager or not self.session:
            return
        
        try:
            cohorts = self.structure_manager.cohort_repo.get_all()
            if not cohorts:
                self.cohort_combo.setToolTip("⚠️ Aucune cohorte disponible. Veuillez créer une cohorte d'abord.")
            else:
                for c in cohorts:
                    self.cohort_combo.addItem(f"{c.name} ({c.academic_year})", c.id)
        except Exception as e:
            self.cohort_combo.setToolTip(f"❌ Erreur lors du chargement des cohortes: {str(e)}")

    def load_teachers(self):
        """Charge les enseignants disponibles."""
        if not self.structure_manager or not self.session:
            return
        
        try:
            from ...database.repositories import TeacherRepository
            teacher_repo = TeacherRepository(self.session)
            teachers = teacher_repo.get_all()
            for t in teachers:
                self.teacher_combo.addItem(t.full_name, t.id)
        except Exception as e:
            self.teacher_combo.setToolTip(f"⚠️ Erreur lors du chargement des enseignants: {str(e)}")

    def load_activity_data(self):
        """Charge les données de l'activité."""
        pass  # TODO: Implémenter

    def on_save(self):
        """Enregistre l'activité."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            return

        if not self.code_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le code est obligatoire")
            return

        cohort_id = self.cohort_combo.currentData()
        if not cohort_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une cohorte")
            return

        if not self.activity_manager:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return

        teacher_id = self.teacher_combo.currentData()
        result = self.activity_manager.create_activity(
            name=self.name_edit.text().strip(),
            code=self.code_edit.text().strip(),
            activity_type=self.type_combo.currentData(),
            volume_hours=self.volume_spin.value(),
            cohort_id=cohort_id,
            teacher_id=teacher_id,
            activation_date=self.activation_date.date().toPyDate(),
            deadline=self.deadline_date.date().toPyDate(),
            priority=self.priority_combo.currentData(),
        )

        if result.get("success"):
            QMessageBox.information(self, "Succès", result.get("message", "Activité créée"))
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "Erreur inconnue"))
