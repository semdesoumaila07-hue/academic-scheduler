<<<<<<< HEAD
from PyQt5.QtWidgets import QDialog

class ConstraintReportDialog(QDialog):
    """Dialogue pour soumettre un rapport de contrainte (squelette minimal)."""
    def __init__(self, parent=None, session=None, teacher_id=None):
        super().__init__(parent)
        self.session = session
        self.teacher_id = teacher_id
        self.setWindowTitle("Rapport de contrainte")
        # Ajoutez ici la logique UI et gestion des rapports
=======
"""
Dialogue pour soumettre un signalement de conflit ou contrainte (enseignant).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QTextEdit, QLabel, QMessageBox
)
from sqlalchemy.orm import Session

from ...database.models import ConstraintReportTypeEnum
from ...database.repositories import ConstraintReportRepository


class ConstraintReportDialog(QDialog):
    """Dialogue pour créer un signalement (conflit ou contrainte)."""

    def __init__(self, parent=None, session: Session = None, teacher_id: int = None):
        super().__init__(parent)
        self.session = session
        self.teacher_id = teacher_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Signaler un conflit ou une contrainte")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.type_combo = QComboBox()
        for t in ConstraintReportTypeEnum:
            self.type_combo.addItem(t.value, t)
        form.addRow("Type *:", self.type_combo)

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Décrivez le conflit ou la contrainte (créneau concerné, raison...)")
        self.desc_edit.setMaximumHeight(120)
        form.addRow("Description *:", self.desc_edit)

        layout.addLayout(form)
        layout.addWidget(QLabel("L'équipe pédagogique traitera votre signalement."))
        buttons = QHBoxLayout()
        btn_ok = QPushButton("Envoyer")
        btn_ok.clicked.connect(self.on_submit)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_ok)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)

    def on_submit(self):
        desc = self.desc_edit.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Validation", "La description est obligatoire.")
            return
        if not self.session or not self.teacher_id:
            QMessageBox.critical(self, "Erreur", "Contexte invalide.")
            return
        try:
            repo = ConstraintReportRepository(self.session)
            repo.create(
                teacher_id=self.teacher_id,
                report_type=self.type_combo.currentData(),
                description=desc,
            )
            QMessageBox.information(self, "Succès", "Signalement enregistré.")
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer : {e}")
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
