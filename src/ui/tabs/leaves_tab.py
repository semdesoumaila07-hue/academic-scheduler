"""
<<<<<<< HEAD
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
=======
Onglet Congés - PyQt5 - VERSION AMÉLIORÉE
UC4: Déclarer les disponibilités
Gestion des demandes de congé et indisponibilités
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QDialog,
    QLineEdit, QComboBox, QMessageBox, QFormLayout, QTextEdit,
    QDateEdit, QCalendarWidget, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
import json
from pathlib import Path
from datetime import datetime, timedelta


class LeavesTab(QWidget):
    """Onglet de gestion des congés et disponibilités - VERSION AMÉLIORÉE."""
    
    def __init__(self):
        super().__init__()
        
        # Données
        self.data = {
            "demandes": [],
            "enseignants": []
        }
        
        self.load_data()
        self.load_teachers()
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # ==========================================
        # EN-TÊTE
        # ==========================================
        header_layout = QVBoxLayout()
        
        title = QLabel("Gestion des Congés")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("UC4 - Déclarer les disponibilités et gérer les demandes de congé")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # ==========================================
        # ONGLETS
        # ==========================================
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #F5F5F5;
                color: #666;
                padding: 12px 30px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1976D2;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #E3F2FD;
            }
        """)
        
        # Créer les onglets
        self.tab_demandes = self.create_demandes_tab()
        self.tab_calendrier = self.create_calendrier_tab()
        
        self.tab_widget.addTab(self.tab_demandes, "📋 Demandes de congé")
        self.tab_widget.addTab(self.tab_calendrier, "📅 Calendrier")
        
        layout.addWidget(self.tab_widget)
        
        # ==========================================
        # STATISTIQUES EN BAS
        # ==========================================
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        self.stat_total = self.create_stat_box("Total demandes", "0", "#3498db")
        self.stat_pending = self.create_stat_box("En attente", "0", "#f39c12")
        self.stat_approved = self.create_stat_box("Approuvées", "0", "#27ae60")
        self.stat_rejected = self.create_stat_box("Refusées", "0", "#e74c3c")
        
        self.stats_layout.addWidget(self.stat_total)
        self.stats_layout.addWidget(self.stat_pending)
        self.stats_layout.addWidget(self.stat_approved)
        self.stats_layout.addWidget(self.stat_rejected)
        
        layout.addLayout(self.stats_layout)
        
        # Mettre à jour les stats initiales
        self.update_statistics()
    
    # ==========================================
    # ONGLET DEMANDES
    # ==========================================
    
    def create_demandes_tab(self):
        """Crée l'onglet des demandes."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
<<<<<<< HEAD

        actions_layout = QHBoxLayout()
        self._count_label = QLabel("Demandes de congé")
        self._count_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        actions_layout.addWidget(self._count_label)
        actions_layout.addStretch()

        filter_label = QLabel("Statut :")
        filter_label.setStyleSheet("font-weight: bold;")
        actions_layout.addWidget(filter_label)

=======
        
        # Barre d'actions
        actions_layout = QHBoxLayout()
        
        # Compteur
        count = len(self.data["demandes"])
        title = QLabel(f"Demandes de congé ({count})")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        actions_layout.addWidget(title)
        
        actions_layout.addStretch()
        
        # Filtres
        filter_label = QLabel("Statut :")
        filter_label.setStyleSheet("font-weight: bold;")
        actions_layout.addWidget(filter_label)
        
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tous", "En attente", "Approuvée", "Refusée"])
        self.filter_combo.setFixedHeight(35)
        self.filter_combo.currentTextChanged.connect(self.refresh_demandes_table)
        actions_layout.addWidget(self.filter_combo)
<<<<<<< HEAD

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
=======
        
        # Bouton Nouvelle demande
        btn_add = QPushButton("➕ Nouvelle demande")
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_add.clicked.connect(self.add_leave_request)  # ✅ DÉJÀ CONNECTÉ
        actions_layout.addWidget(btn_add)
        
        layout.addLayout(actions_layout)
        
        # Tableau
        self.table_demandes = self.create_table()
        layout.addWidget(self.table_demandes)
        
        self.refresh_demandes_table()
        
        return widget
    
    def create_table(self):
        """Crée le tableau des demandes."""
        table = QTableWidget()
        headers = ["Enseignant", "Type", "Date début", "Date fin", "Jours", "Statut", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Style moderne
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
                color: #333;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        
        # Configuration
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        table.setColumnWidth(6, 150)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        return table
    
    def refresh_demandes_table(self):
        """Rafraîchir le tableau des demandes."""
        self.table_demandes.setRowCount(0)
        
        # Filtre
        filtre = self.filter_combo.currentText()
        
        filtered_count = 0
        
        for demande in self.data["demandes"]:
            # Appliquer le filtre
            if filtre != "Tous" and demande.get('statut') != filtre:
                continue
            
            filtered_count += 1
            row = self.table_demandes.rowCount()
            self.table_demandes.insertRow(row)
            
            # Enseignant
            enseignant_nom = demande.get('enseignant_nom', 'N/A')
            self.table_demandes.setItem(row, 0, QTableWidgetItem(enseignant_nom))
            
            # Type
            self.table_demandes.setItem(row, 1, QTableWidgetItem(demande.get('type', 'N/A')))
            
            # Date début
            self.table_demandes.setItem(row, 2, QTableWidgetItem(demande.get('date_debut', 'N/A')))
            
            # Date fin
            self.table_demandes.setItem(row, 3, QTableWidgetItem(demande.get('date_fin', 'N/A')))
            
            # Nombre de jours
            self.table_demandes.setItem(row, 4, QTableWidgetItem(str(demande.get('nb_jours', 0))))
            
            # Statut avec couleur
            statut = demande.get('statut', 'N/A')
            statut_item = QTableWidgetItem(statut)
            if statut == "En attente":
                statut_item.setBackground(QColor('#FFF3C7'))
                statut_item.setForeground(QColor('#F57C00'))
            elif statut == "Approuvée":
                statut_item.setBackground(QColor('#E8F5E9'))
                statut_item.setForeground(QColor('#2E7D32'))
            elif statut == "Refusée":
                statut_item.setBackground(QColor('#FFEBEE'))
                statut_item.setForeground(QColor('#C62828'))
            self.table_demandes.setItem(row, 5, statut_item)
            
            # Actions
            actions_widget = self.create_action_buttons(demande)
            self.table_demandes.setCellWidget(row, 6, actions_widget)
        
        # Mettre à jour le compteur
        self.tab_widget.setTabText(0, f"📋 Demandes de congé ({filtered_count})")
    
    def create_action_buttons(self, demande):
        """Crée les boutons d'action."""
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
<<<<<<< HEAD
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

