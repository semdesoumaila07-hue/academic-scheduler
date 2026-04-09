"""
Onglet Tâches Sporadiques — Gestion des examens et soutenances ponctuels.

Implémente le test d'acceptation de Liu & Layland :
    ΣU_périodiques + Us ≤ 1.0
où Us = Cs / ds (volume horaire / fenêtre d'exécution en jours ouvrables)

Les tâches acceptées sont planifiées via l'algorithme EDF (Earliest Deadline First)
sur la capacité résiduelle laissée par les tâches périodiques.
"""
from datetime import date, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QComboBox, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit, QProgressBar
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont

from src.database.db_manager import db_manager
from src.database.models import (
    AcademicActivityModel, CohortModel, TeacherModel,
    ActivityTypeEnum, ActivityStatusEnum, PriorityEnum
)
from src.database.repositories.cohort_repository import CohortRepository
from src.database.repositories.teacher_repository import TeacherRepository
from src.services.pfair_scheduler import PfairScheduler


# ══════════════════════════════════════════════════════════════════
# DIALOGUE CRÉATION D'UNE TÂCHE SPORADIQUE
# ══════════════════════════════════════════════════════════════════

class SporadicTaskDialog(QDialog):
    """
    Dialogue de création d'une tâche sporadique.
    Champs spécifiques : arrival_date, execution_window.
    """

    def __init__(self, cohorts, teachers, parent=None):
        super().__init__(parent)
        self.cohorts  = cohorts
        self.teachers = teachers
        self.setWindowTitle("Nouvelle tâche sporadique")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(14)

        # En-tête
        title = QLabel("➕  Nouvelle tâche sporadique")
        title.setStyleSheet("font-size:15px; font-weight:bold; color:#1a73e8;")
        layout.addWidget(title)

        info = QLabel(
            "Une tâche sporadique (examen, soutenance ponctuelle) arrive à une date "
            "précise et doit être exécutée dans une fenêtre limitée.\n"
            "Le test d'acceptation vérifie que ΣU + Us ≤ 1.0 avant planification."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background:#EBF3FB; color:#1F4E79; padding:10px; "
            "border-radius:6px; font-size:12px;"
        )
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)
        st = "border:1px solid #ddd; border-radius:5px; padding:0 8px; height:34px;"

        # Nom
        self._name = QLineEdit()
        self._name.setStyleSheet(st)
        self._name.setPlaceholderText("ex: Examen Final Algo, Soutenance Mémoire")
        form.addRow("Nom :", self._name)

        # Code
        self._code = QLineEdit()
        self._code.setStyleSheet(st)
        self._code.setPlaceholderText("ex: EXF-ALGO-2026")
        form.addRow("Code :", self._code)

        # Type
        self._type = QComboBox()
        self._type.setStyleSheet(st)
        for t in [ActivityTypeEnum.EXAMEN, ActivityTypeEnum.SOUTENANCE]:
            self._type.addItem(t.value, t)
        form.addRow("Type :", self._type)

        # Volume horaire
        self._volume = QDoubleSpinBox()
        self._volume.setRange(1.0, 12.0)
        self._volume.setValue(2.0)
        self._volume.setSuffix(" h")
        self._volume.setStyleSheet(st)
        form.addRow("Volume horaire :", self._volume)

        # Cohorte
        self._cohort = QComboBox()
        self._cohort.setStyleSheet(st)
        for c in self.cohorts:
            self._cohort.addItem(c.name, c.id)
        form.addRow("Cohorte :", self._cohort)

        # Enseignant
        self._teacher = QComboBox()
        self._teacher.setStyleSheet(st)
        self._teacher.addItem("— Non assigné —", None)
        for t in self.teachers:
            self._teacher.addItem(t.full_name, t.id)
        form.addRow("Enseignant responsable :", self._teacher)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#E5E7EB;")

        # Date d'arrivée (ri)
        self._arrival = QDateEdit()
        self._arrival.setCalendarPopup(True)
        self._arrival.setDate(QDate.currentDate())
        self._arrival.setStyleSheet(st)
        form.addRow("Date d'arrivée (ri) :", self._arrival)

        # Fenêtre d'exécution (di)
        self._window = QSpinBox()
        self._window.setRange(1, 90)
        self._window.setValue(7)
        self._window.setSuffix(" jours")
        self._window.setStyleSheet(st)
        self._window.setToolTip(
            "Nombre de jours calendaires à partir de la date d'arrivée "
            "pendant lesquels la tâche peut être planifiée.\n"
            "Deadline = Date d'arrivée + Fenêtre"
        )
        form.addRow("Fenêtre d'exécution (di) :", self._window)

        # Deadline calculée (affichage dynamique)
        self._deadline_lbl = QLabel()
        self._deadline_lbl.setStyleSheet("color:#E65100; font-weight:bold; font-size:12px;")
        form.addRow("Deadline calculée :", self._deadline_lbl)
        self._arrival.dateChanged.connect(self._update_deadline)
        self._window.valueChanged.connect(self._update_deadline)
        self._update_deadline()

        layout.addLayout(form)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet(
            "border:1px solid #ddd; border-radius:6px; padding:0 16px; color:#555;"
        )
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("✅  Créer la tâche")
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet(
            "background:#1a73e8; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 18px;"
        )
        btn_save.clicked.connect(self._validate_and_accept)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _update_deadline(self):
        qd = self._arrival.date()
        d  = date(qd.year(), qd.month(), qd.day())
        deadline = d + timedelta(days=self._window.value())
        self._deadline_lbl.setText(deadline.strftime("%d/%m/%Y"))

    def _validate_and_accept(self):
        if not self._name.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return
        if not self._code.text().strip():
            QMessageBox.warning(self, "Erreur", "Le code est obligatoire.")
            return
        if self._cohort.count() == 0:
            QMessageBox.warning(self, "Erreur", "Aucune cohorte disponible.")
            return
        self.accept()

    def get_values(self):
        qd = self._arrival.date()
        return {
            'name'             : self._name.text().strip(),
            'code'             : self._code.text().strip(),
            'type'             : self._type.currentData(),
            'volume_hours'     : self._volume.value(),
            'cohort_id'        : self._cohort.currentData(),
            'teacher_id'       : self._teacher.currentData(),
            'arrival_date'     : date(qd.year(), qd.month(), qd.day()),
            'execution_window' : self._window.value(),
            'is_sporadic'      : True,
        }


