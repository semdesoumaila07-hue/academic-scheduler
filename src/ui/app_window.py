# -*- coding: utf-8 -*-
"""
app_window.py — Fenetre principale de l'application
Chemin : src/ui/app_window.py

L'application se lance directement (sans popup de connexion).
L'onglet "Connexion / Mon Compte" est toujours visible dans la sidebar.
Apres connexion, les onglets metier apparaissent selon le role.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from src.ui.notification_panel import BellButton
from PyQt5.QtGui import QFont

from src.database.db_manager import db_manager


# ─── Mapping roles → indices onglets autorises ────────────────────────────────
# Index dans TAB_CLASSES :
# 0=Dashboard  1=Structure  2=Enseignants  3=Activites  4=Calendrier
# 5=Conges     6=Ordonnancement  7=Retards  8=Rapports  9=Emplois_temps
# 10=Disponibilites

ROLE_ALLOWED = {
    'admin':      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],   # tout + sporadiques
    'responsable': [0, 3, 4, 5, 6, 7, 9, 13],             # UC3 UC5 UC7 UC10 + sporadiques
    'teacher':     [0, 5, 7, 9, 10],
    'teacher_user':[0, 5, 7, 9, 10],
    'Enseignant':          [0, 5, 7, 9, 10],
    'Teacher':             [0, 5, 7, 9, 10],
    'student':     [],                                     # → StudentWindow dédié
}

ROLE_COLORS = {
    'admin':       "#1565C0",
    'responsable': "#2E7D32",
    'teacher':     "#E65100",
    'student':     "#6A1B9A",
}

ROLE_LABELS = {
    'admin':       ("👨\u200d💼", "Administrateur Académique"),
    'responsable': ("📋",         "Responsable Pédagogique"),
    'teacher':     ("👨\u200d🏫", "Enseignant"),
    'student':     ("🎓",         "Étudiant"),
}


class AppWindow(QMainWindow):
    """
    Fenetre principale.
    - Lance directement, sans popup
    - Barre laterale avec onglet Connexion toujours visible
    - Apres login, affiche les onglets selon le role
    """

    def __init__(self):
        super().__init__()
        self._user      = None
        self._role      = ''
        self._nav_btns  = []          # boutons sidebar metier
        self._auth_btn  = None        # bouton sidebar connexion/compte
        self._content   = None        # QStackedWidget zone droite
        self._tab_refs  = []          # [(logic_index, widget)]

        self.setWindowTitle("Système d'Ordonnancement Académique P-équitable")
        self.setMinimumSize(1280, 800)
        self._build_ui()
        self.center()
        self._inactivity_timer = QTimer(self)
        self._inactivity_timer.setInterval(60000)
        self._inactivity_timer.timeout.connect(self._check_inactivity)
        self._inactivity_minutes = 0
        self._warning_shown = False

    # ══════════════════════════════════════════════════════════════════════════
    # Construction UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # En-tete
        root.addWidget(self._make_header())

        # Corps : sidebar + contenu
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._sidebar = self._make_sidebar()
        body.addWidget(self._sidebar)

        self._content = QStackedWidget()
        self._content.setStyleSheet("background: white;")
        body.addWidget(self._content, 1)

        root.addLayout(body, 1)

        # Barre de statut
        sb = QStatusBar()
        sb.setStyleSheet("background:#f9fafb; border-top:1px solid #e5e7eb; color:#6b7280; font-size:11px; padding:0 16px;")
        sb.showMessage("Système d'Ordonnancement Académique P-équitable v1.0.0")
        self.setStatusBar(sb)

        # Charger l'ecran de connexion au demarrage
        self._show_auth_screen()

    def _make_header(self):
        bar = QFrame()
        bar.setFixedHeight(64)
        bar.setStyleSheet("background:white; border-bottom:1px solid #e5e7eb;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(24, 0, 24, 0)

        ico = QLabel("📊")
        ico.setStyleSheet("font-size:28px;")
        lay.addWidget(ico)

        txt = QVBoxLayout()
        txt.setSpacing(1)
        t = QLabel("Pfair Scheduler")
        t.setStyleSheet("font-size:17px; font-weight:700; color:#1f2937;")
        s = QLabel("Ordonnancement académique P-équitable")
        s.setStyleSheet("font-size:11px; color:#6b7280;")
        txt.addWidget(t); txt.addWidget(s)
        lay.addLayout(txt)
        lay.addStretch()

        # Badge utilisateur (mis a jour apres connexion)
        self._bell = None  # sera cree apres connexion
        self._bell_container = QWidget()
        self._bell_layout = QHBoxLayout(self._bell_container)
        self._bell_layout.setContentsMargins(0,0,0,0)
        lay.addWidget(self._bell_container)
        self._user_badge = QLabel("Non connecté")
        self._user_badge.setStyleSheet("color:#6b7280; font-size:12px;")
        lay.addWidget(self._user_badge)

        return bar

    def _make_sidebar(self):
        sb = QFrame()
        sb.setFixedWidth(245)
        sb.setStyleSheet("background:#f9fafb; border-right:1px solid #e5e7eb;")

        self._sb_layout = QVBoxLayout(sb)
        self._sb_layout.setContentsMargins(0, 16, 0, 16)
        self._sb_layout.setSpacing(4)

        # Titre sidebar
        title = QLabel("  Navigation")
        title.setStyleSheet("color:#9ca3af; font-size:11px; font-weight:600; padding:0 16px 8px;")
        self._sb_layout.addWidget(title)

        # Bouton Connexion/Compte (toujours present)
        self._auth_btn = self._make_nav_btn("🔐", "Connexion / Compte", -1)
        self._auth_btn.clicked.connect(self._goto_auth)
        self._sb_layout.addWidget(self._auth_btn)

        self._separator = self._make_separator()
        self._sb_layout.addWidget(self._separator)
        self._separator.setVisible(False)

        # Zone onglets metier (vide au demarrage)
        self._metier_container = QWidget()
        self._metier_layout = QVBoxLayout(self._metier_container)
        self._metier_layout.setContentsMargins(0, 0, 0, 0)
        self._metier_layout.setSpacing(4)
        self._sb_layout.addWidget(self._metier_container)

        self._sb_layout.addStretch()

        # Bouton deconnexion (bas de sidebar)
        self._logout_btn = QPushButton("  🚪  Se déconnecter")
        self._logout_btn.setFixedHeight(40)
        self._logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #ef4444;
                border: 1px solid #fca5a5; border-radius: 8px;
                margin: 0 12px; font-size: 12px; text-align: left;
                padding-left: 12px;
            }
            QPushButton:hover { background: #fef2f2; }
        """)
        self._logout_btn.clicked.connect(self._logout)
        self._logout_btn.setVisible(False)
        self._sb_layout.addWidget(self._logout_btn)

        return sb

    def _make_nav_btn(self, icon, label, idx):
        btn = QPushButton(f"  {icon}  {label}")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("active", False)
        btn.setStyleSheet(self._btn_style(False))
        return btn

    def _make_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#e5e7eb; margin:4px 12px;")
        return sep

    # ══════════════════════════════════════════════════════════════════════════
    # Gestion auth
    # ══════════════════════════════════════════════════════════════════════════

    def _show_auth_screen(self):
        """Affiche l'ecran connexion/inscription dans la zone contenu."""
        from src.ui.tabs.auth_tab import AuthTab
        # Verifier si deja cree
        for i in range(self._content.count()):
            w = self._content.widget(i)
            if hasattr(w, '_is_auth_tab'):
                self._content.setCurrentWidget(w)
                self._set_active_btn(self._auth_btn)
                return

        auth = AuthTab()
        auth._is_auth_tab = True
        auth.user_changed.connect(self._on_user_changed)
        self._content.addWidget(auth)
        self._content.setCurrentWidget(auth)
        self._set_active_btn(self._auth_btn)

    def _on_user_changed(self, user_obj, role_str):
        """Appele quand l'utilisateur se connecte ou se deconnecte."""
        if user_obj is None:
            # Deconnexion
            self._logout()
        else:
            self._user = user_obj
            self._role = role_str
            self._apply_role(role_str, user_obj)

    def _apply_role(self, role_str, user_obj):
        """Construit les onglets metier selon le role et affiche le dashboard."""
        # Mettre a jour le badge header
        name = self._get_name(user_obj)
        icon, label = ROLE_LABELS.get(role_str, ("👤", "Utilisateur"))
        color = ROLE_COLORS.get(role_str, "#555")
        self._user_badge.setText(f"{icon}  {name}  |  {label}")
        self._user_badge.setStyleSheet(f"color:{color}; font-size:12px; font-weight:bold;")

        # Mettre a jour le bouton auth
        self._auth_btn.setText(f"  👤  Mon Compte")
        self._auth_btn.setStyleSheet(self._btn_style(False, color))

        # Afficher separateur et bouton logout
        self._separator.setVisible(True)
        self._logout_btn.setVisible(True)
        self._inactivity_minutes = 0
        self._warning_shown = False
        self._inactivity_timer.start()
        # Ajouter cloche notifications
        if hasattr(user_obj, "id") and user_obj.id:
            from src.ui.notification_panel import BellButton
            # Supprimer ancienne cloche
            for i in reversed(range(self._bell_layout.count())):
                w = self._bell_layout.itemAt(i).widget()
                if w: w.deleteLater()
            self._bell = BellButton(user_obj.id)
            self._bell_layout.addWidget(self._bell)

        # Si etudiant → fenetre dediee
        if role_str == 'student':
            self._open_student_window(user_obj)
            return

        # Supprimer anciens onglets metier
        self._clear_metier_tabs()

        # Construire nouveaux onglets selon le role
        self._build_metier_tabs(role_str, user_obj)

        # Aller sur le premier onglet metier (Dashboard)
        if self._tab_refs:
            first_widget = self._tab_refs[0][1]
            self._content.setCurrentWidget(first_widget)
            self._set_active_btn(self._nav_btns[0] if self._nav_btns else self._auth_btn)

    def _clear_metier_tabs(self):
        """Supprime tous les onglets metier existants."""
        for _, widget in self._tab_refs:
            self._content.removeWidget(widget)
            widget.deleteLater()
        self._tab_refs.clear()

        for btn in self._nav_btns:
            self._metier_layout.removeWidget(btn)
            btn.deleteLater()
        self._nav_btns.clear()

    def _build_metier_tabs(self, role_str, user_obj):
        """Instancie les onglets metier pour le role donne."""
        from src.ui.main_window import TAB_CLASSES
        from src.services.permissions_config import TAB_ITEMS

        allowed = ROLE_ALLOWED.get(role_str, list(range(len(TAB_CLASSES))))

        # Trouver ActivitiesTab d'abord
        activities_tab_instance = None
        widgets_to_add = []

        for logic_idx in allowed:
            if logic_idx >= len(TAB_CLASSES):
                continue
            # Trouver le label
            label = "Onglet"
            icon  = "📋"
            for item in TAB_ITEMS:
                if item[0] == logic_idx:
                    icon  = item[2]
                    label = item[3]
                    break

            tab_class = TAB_CLASSES[logic_idx]
            try:
                if tab_class.__name__ == 'ActivitiesTab':
                    w = tab_class(current_user=user_obj)
                    activities_tab_instance = w
                elif tab_class.__name__ == 'TeachersTab':
                    w = tab_class(activities_tab=activities_tab_instance)
                elif tab_class.__name__ == 'LeavesTab':
                    # Pour les enseignants (TeacherModel sans roles),
                    # passer current_user=None afin d'utiliser _submit_leave_direct
                    # qui bypass le décorateur @require_permission
                    cu = user_obj if hasattr(user_obj, 'roles') else None
                    w = tab_class(current_user=cu)
                elif tab_class.__name__ == 'SchedulingTab':
                    w = tab_class()
                else:
                    w = tab_class()
            except Exception as e:
                print(f"[AppWindow] Erreur instanciation {tab_class.__name__}: {e}")
                continue

            widgets_to_add.append((logic_idx, icon, label, w))

        # Ajouter au contenu et a la sidebar
        for logic_idx, icon, label, w in widgets_to_add:
            self._content.addWidget(w)
            self._tab_refs.append((logic_idx, w))

            btn = self._make_nav_btn(icon, label, logic_idx)
            final_widget = w
            final_btn = btn
            btn.clicked.connect(lambda checked=False, fw=final_widget, fb=final_btn: self._switch_tab(fw, fb))
            self._nav_btns.append(btn)
            self._metier_layout.addWidget(btn)

    def _switch_tab(self, widget, btn):
        self._content.setCurrentWidget(widget)
        self._set_active_btn(btn)

    def _goto_auth(self):
        self._show_auth_screen()

    def _logout(self):
        self._user = None
        self._role = ''
        self._user_badge.setText("Non connecté")
        self._user_badge.setStyleSheet("color:#6b7280; font-size:12px;")
        self._auth_btn.setText("  🔐  Connexion / Compte")
        self._auth_btn.setStyleSheet(self._btn_style(False))
        self._separator.setVisible(False)
        self._logout_btn.setVisible(False)
        self._inactivity_timer.stop()
        self._inactivity_minutes = 0
        if self._bell:
            self._bell.hide()
            self._bell = None
        self._clear_metier_tabs()
        self._show_auth_screen()

    def _open_student_window(self, student):
        """Ouvre la fenetre dediee aux etudiants."""
        try:
            from src.ui.student_window import StudentWindow
            self._student_win = StudentWindow(student)
            self._student_win.show()
        except Exception as e:
            print(f"[AppWindow] Erreur StudentWindow: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # Utilitaires
    # ══════════════════════════════════════════════════════════════════════════


    def _reset_inactivity(self):
        self._inactivity_minutes = 0
        self._warning_shown = False

    def _check_inactivity(self):
        if self._user is None:
            return
        self._inactivity_minutes += 1
        remaining = 5 - self._inactivity_minutes
        if self._inactivity_minutes >= 3 and not self._warning_shown:
            self._warning_shown = True
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Inactivite detectee")
            msg.setText(f"Vous serez deconnecte dans {remaining} minute(s).\nCliquez OK pour rester connecte.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            self._reset_inactivity()
        elif self._inactivity_minutes >= 5:
            self._inactivity_timer.stop()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Session expiree", "Deconnecte automatiquement pour inactivite.")
            self._logout()

    def mousePressEvent(self, event):
        self._reset_inactivity()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self._reset_inactivity()
        super().keyPressEvent(event)

    def _set_active_btn(self, active_btn):
        all_btns = [self._auth_btn] + self._nav_btns
        for b in all_btns:
            b.setProperty("active", b is active_btn)
            role_color = ROLE_COLORS.get(self._role, "#1a73e8")
            b.setStyleSheet(self._btn_style(b is active_btn, role_color))

    def _btn_style(self, active, color="#1a73e8"):
        if active:
            return f"""
                QPushButton {{
                    background: {color}18;
                    color: {color};
                    border: none;
                    border-left: 3px solid {color};
                    border-radius: 0;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                    padding: 0 16px;
                }}
            """
        return """
            QPushButton {
                background: transparent;
                color: #374151;
                border: none;
                font-size: 13px;
                text-align: left;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #f3f4f6;
                color: #111827;
            }
        """

    def _get_name(self, obj):
        if hasattr(obj, 'full_name') and obj.full_name:
            return obj.full_name
        if hasattr(obj, 'username') and obj.username:
            return obj.username
        if isinstance(obj, dict):
            return obj.get('name', 'Utilisateur')
        return 'Utilisateur'

    def center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())