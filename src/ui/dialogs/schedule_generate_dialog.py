"""
Dialogue pour lancer la génération d'emploi du temps (Pfair).
Responsable pédagogique : choix de la cohorte, période, salles, etc.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QDateEdit, QLineEdit, QCheckBox,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import QDate
from sqlalchemy.orm import Session

from ...managers import ScheduleGenerator, StructureManager


class ScheduleGenerateDialog(QDialog):
    """Dialogue pour configurer et lancer la génération d'un emploi du temps."""

    def __init__(self, parent=None, session: Session = None, current_user=None):
        super().__init__(parent)

        self.session = session
        self.current_user = current_user
        self.schedule_generator = ScheduleGenerator(session) if session else None
        self.structure_manager = StructureManager(session) if session else None

        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Générer un Emploi du Temps (Pfair)")
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Choix de la cohorte
        self.cohort_combo = QComboBox()
        self.cohort_combo.addItem("-- Sélectionner une cohorte --", None)
        if self.structure_manager and self.session:
            try:
                cohorts = self.structure_manager.cohort_repo.get_all()
                for c in cohorts:
                    label = f"{c.name} ({c.academic_year})"
                    self.cohort_combo.addItem(label, c.id)
            except Exception:
                pass
        form_layout.addRow("Cohorte *:", self.cohort_combo)

        # Période de génération
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de début *:", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(1))
        self.end_date_edit.setCalendarPopup(True)
        form_layout.addRow("Date de fin *:", self.end_date_edit)

        # Salles disponibles (optionnel)
        self.rooms_edit = QLineEdit()
        self.rooms_edit.setPlaceholderText("Ex: A101,B202,C303 (laisser vide pour ignorer)")
        form_layout.addRow("Salles disponibles:", self.rooms_edit)

        # Remplacer l'EDT existant
        self.replace_checkbox = QCheckBox("Remplacer l'emploi du temps existant pour cette période")
        self.replace_checkbox.setChecked(False)
        form_layout.addRow("", self.replace_checkbox)

        layout.addLayout(form_layout)

        note = QLabel(
            "Le système vérifiera la faisabilité (charge Pfair) et les jours ouvrables\n"
            "avant de générer les créneaux."
        )
        note.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(note)

        buttons_layout = QHBoxLayout()
        btn_generate = QPushButton("🔄 Générer")
        btn_generate.clicked.connect(self.on_generate)
        btn_generate.setDefault(True)
        buttons_layout.addWidget(btn_generate)

        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        layout.addLayout(buttons_layout)

    def on_generate(self):
        """Lance la génération via ScheduleGenerator."""
        if not self.schedule_generator:
            QMessageBox.warning(self, "Erreur", "Session de base de données non disponible")
            return

        cohort_id = self.cohort_combo.currentData()
        if not cohort_id:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une cohorte")
            return

        start_qdate = self.start_date_edit.date()
        end_qdate = self.end_date_edit.date()

        start_date = start_qdate.toPyDate()
        end_date = end_qdate.toPyDate()

        if end_date < start_date:
            QMessageBox.warning(self, "Validation", "La date de fin doit être après la date de début")
            return

        rooms_text = self.rooms_edit.text().strip()
        available_rooms = None
        if rooms_text:
            available_rooms = [r.strip() for r in rooms_text.split(",") if r.strip()]

        replace_existing = self.replace_checkbox.isChecked()

        try:
            result = self.schedule_generator.generate_schedule(
                cohort_id=cohort_id,
                start_date=start_date,
                end_date=end_date,
                available_rooms=available_rooms,
                replace_existing=replace_existing,
                current_user=self.current_user,
            )

            if not result.get("success", False):
                # Message d'erreur détaillé (Pfair ou permissions)
                msg = result.get("error", "Erreur inconnue lors de la génération")
                extra = []
                if "total_charge" in result:
                    extra.append(f"Charge totale: {result['total_charge']:.2f}")
                if "effective_days" in result:
                    extra.append(f"Jours ouvrables: {result['effective_days']}")
                if extra:
                    msg += "\n\n" + "\n".join(extra)

                QMessageBox.warning(self, "Échec de la génération", msg)
                return

            scheduled = result.get("scheduled_slots", 0)
            total_hours = result.get("total_hours", 0)
            conflicts = result.get("conflicts", 0)
            period = result.get("period", f"{start_date} à {end_date}")

            msg = (
                f"Emploi du temps généré avec succès pour la période {period}.\n\n"
                f"Créneaux générés : {scheduled}\n"
                f"Heures planifiées : {total_hours}h\n"
                f"Conflits détectés : {conflicts}"
            )

            QMessageBox.information(self, "Succès", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération :\n{e}")