# ══════════════════════════════════════════════════════════════════
# ONGLET PRINCIPAL
# ══════════════════════════════════════════════════════════════════

class SporadicTab(QWidget):
    """
    Onglet de gestion des tâches sporadiques.

    Fonctionnalités :
    - Créer une tâche sporadique (examen, soutenance)
    - Lancer le test d'acceptation de Liu & Layland
    - Planifier via EDF sur la capacité résiduelle
    - Visualiser le statut de toutes les tâches sporadiques
    """

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.session      = db_manager.get_session()
        self._cohorts     = []
        self._teachers    = []
        self._tasks       = []
        self._init_ui()
        self._load_data()

    # ── Chargement ────────────────────────────────────────────────

    def _load_data(self):
        try:
            self._cohorts  = CohortRepository(self.session).get_all()
            self._teachers = TeacherRepository(self.session).get_all()

            # Charger toutes les tâches sporadiques
            self._tasks = self.session.query(AcademicActivityModel).filter(
                AcademicActivityModel.is_sporadic == True
            ).all()

            self._populate_cohort_filter()
            self._refresh_table()
            self._refresh_stats()
        except Exception as e:
            print(f"[sporadic_tab] Erreur chargement : {e}")

    def _populate_cohort_filter(self):
        self._cohort_filter.blockSignals(True)
        self._cohort_filter.clear()
        self._cohort_filter.addItem("Toutes les cohortes", None)
        for c in self._cohorts:
            self._cohort_filter.addItem(c.name, c.id)
        self._cohort_filter.blockSignals(False)

    def _refresh_table(self):
        cohort_id = self._cohort_filter.currentData()
        tasks = [t for t in self._tasks
                 if cohort_id is None or t.cohort_id == cohort_id]

        self._table.setRowCount(0)
        for row, task in enumerate(tasks):
            self._table.insertRow(row)

            # Deadline
            deadline_str = "—"
            days_left    = None
            if task.arrival_date and task.execution_window:
                deadline = task.arrival_date + timedelta(days=task.execution_window)
                deadline_str = deadline.strftime("%d/%m/%Y")
                days_left = (deadline - date.today()).days

            # Alpha de statut
            remaining = max(0.0, task.volume_hours - (task.hours_done or 0))
            pct = round((1 - remaining / task.volume_hours) * 100) if task.volume_hours > 0 else 0

            # Couleur selon urgence deadline
            if days_left is not None and days_left <= 3:
                bg = QColor("#FEE2E2")
            elif days_left is not None and days_left <= 7:
                bg = QColor("#FEF3C7")
            else:
                bg = QColor("#F0FDF4")

            # Cohorte
            cohort_name = task.cohort.name if task.cohort else "?"
            # Enseignant
            teacher_name = task.teacher.full_name if task.teacher else "—"
            # Type
            type_str = task.type.value if task.type else "?"
            # Statut
            status_str = task.status.value if task.status else "?"

            values = [
                str(task.id),
                task.name,
                type_str,
                cohort_name,
                teacher_name,
                str(task.arrival_date.strftime("%d/%m/%Y") if task.arrival_date else "—"),
                deadline_str,
                f"{task.execution_window or '—'} j",
                f"{remaining:.0f}h / {task.volume_hours:.0f}h",
                status_str,
            ]

            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setBackground(bg)
                item.setTextAlignment(Qt.AlignCenter)
                # Mettre en gras les tâches urgentes (deadline ≤ 3 jours)
                if days_left is not None and days_left <= 3:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self._table.setItem(row, col, item)

            # Barre de progression
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setStyleSheet("""
                QProgressBar { border:1px solid #ccc; border-radius:4px;
                               background:#f0f0f0; height:20px; }
                QProgressBar::chunk { background:#10B981; border-radius:4px; }
            """)
            # Remplacer la colonne statut par la barre
            # (la barre est dans une cellule widget)

        self._table.resizeColumnsToContents()

    def _refresh_stats(self):
        total    = len(self._tasks)
        pending  = sum(1 for t in self._tasks if t.status == ActivityStatusEnum.PENDING)
        sched    = sum(1 for t in self._tasks if t.status == ActivityStatusEnum.SCHEDULED)
        urgent   = 0
        for t in self._tasks:
            if t.arrival_date and t.execution_window:
                deadline  = t.arrival_date + timedelta(days=t.execution_window)
                days_left = (deadline - date.today()).days
                if days_left <= 7:
                    urgent += 1

        self._set_kpi(self._stat_total,     total)
        self._set_kpi(self._stat_pending,   pending)
        self._set_kpi(self._stat_scheduled, sched)
        self._set_kpi(self._stat_urgent,    urgent)

    # ── UI ────────────────────────────────────────────────────────

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Titre
        title = QLabel("⚡  Tâches Sporadiques")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Examens & soutenances ponctuels — Test d'acceptation Liu & Layland "
            "( ΣU_périodiques + Us ≤ 1.0 ) — Planification EDF"
        )
        subtitle.setStyleSheet("font-size:13px; color:#666; font-style:italic;")
        layout.addWidget(subtitle)

        # ── Bannière théorie ──────────────────────────────────────
        theory = QFrame()
        theory.setStyleSheet(
            "background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px;"
        )
        tl = QHBoxLayout(theory)
        tl.setContentsMargins(16, 12, 16, 12)
        tl.setSpacing(24)
        for formula, desc in [
            ("ri",       "Date d'arrivée de la tâche"),
            ("di",       "Fenêtre d'exécution (jours)"),
            ("Di = ri+di","Deadline absolue"),
            ("Us = Cs/ds","Facteur de charge sporadique"),
            ("ΣU+Us ≤ 1","Test d'acceptation (Liu & Layland)"),
        ]:
            box = QVBoxLayout()
            f_lbl = QLabel(formula)
            f_lbl.setStyleSheet(
                "font-family:Courier New; font-size:14px; font-weight:bold; "
                "color:#1E40AF;"
            )
            f_lbl.setAlignment(Qt.AlignCenter)
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("font-size:10px; color:#666;")
            d_lbl.setAlignment(Qt.AlignCenter)
            box.addWidget(f_lbl)
            box.addWidget(d_lbl)
            tl.addLayout(box)
            if formula != "ΣU+Us ≤ 1":
                sep = QFrame()
                sep.setFrameShape(QFrame.VLine)
                sep.setStyleSheet("color:#BFDBFE;")
                tl.addWidget(sep)
        layout.addWidget(theory)

        # ── KPI cards ─────────────────────────────────────────────
        kpi = QHBoxLayout()
        self._stat_total     = self._make_kpi("Total",          "0", "#3B82F6")
        self._stat_pending   = self._make_kpi("En attente",     "0", "#F59E0B")
        self._stat_scheduled = self._make_kpi("Planifiées",     "0", "#10B981")
        self._stat_urgent    = self._make_kpi("Deadline ≤ 7j",  "0", "#EF4444")
        for card in [self._stat_total, self._stat_pending,
                     self._stat_scheduled, self._stat_urgent]:
            kpi.addWidget(card)
        layout.addLayout(kpi)

        # ── Barre d'actions ───────────────────────────────────────
        bar = QHBoxLayout()
        bar.setSpacing(10)

        self._cohort_filter = QComboBox()
        self._cohort_filter.setFixedHeight(36)
        self._cohort_filter.setMinimumWidth(200)
        self._cohort_filter.currentIndexChanged.connect(self._refresh_table)
        bar.addWidget(QLabel("Cohorte :"))
        bar.addWidget(self._cohort_filter)
        bar.addStretch()

        btn_new = QPushButton("➕  Nouvelle tâche sporadique")
        btn_new.setFixedHeight(38)
        btn_new.setStyleSheet(
            "background:#1a73e8; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 16px;"
        )
        btn_new.clicked.connect(self._on_new_task)
        bar.addWidget(btn_new)

        btn_test = QPushButton("🔬  Tester acceptation")
        btn_test.setFixedHeight(38)
        btn_test.setStyleSheet(
            "background:#7C3AED; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 16px;"
        )
        btn_test.clicked.connect(self._on_test_acceptance)
        bar.addWidget(btn_test)

        btn_plan = QPushButton("🚀  Planifier (EDF)")
        btn_plan.setFixedHeight(38)
        btn_plan.setStyleSheet(
            "background:#10B981; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 16px;"
        )
        btn_plan.clicked.connect(self._on_plan_task)
        bar.addWidget(btn_plan)

        btn_del = QPushButton("🗑️  Supprimer")
        btn_del.setFixedHeight(38)
        btn_del.setStyleSheet(
            "background:#EF4444; color:white; border-radius:6px; "
            "font-weight:bold; padding:0 16px;"
        )
        btn_del.clicked.connect(self._on_delete_task)
        bar.addWidget(btn_del)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setFixedWidth(40)
        btn_refresh.setStyleSheet(
            "background:#F3F4F6; border-radius:6px; font-size:16px;"
        )
        btn_refresh.clicked.connect(self._load_data)
        bar.addWidget(btn_refresh)

        layout.addLayout(bar)

        # ── Légende ───────────────────────────────────────────────
        leg = QHBoxLayout()
        for color, label in [
            ("#FEE2E2", "🔴 Deadline ≤ 3 jours"),
            ("#FEF3C7", "🟡 Deadline ≤ 7 jours"),
            ("#F0FDF4", "🟢 Deadline > 7 jours"),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"background:{color}; padding:3px 10px; border-radius:4px; "
                "font-size:11px;"
            )
            leg.addWidget(lbl)
        leg.addStretch()
        layout.addLayout(leg)

        # ── Table ─────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels([
            "ID", "Nom", "Type", "Cohorte", "Enseignant",
            "Arrivée (ri)", "Deadline (Di)", "Fenêtre (di)",
            "Volume", "Statut"
        ])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        for i in [0, 2, 5, 6, 7, 8, 9]:
            self._table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeToContents
            )
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget { border:1px solid #E5E7EB; border-radius:8px; }
            QHeaderView::section {
                background:#F9FAFB; font-weight:bold; padding:8px;
                border:none; border-bottom:1px solid #E5E7EB;
            }
            QTableWidget::item { padding:6px; }
        """)
        layout.addWidget(self._table)

    def _make_kpi(self, label, value, color):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background:{color}; border-radius:12px; }}"
        )
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        val_lbl = QLabel(value)
        val_lbl.setObjectName("val")
        val_lbl.setStyleSheet(
            "font-size:28px; font-weight:bold; color:white;"
        )
        val_lbl.setAlignment(Qt.AlignCenter)
        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet("font-size:12px; color:white;")
        lbl_lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(val_lbl)
        v.addWidget(lbl_lbl)
        return frame

    def _set_kpi(self, card, value):
        for child in card.findChildren(QLabel):
            if child.objectName() == "val":
                child.setText(str(value))

    def _get_selected_task(self):
        """Retourne la tâche sélectionnée dans la table, ou None."""
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Sélection requise",
                "Veuillez sélectionner une tâche dans la liste.")
            return None
        task_id = int(self._table.item(rows[0].row(), 0).text())
        task = self.session.query(AcademicActivityModel).get(task_id)
        return task

    # ── Actions ───────────────────────────────────────────────────

    def _on_new_task(self):
        """Ouvre le dialogue de création d'une tâche sporadique."""
        if not self._cohorts:
            QMessageBox.warning(self, "Erreur",
                "Aucune cohorte disponible. Créez d'abord une cohorte.")
            return

        dialog = SporadicTaskDialog(self._cohorts, self._teachers, parent=self)
        if dialog.exec_() != QDialog.Accepted:
            return

        values = dialog.get_values()
        try:
            # Vérifier unicité du code
            existing = self.session.query(AcademicActivityModel).filter_by(
                code=values['code']
            ).first()
            if existing:
                QMessageBox.warning(self, "Code dupliqué",
                    f"Le code '{values['code']}' est déjà utilisé.")
                return

            task = AcademicActivityModel(
                name             = values['name'],
                code             = values['code'],
                type             = values['type'],
                volume_hours     = values['volume_hours'],
                hours_done       = 0.0,
                charge_factor    = 0.0,
                cohort_id        = values['cohort_id'],
                teacher_id       = values['teacher_id'],
                is_sporadic      = True,
                arrival_date     = values['arrival_date'],
                execution_window = values['execution_window'],
                priority         = PriorityEnum.URGENTE,
                status           = ActivityStatusEnum.PENDING,
            )
            self.session.add(task)
            self.session.commit()

            deadline = values['arrival_date'] + timedelta(days=values['execution_window'])
            QMessageBox.information(
                self, "Tâche créée",
                "Tâche sporadique créée avec succès.\n\n"
                + "Nom : " + values['name'] + "\n"
                + "Deadline : " + deadline.strftime("%d/%m/%Y") + "\n\n"
                "Lancez le test d'acceptation avant de planifier."
            )
            self._load_data()

        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erreur", "Création échouée :\n" + str(e))

    def _on_test_acceptance(self):
        """Lance le test d'acceptation de Liu & Layland sur la tâche sélectionnée."""
        task = self._get_selected_task()
        if not task:
            return
        if not task.is_sporadic:
            QMessageBox.warning(self, "Erreur",
                "Cette tâche n'est pas marquée comme sporadique.")
            return

        # Période de référence : aujourd'hui → deadline
        if not task.arrival_date or not task.execution_window:
            QMessageBox.warning(self, "Données manquantes",
                "La tâche doit avoir une date d'arrivée et une fenêtre d'exécution.")
            return

        try:
            scheduler   = PfairScheduler(self.session)
            start_date  = task.arrival_date
            deadline    = task.arrival_date + timedelta(days=task.execution_window)
            result      = scheduler.accept_sporadic_task(task.id, start_date, deadline)

            # Affichage du résultat
            if result['accepted']:
                icon = "✅"
                color_title = "Tâche acceptée"
            else:
                icon = "❌"
                color_title = "Tâche refusée"

            msg = (
                icon + "  " + color_title + "\n\n"
                "═══ Résultat du test Liu & Layland ═══\n\n"
                "Tâche : " + task.name + "\n"
                "Deadline : " + deadline.strftime("%d/%m/%Y") + "\n"
                "Fenêtre ouvrable : " + str(result.get('d_window', '?')) + " jours\n\n"
                "ΣU périodiques  : " + str(result['u_periodic_sum']) + "\n"
                "Us (sporadique) : " + str(result['u_sporadic']) + "\n"
                "─────────────────────────────────\n"
                "U total         : " + str(result['u_total']) + " (seuil : 1.0)\n"
                "Capacité résid. : " + str(result['residual_capacity']) + "\n\n"
                + result['reason']
            )
            if result['accepted']:
                QMessageBox.information(self, color_title, msg)
            else:
                QMessageBox.warning(self, color_title, msg)

        except Exception as e:
            QMessageBox.critical(self, "Erreur test", str(e))

    def _on_plan_task(self):
        """Planifie la tâche sporadique sélectionnée via EDF."""
        task = self._get_selected_task()
        if not task:
            return
        if not task.is_sporadic:
            QMessageBox.warning(self, "Erreur",
                "Cette tâche n'est pas marquée comme sporadique.")
            return
        if task.status == ActivityStatusEnum.COMPLETED:
            QMessageBox.information(self, "Déjà terminée",
                "Cette tâche est déjà marquée comme terminée.")
            return
        if not task.arrival_date or not task.execution_window:
            QMessageBox.warning(self, "Données manquantes",
                "La tâche doit avoir une date d'arrivée et une fenêtre d'exécution.")
            return

        deadline = task.arrival_date + timedelta(days=task.execution_window)

        reply = QMessageBox.question(
            self, "Confirmer la planification",
            "Planifier la tâche sporadique ?\n\n"
            + "• " + task.name + "\n"
            + "• Arrivée : " + str(task.arrival_date) + "\n"
            + "• Deadline : " + deadline.strftime("%d/%m/%Y") + "\n\n"
            "Le test d'acceptation sera relancé automatiquement.",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        try:
            scheduler = PfairScheduler(self.session)
            result    = scheduler.schedule_sporadic_task(
                activity_id     = task.id,
                start_date      = task.arrival_date,
                end_date        = deadline,
                available_rooms = None
            )

            if result['success']:
                icon = "⚠️" if result.get('partial') else "✅"
                msg = (
                    icon + "  Planification terminée\n\n"
                    + result['message'] + "\n\n"
                    "Créneaux planifiés : " + str(result['scheduled_slots']) + "\n"
                    "Heures planifiées  : " + str(result['total_hours']) + "h\n"
                    "Conflits détectés  : " + str(result['conflicts']) + "\n"
                    "Deadline           : " + str(result['deadline'])
                )
                if result.get('partial'):
                    QMessageBox.warning(self, "Planification partielle", msg)
                else:
                    QMessageBox.information(self, "Planification réussie", msg)
            else:
                QMessageBox.warning(
                    self, "Planification refusée",
                    "La tâche ne peut pas être planifiée.\n\n"
                    + result.get('reason', '—')
                )
            self._load_data()

        except Exception as e:
            QMessageBox.critical(self, "Erreur planification", str(e))

    def _on_delete_task(self):
        """Supprime la tâche sporadique sélectionnée."""
        task = self._get_selected_task()
        if not task:
            return

        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            "Supprimer cette tâche sporadique ?\n\n"
            + "• " + task.name + " (" + task.code + ")\n\n"
            "Tous les créneaux associés seront également supprimés.\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.session.delete(task)
            self.session.commit()
            QMessageBox.information(
                self, "Tâche supprimée",
                "La tâche '" + task.name + "' a été supprimée."
            )
            self._load_data()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erreur", "Suppression échouée :\n" + str(e))

    def showEvent(self, event):
        super().showEvent(event)
        self._load_data()