=======
        
        statut = demande.get('statut')
        
        # Bouton Détails
        btn_details = QPushButton("👁️")
        btn_details.setFixedSize(30, 30)
        btn_details.setCursor(Qt.PointingHandCursor)
        btn_details.setToolTip("Voir les détails")
        btn_details.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                border-radius: 5px;
            }
        """)
        btn_details.clicked.connect(lambda: self.view_details(demande))
        layout.addWidget(btn_details)
        
        # Si en attente, ajouter boutons Approuver/Refuser
        if statut == "En attente":
            # Bouton Approuver
            btn_approve = QPushButton("✅")
            btn_approve.setFixedSize(30, 30)
            btn_approve.setCursor(Qt.PointingHandCursor)
            btn_approve.setToolTip("Approuver")
            btn_approve.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E8F5E9;
                    border-radius: 5px;
                }
            """)
            btn_approve.clicked.connect(lambda: self.approve_request(demande))
            layout.addWidget(btn_approve)
            
            # Bouton Refuser
            btn_reject = QPushButton("❌")
            btn_reject.setFixedSize(30, 30)
            btn_reject.setCursor(Qt.PointingHandCursor)
            btn_reject.setToolTip("Refuser")
            btn_reject.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #FFEBEE;
                    border-radius: 5px;
                }
            """)
            btn_reject.clicked.connect(lambda: self.reject_request(demande))
            layout.addWidget(btn_reject)
        
        # Bouton Supprimer
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(30, 30)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
                border-radius: 5px;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_request(demande))
        layout.addWidget(btn_delete)
        
        layout.addStretch()
        return widget
    
    # ==========================================
    # ONGLET CALENDRIER
    # ==========================================
    
    def create_calendrier_tab(self):
        """Crée l'onglet calendrier."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Info
        info_label = QLabel("📅 Visualisation des congés sur le calendrier académique")
        info_label.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 20px;")
        layout.addWidget(info_label)
        
        # Calendrier
        calendar = QCalendarWidget()
        calendar.setMinimumHeight(400)
        calendar.setStyleSheet("""
            QCalendarWidget QWidget {
                background-color: white;
            }
            QCalendarWidget QToolButton {
                color: #1a1a1a;
                background-color: white;
                border: none;
                font-size: 14px;
                padding: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #E3F2FD;
                border-radius: 4px;
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #1976D2;
                selection-color: white;
            }
        """)
        layout.addWidget(calendar)
        
        # Légende
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        legend_layout = QHBoxLayout(legend_frame)
        
        legend_label = QLabel("Légende :")
        legend_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        legend_layout.addWidget(legend_label)
        
        # En attente
        pending_box = QWidget()
        pending_box.setFixedSize(20, 20)
        pending_box.setStyleSheet("background: #f39c12; border-radius: 4px;")
        legend_layout.addWidget(pending_box)
        legend_layout.addWidget(QLabel("En attente"))
        
        # Approuvée
        approved_box = QWidget()
        approved_box.setFixedSize(20, 20)
        approved_box.setStyleSheet("background: #27ae60; border-radius: 4px;")
        legend_layout.addWidget(approved_box)
        legend_layout.addWidget(QLabel("Approuvée"))
        
        # Refusée
        rejected_box = QWidget()
        rejected_box.setFixedSize(20, 20)
        rejected_box.setStyleSheet("background: #e74c3c; border-radius: 4px;")
        legend_layout.addWidget(rejected_box)
        legend_layout.addWidget(QLabel("Refusée"))
        
        legend_layout.addStretch()
        
        layout.addWidget(legend_frame)
        
        return widget
    
    # ==========================================
    # FONCTIONS CRUD
    # ==========================================
    
    def add_leave_request(self):
        """Ajouter une demande de congé."""
        # Vérifier qu'il y a des enseignants
        if not self.data["enseignants"]:
            # Créer des enseignants exemple
            reply = QMessageBox.question(
                self,
                "Aucun enseignant",
                "Aucun enseignant trouvé dans le système.\n\n"
                "Voulez-vous utiliser des enseignants exemple pour tester ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.create_sample_teachers()
            else:
                QMessageBox.information(
                    self,
                    "Information",
                    "Veuillez d'abord créer des enseignants dans l'onglet 'Enseignants'."
                )
                return
        
        dialog = LeaveRequestDialog(self, self.data["enseignants"])
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            result["id"] = f"leave_{len(self.data['demandes']) + 1}_{datetime.now().timestamp()}"
            result["statut"] = "En attente"
            result["date_creation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.data["demandes"].append(result)
            self.save_data()
            self.refresh_demandes_table()
            self.update_statistics()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Demande de congé enregistrée !\n\n"
                f"Enseignant : {result['enseignant_nom']}\n"
                f"Du {result['date_debut']} au {result['date_fin']}\n"
                f"Durée : {result['nb_jours']} jour(s)\n\n"
                f"Le responsable pédagogique sera notifié pour validation."
            )
    
    def view_details(self, demande):
        """Voir les détails d'une demande."""
        dialog = LeaveDetailsDialog(self, demande)
        dialog.exec_()
    
    def approve_request(self, demande):
        """Approuver une demande."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Approuver la demande de congé de {demande.get('enseignant_nom')} ?\n\n"
            f"Du {demande.get('date_debut')} au {demande.get('date_fin')}\n"
            f"Durée : {demande.get('nb_jours')} jour(s)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            demande["statut"] = "Approuvée"
            demande["date_validation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            demande["validateur"] = "Responsable Pédagogique"
            
            self.save_data()
            self.refresh_demandes_table()
            self.update_statistics()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Demande approuvée !\n\n"
                f"L'enseignant {demande.get('enseignant_nom')} sera notifié."
            )
    
    def reject_request(self, demande):
        """Refuser une demande."""
        # Demander une justification
        dialog = JustificationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            justification = dialog.get_justification()
            
            demande["statut"] = "Refusée"
            demande["date_validation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            demande["validateur"] = "Responsable Pédagogique"
            demande["justification_refus"] = justification
            
            self.save_data()
            self.refresh_demandes_table()
            self.update_statistics()
            
            QMessageBox.information(
                self,
                "Succès",
                f"❌ Demande refusée.\n\n"
                f"L'enseignant {demande.get('enseignant_nom')} sera notifié avec la justification."
            )
    
    def delete_request(self, demande):
        """Supprimer une demande."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer la demande de {demande.get('enseignant_nom')} ?\n\n"
            f"Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data["demandes"].remove(demande)
            self.save_data()
            self.refresh_demandes_table()
            self.update_statistics()
            QMessageBox.information(self, "Succès", "✅ Demande supprimée !")
    
    # ==========================================
    # STATISTIQUES
    # ==========================================
    
    def create_stat_box(self, label, value, color):
        """Crée une boîte de statistique."""
        box = QWidget()
        box.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
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
    
    def update_stat_box(self, box, value):
        """Mettre à jour une boîte de statistique."""
        labels = box.findChildren(QLabel)
        if labels:
            labels[0].setText(value)
    
    def update_statistics(self):
        """Mettre à jour les statistiques."""
        total = len(self.data["demandes"])
        pending = len([d for d in self.data["demandes"] if d.get('statut') == 'En attente'])
        approved = len([d for d in self.data["demandes"] if d.get('statut') == 'Approuvée'])
        rejected = len([d for d in self.data["demandes"] if d.get('statut') == 'Refusée'])
        
        self.update_stat_box(self.stat_total, str(total))
        self.update_stat_box(self.stat_pending, str(pending))
        self.update_stat_box(self.stat_approved, str(approved))
        self.update_stat_box(self.stat_rejected, str(rejected))
    
    # ==========================================
    # PERSISTANCE
    # ==========================================
    
    def load_data(self):
        """Charger les données."""
        data_file = Path("data/leaves.json")
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data["demandes"] = loaded_data.get("demandes", [])
            except Exception as e:
                print(f"Erreur de chargement: {e}")
    
    def load_teachers(self):
        """Charger les enseignants."""
        # Essayer plusieurs sources
        teachers_file = Path("data/teachers.json")
        if teachers_file.exists():
            try:
                with open(teachers_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data["enseignants"] = loaded_data.get("enseignants", [])
                    if self.data["enseignants"]:
                        return
            except Exception as e:
                print(f"Erreur de chargement teachers: {e}")
        
        # Si pas d'enseignants, créer des exemples
        if not self.data["enseignants"]:
            self.create_sample_teachers()
    
    def create_sample_teachers(self):
        """Créer des enseignants exemple."""
        self.data["enseignants"] = [
            {'id': 1, 'nom': 'KABORE', 'prenom': 'Marie'},
            {'id': 2, 'nom': 'TRAORE', 'prenom': 'Moussa'},
            {'id': 3, 'nom': 'SAWADOGO', 'prenom': 'Fatimata'},
            {'id': 4, 'nom': 'OUATTARA', 'prenom': 'Ibrahim'},
            {'id': 5, 'nom': 'ZONGO', 'prenom': 'Aminata'}
        ]
    
    def save_data(self):
        """Sauvegarder les données."""
        data_file = Path("data/leaves.json")
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder: {e}")


# ==========================================
# DIALOGUES
# ==========================================

class LeaveRequestDialog(QDialog):
    """Dialogue pour créer une demande de congé."""
    
    def __init__(self, parent, enseignants):
        super().__init__(parent)
        self.enseignants = enseignants
        
        self.setWindowTitle("Nouvelle demande de congé")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("📝 Nouvelle demande de congé")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        
        subtitle = QLabel("Remplissez le formulaire ci-dessous")
        subtitle.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Enseignant
        self.enseignant_combo = QComboBox()
        enseignant_labels = [f"{e.get('nom', '')} {e.get('prenom', '')}" for e in self.enseignants]
        self.enseignant_combo.addItems(enseignant_labels)
        self.enseignant_combo.setFixedHeight(40)
        form.addRow("Enseignant *:", self.enseignant_combo)
        
        # Type de congé
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Congé annuel",
            "Mission",
            "Congé maladie prévu",
            "Formation",
            "Congé sans solde",
            "Autre"
        ])
        self.type_combo.setFixedHeight(40)
        form.addRow("Type de congé *:", self.type_combo)
        
        # Date début
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())
        self.date_debut.setFixedHeight(40)
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
<<<<<<< HEAD
        self.date_debut.dateChanged.connect(self._calc_days)

