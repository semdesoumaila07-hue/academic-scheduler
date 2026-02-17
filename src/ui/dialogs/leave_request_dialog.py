"""
Dialogue pour les demandes de congé.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QPushButton, QLabel, QMessageBox,
    QDateEdit, QTextEdit, QWidget
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.models import LeaveTypeEnum, LeaveStatusEnum
from ...database.repositories import LeaveRequestRepository, TeacherRepository
from ...utils.helpers import count_workdays


class LeaveRequestDialog(QDialog):
    """Dialogue pour créer une demande de congé (persistée en base)."""

    def __init__(self, parent=None, session: Session = None, teacher_id: int = None):
        super().__init__(parent)
        self.session = session
        self.teacher_id = teacher_id  # Si fourni, l'enseignant est fixé (connexion enseignant)
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface."""
        self.setWindowTitle("Nouvelle Demande de Congé")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Enseignant (masqué si teacher_id fourni)
        self.teacher_widget = QWidget()
        teacher_row = QFormLayout()
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("-- Sélectionner un enseignant --", None)
        if self.session and not self.teacher_id:
            try:
                teacher_repo = TeacherRepository(self.session)
                for t in teacher_repo.get_all():
                    self.teacher_combo.addItem(f"{t.full_name} ({t.email})", t.id)
            except Exception:
                pass
        teacher_row.addRow("Enseignant *:", self.teacher_combo)
        self.teacher_widget.setLayout(teacher_row)
        layout.addWidget(self.teacher_widget)
        if self.teacher_id is not None:
            self.teacher_widget.setVisible(False)

        # Type de congé
        self.type_combo = QComboBox()
        for leave_type in LeaveTypeEnum:
            self.type_combo.addItem(leave_type.value, leave_type)
        form.addRow("Type de congé *:", self.type_combo)

        # Date de début
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        form.addRow("Date de début *:", self.start_date)

        # Date de fin
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(7))
        self.end_date.setCalendarPopup(True)
        form.addRow("Date de fin *:", self.end_date)

        # Raison
        self.reason_edit = QTextEdit()
        self.reason_edit.setPlaceholderText("Expliquez la raison de votre demande...")
        self.reason_edit.setMaximumHeight(100)
        form.addRow("Raison *:", self.reason_edit)

        layout.addLayout(form)

        # Note
        note = QLabel("La demande sera soumise pour approbation.")
        note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)

        # Boutons
        buttons = QHBoxLayout()
        btn_submit = QPushButton("📨 Soumettre")
        btn_submit.clicked.connect(self.on_submit)
        buttons.addWidget(btn_submit)

        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)

        layout.addLayout(buttons)

    def _get_teacher_id(self):
        if self.teacher_id is not None:
            return self.teacher_id
        return self.teacher_combo.currentData()

    def on_submit(self):
        """Valide, vérifie les chevauchements et persiste la demande en base."""
        reason = self.reason_edit.toPlainText().strip()
        if not reason:
            QMessageBox.warning(self, "Validation", "La raison est obligatoire")
            return

        teacher_id = self._get_teacher_id()
        if teacher_id is None:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner un enseignant.")
            return

        if not self.session:
            QMessageBox.critical(self, "Erreur", "Session base de données indisponible.")
            return

        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        if start_date > end_date:
            QMessageBox.warning(self, "Validation", "La date de fin doit être après la date de début.")
            return

        leave_repo = LeaveRequestRepository(self.session)
        if leave_repo.check_overlap(teacher_id, start_date, end_date):
            QMessageBox.warning(
                self, "Chevauchement",
                "Une demande de congé existe déjà sur cette période pour cet enseignant."
            )
            return

        try:
            working_days = count_workdays(start_date, end_date)
            leave_repo.create(
                teacher_id=teacher_id,
                start_date=start_date,
                end_date=end_date,
                leave_type=self.type_combo.currentData(),
                reason=reason,
                status=LeaveStatusEnum.PENDING,
                working_days=working_days,
            )
            QMessageBox.information(self, "Succès", "Demande de congé enregistrée et soumise pour approbation.")
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible d'enregistrer la demande : {e}"
            )