=======
        self.date_debut.dateChanged.connect(self.calculate_days)
        form.addRow("Date début *:", self.date_debut)
        
        # Date fin
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate().addDays(1))
        self.date_fin.setFixedHeight(40)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
<<<<<<< HEAD
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
=======
        self.date_fin.dateChanged.connect(self.calculate_days)
        form.addRow("Date fin *:", self.date_fin)
        
        # Nombre de jours (calculé automatiquement)
        self.nb_jours_label = QLabel("1 jour(s)")
        self.nb_jours_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db;")
        form.addRow("Durée :", self.nb_jours_label)
        
        # Justification
        self.justification_input = QTextEdit()
        self.justification_input.setPlaceholderText("Motif de la demande (optionnel)")
        self.justification_input.setFixedHeight(100)
        form.addRow("Justification:", self.justification_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.setFixedSize(140, 45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(180, 45)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
        # Calculer les jours initialement
        self.calculate_days()
    
    def calculate_days(self):
        """Calculer le nombre de jours."""
        debut = self.date_debut.date()
        fin = self.date_fin.date()
        
        if fin >= debut:
            nb_jours = debut.daysTo(fin) + 1
            self.nb_jours_label.setText(f"{nb_jours} jour(s)")
        else:
            self.nb_jours_label.setText("⚠️ Date invalide")
            self.nb_jours_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
    
    def validate_and_accept(self):
        """Valider et accepter."""
        debut = self.date_debut.date()
        fin = self.date_fin.date()
        
        if fin < debut:
            QMessageBox.warning(
                self,
                "Dates invalides",
                "La date de fin doit être après ou égale à la date de début !"
            )
            return
        
        self.accept()
    
    def get_data(self):
        """Retourne les données."""
        enseignant_label = self.enseignant_combo.currentText()
        enseignant_id = None
        for e in self.enseignants:
            if f"{e.get('nom', '')} {e.get('prenom', '')}" == enseignant_label:
                enseignant_id = e.get('id')
                break
        
        debut = self.date_debut.date()
        fin = self.date_fin.date()
        nb_jours = debut.daysTo(fin) + 1
        
        return {
            "enseignant_id": enseignant_id,
            "enseignant_nom": enseignant_label,
            "type": self.type_combo.currentText(),
            "date_debut": debut.toString("yyyy-MM-dd"),
            "date_fin": fin.toString("yyyy-MM-dd"),
            "nb_jours": nb_jours,
            "justification": self.justification_input.toPlainText().strip()
        }


class LeaveDetailsDialog(QDialog):
    """Dialogue pour afficher les détails d'une demande."""
    
    def __init__(self, parent, demande):
        super().__init__(parent)
        self.demande = demande
        
        self.setWindowTitle("Détails de la demande")
        self.setMinimumWidth(500)
        self.setMinimumHeight(550)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("📋 Détails de la demande")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Informations
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #F5F5F5;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)
        
        # Enseignant
        self.add_info_row(info_layout, "Enseignant", self.demande.get('enseignant_nom', 'N/A'))
        
        # Type
        self.add_info_row(info_layout, "Type de congé", self.demande.get('type', 'N/A'))
        
        # Dates
        self.add_info_row(info_layout, "Date début", self.demande.get('date_debut', 'N/A'))
        self.add_info_row(info_layout, "Date fin", self.demande.get('date_fin', 'N/A'))
        self.add_info_row(info_layout, "Durée", f"{self.demande.get('nb_jours', 0)} jour(s)")
        
        # Statut
        statut = self.demande.get('statut', 'N/A')
        statut_label = QLabel(statut)
        if statut == "En attente":
            statut_label.setStyleSheet("background: #f39c12; color: white; padding: 8px 20px; border-radius: 6px; font-weight: bold;")
        elif statut == "Approuvée":
            statut_label.setStyleSheet("background: #27ae60; color: white; padding: 8px 20px; border-radius: 6px; font-weight: bold;")
        elif statut == "Refusée":
            statut_label.setStyleSheet("background: #e74c3c; color: white; padding: 8px 20px; border-radius: 6px; font-weight: bold;")
        
        statut_row = QHBoxLayout()
        statut_row.addWidget(QLabel("Statut:"))
        statut_row.addWidget(statut_label)
        statut_row.addStretch()
        info_layout.addLayout(statut_row)
        
        # Justification
        if self.demande.get('justification'):
            justif_label = QLabel("Justification:")
            justif_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            info_layout.addWidget(justif_label)
            
            justif_text = QLabel(self.demande.get('justification'))
            justif_text.setWordWrap(True)
            justif_text.setStyleSheet("background: white; padding: 10px; border-radius: 5px;")
            info_layout.addWidget(justif_text)
        
        # Si refusée, afficher la justification du refus
        if statut == "Refusée" and self.demande.get('justification_refus'):
            refus_label = QLabel("❌ Motif du refus:")
            refus_label.setStyleSheet("color: #e74c3c; font-weight: bold; margin-top: 15px;")
            info_layout.addWidget(refus_label)
            
            refus_text = QLabel(self.demande.get('justification_refus'))
            refus_text.setWordWrap(True)
            refus_text.setStyleSheet("background: #FFEBEE; padding: 10px; border-radius: 5px; color: #C62828;")
            info_layout.addWidget(refus_text)
        
        layout.addWidget(info_frame)
        layout.addStretch()
        
        # Bouton Fermer
        btn_close = QPushButton("Fermer")
        btn_close.setFixedSize(140, 45)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
    
    def add_info_row(self, layout, label, value):
        """Ajouter une ligne d'information."""
        row = QHBoxLayout()
        
        label_widget = QLabel(f"{label}:")
        label_widget.setStyleSheet("font-weight: bold; color: #666; min-width: 120px;")
        row.addWidget(label_widget)
        
        value_widget = QLabel(str(value))
        value_widget.setWordWrap(True)
        value_widget.setStyleSheet("color: #1a1a1a;")
        row.addWidget(value_widget)
        
        row.addStretch()
        layout.addLayout(row)


class JustificationDialog(QDialog):
    """Dialogue pour saisir une justification de refus."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setWindowTitle("Justification du refus")
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("❌ Motif du refus")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(title)
        layout.addSpacing(10)
        
        # Message
        info = QLabel("Veuillez fournir une justification pour le refus de cette demande :")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(info)
        layout.addSpacing(15)
        
        # Zone de texte
        self.justification_input = QTextEdit()
        self.justification_input.setPlaceholderText("Saisissez le motif du refus...")
        self.justification_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #e74c3c;
            }
        """)
        layout.addWidget(self.justification_input)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Confirmer le refus")
        btn_ok.setFixedSize(180, 45)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_ok.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valider et accepter."""
        if not self.justification_input.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Justification requise",
                "Veuillez saisir un motif pour le refus."
            )
            return
        self.accept()
    
    def get_justification(self):
        """Retourne la justification."""
        return self.justification_input.toPlainText().strip()
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
