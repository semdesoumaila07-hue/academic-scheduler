<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Fenetre de connexion multi-roles
Systeme d'Ordonnancement Academique P-equitable
"""
import hashlib
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.database.db_manager import db_manager
from src.database.models import StudentModel, TeacherModel, UserModel

DEMO_ACCOUNTS = {
    "admin": ("admin", "admin"),
    "resp":  ("resp",  "responsable"),
    "responsable": ("resp", "responsable"),
}

def _authenticate(identifier, password):
    identifier = identifier.strip()
    if not identifier or not password:
        return None, None
    if identifier in DEMO_ACCOUNTS:
        pw_ok, role = DEMO_ACCOUNTS[identifier]
        if password == pw_ok:
            return role, {"name": identifier, "username": identifier, "role": role}
    try:
        session = db_manager.get_session()
        user = session.query(UserModel).filter(
            (UserModel.username == identifier) | (UserModel.email == identifier)
        ).first()
        if user and user.is_active:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash in (hashed, password):
                role_names = {getattr(r, 'name', '').lower() for r in getattr(user, 'roles', [])}
                if 'admin' in role_names or 'administrator' in role_names:
                    return 'admin', user
                elif any(x in role_names for x in ('pedagogical','responsable','responsible')):
                    return 'responsable', user
                elif 'teacher' in role_names:
                    return 'teacher_user', user
                return 'admin', user
        teacher = session.query(TeacherModel).filter(TeacherModel.email == identifier).first()
        if teacher:
            pw_check = teacher.email.split('@')[0].lower()
            if password.lower() in (pw_check, teacher.full_name.lower(), teacher.email.lower()):
                return 'teacher', teacher
        student = session.query(StudentModel).filter(
            (StudentModel.student_id == identifier) | (StudentModel.email == identifier)
        ).first()
        if student and password == student.student_id:
            return 'student', student
    except Exception as e:
        print(f"[login] Erreur: {e}")
    return None, None

class RoleCard(QFrame):
    def __init__(self, icon, title, desc, color, role_key, parent=None):
        super().__init__(parent)
        self._color = color
        self._role_key = role_key
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(66)
        self._style(False)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 6, 12, 6)
        lay.setSpacing(10)
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:24px; background:transparent; border:none;")
        ico.setFixedWidth(34)
        lay.addWidget(ico)
        txt = QVBoxLayout()
        txt.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"font-weight:bold; font-size:12px; color:{color}; background:transparent; border:none;")
        d = QLabel(desc)
        d.setStyleSheet("color:#888; font-size:9px; background:transparent; border:none;")
        txt.addWidget(t); txt.addWidget(d)
        lay.addLayout(txt)

    def _style(self, sel):
        b = self._color if sel else "#e0e0e0"
        bg = "#eef2ff" if sel else "white"
        self.setStyleSheet(f"QFrame{{background:{bg};border:2px solid {b};border-radius:9px;}}QFrame:hover{{border:2px solid {self._color};}}")

    def set_selected(self, s):
        self._style(s)


class LoginWindow(QMainWindow):
    ROLES_DEF = [
        ("👨\u200d💼", "Administrateur Académique",  "UC1 · UC2 · UC8 — Structure & Rapports",                 "#1565C0", "admin"),
        ("📋",          "Responsable Pédagogique",    "UC3 · UC5 · UC7 · UC10 — Activités & Ordonnancement",   "#2E7D32", "responsable"),
        ("👨\u200d🏫",  "Enseignant",                 "UC4 · UC9 — Disponibilités & Congés",                   "#E65100", "teacher"),
        ("🎓",          "Étudiant",                   "UC6 · UC7 — Emploi du temps & Retards académiques",     "#6A1B9A", "student"),
    ]
    ID_HINTS = {
        "admin":       ("Nom d'utilisateur ou email",  "Mot de passe"),
        "responsable": ("Nom d'utilisateur ou email",  "Mot de passe"),
        "teacher":     ("Email enseignant",            "Partie avant @ (ex: jean.dupont)"),
        "student":     ("Matricule ou email",          "Votre matricule (ex: ETU2025001)"),
    }

    def __init__(self):
        super().__init__()
        self._auth_role = None
        self._auth_object = None
        self._cards = []
        self._selected_role = None
        self._build()

    def _build(self):
        self.setWindowTitle("Ordonnancement Academique P-equitable — Connexion")
        self.setFixedSize(500, 650)
        central = QWidget()
        central.setStyleSheet("background:#1a237e;")
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(30, 26, 30, 26)
        outer.setSpacing(14)

        t = QLabel("🎓 Ordonnancement P-équitable")
        t.setFont(QFont("Arial", 16, QFont.Bold))
        t.setStyleSheet("color:white;")
        t.setAlignment(Qt.AlignCenter)
        outer.addWidget(t)
        s = QLabel("Système de Planification Pfair — Université")
        s.setStyleSheet("color:#90caf9; font-size:10px;")
        s.setAlignment(Qt.AlignCenter)
        outer.addWidget(s)

        card = QFrame()
        card.setStyleSheet("QFrame{background:white;border-radius:14px;}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(10)

        rl = QLabel("Mon profil :")
        rl.setStyleSheet("font-weight:bold; font-size:13px; color:#222;")
        cl.addWidget(rl)

        for icon, title, desc, color, key in self.ROLES_DEF:
            rc = RoleCard(icon, title, desc, color, key)
            rc.mousePressEvent = lambda e, k=key: self._on_role(k)
            self._cards.append(rc)
            cl.addWidget(rc)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#e8e8e8;")
        cl.addWidget(sep)

        id_lbl = QLabel("Identifiant :")
        id_lbl.setStyleSheet("font-size:12px; color:#444;")
        cl.addWidget(id_lbl)
        self._id = QLineEdit()
        self._id.setPlaceholderText("Selectionnez votre profil ci-dessus")
        self._id.setFixedHeight(37)
        self._id.setStyleSheet("QLineEdit{border:1px solid #ddd;border-radius:6px;padding:0 11px;font-size:12px;background:#f9f9f9;}QLineEdit:focus{border:2px solid #1a73e8;background:white;}")
        cl.addWidget(self._id)

        pw_lbl = QLabel("Mot de passe :")
        pw_lbl.setStyleSheet("font-size:12px; color:#444;")
        cl.addWidget(pw_lbl)
        self._pw = QLineEdit()
        self._pw.setEchoMode(QLineEdit.Password)
        self._pw.setPlaceholderText("Mot de passe")
        self._pw.setFixedHeight(37)
        self._pw.setStyleSheet("QLineEdit{border:1px solid #ddd;border-radius:6px;padding:0 11px;font-size:12px;background:#f9f9f9;}QLineEdit:focus{border:2px solid #1a73e8;background:white;}")
        self._pw.returnPressed.connect(self._login)
        cl.addWidget(self._pw)

        self._btn = QPushButton("🔐  Se connecter")
        self._btn.setFixedHeight(42)
        self._btn.setStyleSheet("QPushButton{background:#1a73e8;color:white;border-radius:8px;font-size:13px;font-weight:bold;}QPushButton:hover{background:#1557b0;}QPushButton:disabled{background:#9e9e9e;}")
        self._btn.clicked.connect(self._login)
        cl.addWidget(self._btn)

        self._err = QLabel("")
        self._err.setStyleSheet("color:#c62828; font-size:11px;")
        self._err.setAlignment(Qt.AlignCenter)
        self._err.setVisible(False)
        cl.addWidget(self._err)

        outer.addWidget(card)

        hint = QLabel("💡 Admin: admin/admin   Resp: resp/resp   Enseignant: email/partie-avant-@   Etudiant: matricule/matricule")
        hint.setStyleSheet("color:#90caf9; font-size:9px;")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        outer.addWidget(hint)

    def _on_role(self, key):
        self._selected_role = key
        for rc in self._cards:
            rc.set_selected(rc._role_key == key)
        id_h, pw_h = self.ID_HINTS.get(key, ("Identifiant","Mot de passe"))
        self._id.setPlaceholderText(id_h)
        self._pw.setPlaceholderText(pw_h)
        self._id.setFocus()

    def _login(self):
        ident = self._id.text().strip()
        pw    = self._pw.text()
        if not ident or not pw:
            self._show_err("Remplissez tous les champs.")
            return
        self._btn.setEnabled(False)
        self._btn.setText("Verification...")
        self._err.setVisible(False)
        role, obj = _authenticate(ident, pw)
        if role and obj:
            self._auth_role   = role
            self._auth_object = obj
            self.close()
        else:
            self._show_err("Identifiant ou mot de passe incorrect.")
            self._btn.setEnabled(True)
            self._btn.setText("🔐  Se connecter")

    def _show_err(self, msg):
        self._err.setText("⚠️  " + msg)
        self._err.setVisible(True)

    def get_role(self):   return self._auth_role
    def get_object(self): return self._auth_object


def show_login_window():
    db_manager.initialize()
    db_manager.create_tables()
    app = QApplication.instance()
    win = LoginWindow()
    win.show()
    app.exec_()
    return win.get_role(), win.get_object()
=======
"""
Interface de connexion et sélection des rôles.

Affiche les rôles disponibles avec des descriptions et icônes,
puis ouvre un dialogue de connexion pour le rôle choisi.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGridLayout, QLabel, QLineEdit, QDialog, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from pathlib import Path

from ..services.auth_service import authenticate, get_teacher_for_user
from ..database.db_manager import db_manager
from ..database.repositories import StudentRepository
from .widgets.student_dashboard import StudentDashboard
from .widgets.teacher_dashboard import TeacherDashboard


class LoginDialog(QDialog):
    """Dialogue de connexion username/password."""
    
    login_successful = pyqtSignal(object)  # Émet l'objet user
    
    def __init__(self, role_name: str, parent=None):
        super().__init__(parent)
        self.role_name = role_name
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'Connexion - {self.role_name}')
        self.setGeometry(400, 300, 400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }
            QPushButton#ok {
                background-color: #4CAF50;
            }
            QPushButton#ok:hover {
                background-color: #45a049;
            }
            QPushButton#cancel {
                background-color: #f44336;
            }
            QPushButton#cancel:hover {
                background-color: #da190b;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel(f'Connexion - {self.role_name}')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Username
        layout.addWidget(QLabel('Nom d\'utilisateur:'))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Entrez votre nom d\'utilisateur')
        layout.addWidget(self.username_input)
        
        # Password
        layout.addWidget(QLabel('Mot de passe:'))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Entrez votre mot de passe')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton('Connexion')
        ok_btn.setObjectName('ok')
        ok_btn.clicked.connect(self.attempt_login)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setObjectName('cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Erreur', 'Veuillez remplir tous les champs')
            return
        
        user = authenticate(username, password)
        
        if user:
            self.user = user
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(self, 'Erreur', 'Identifiants invalides')


class RoleCard(QPushButton):
    """Carte visuelle d'un rôle avec icône, titre et description."""
    
    def __init__(self, role_name: str, description: str, icon_text: str = '👤', border_color: str = '#2196F3'):
        super().__init__()
        self.role_name = role_name
        self.description = description
        self.icon_text = icon_text
        self.border_color = border_color
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_font = QFont()
        icon_font.setPointSize(40)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Role name
        name_label = QLabel(role_name)
        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #1a3a52;")
        layout.addWidget(name_label)
        
        # Description
        desc_label = QLabel(description)
        desc_font = QFont()
        desc_font.setPointSize(10)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666;")
        layout.addWidget(desc_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(220)
        self.setMinimumHeight(240)
        
        # Style avec bordure top colorée
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-top: 4px solid {border_color};
                border-radius: 8px;
                text-align: top;
            }}
            QPushButton:hover {{
                background-color: #f9f9f9;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)


class LoginWindow(QMainWindow):
    """Fenêtre d'accueil avec sélection des rôles et connexion."""
    
    user_authenticated = pyqtSignal(object)  # Émet l'objet user
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.selected_role = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Système d\'Ordonnancement Académique - Connexion')
        self.setGeometry(50, 50, 1400, 850)
        
        # Widget central avec fond bleu
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #2c5aa0;
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre de navigation
        navbar = self.create_navbar()
        main_layout.addWidget(navbar)
        
        # Contenu principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2c5aa0;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c5aa0;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #1a3a52;
                border-radius: 5px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #2c5aa0;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre principal
        main_title = QLabel('Choisissez votre rôle pour vous connecter')
        main_title_font = QFont()
        main_title_font.setPointSize(20)
        main_title_font.setBold(True)
        main_title.setFont(main_title_font)
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("color: white; margin-bottom: 20px;")
        content_layout.addWidget(main_title)
        
        # Grille de rôles - première rangée
        roles_layout_1 = QHBoxLayout()
        roles_layout_1.setSpacing(20)
        
        roles_part1 = [
            {
                'name': 'Administrateur',
                'description': 'Gestion complète du système',
                'icon': '👨‍💼',
                'color': '#FF6B6B'
            },
            {
                'name': 'Responsable pédagogique',
                'description': 'Gestion des activités et ordonnancement',
                'icon': '👨‍🏫',
                'color': '#4ECDC4'
            },
            {
                'name': 'Enseignant',
                'description': 'Consultation des emplois du temps',
                'icon': '👩‍🎓',
                'color': '#45B7D1'
            },
        ]
        
        for role_info in roles_part1:
            card = RoleCard(role_info['name'], role_info['description'], role_info['icon'], role_info['color'])
            card.clicked.connect(lambda checked=False, r=role_info['name']: self.on_role_selected(r))
            roles_layout_1.addWidget(card)
        
        content_layout.addLayout(roles_layout_1)
        
        # Grille de rôles - deuxième rangée
        roles_layout_2 = QHBoxLayout()
        roles_layout_2.setSpacing(20)
        
        roles_part2 = [
            {
                'name': 'Maître de discipline',
                'description': 'Surveillance et discipline',
                'icon': '👮',
                'color': '#FFA500'
            },
            {
                'name': 'Comptable',
                'description': 'Gestion financière',
                'icon': '💰',
                'color': '#E74C3C'
            },
            {
                'name': 'Étudiant',
                'description': 'Consultation des notes',
                'icon': '🎓',
                'color': '#9B59B6'
            },
        ]
        
        for role_info in roles_part2:
            card = RoleCard(role_info['name'], role_info['description'], role_info['icon'], role_info['color'])
            card.clicked.connect(lambda checked=False, r=role_info['name']: self.on_role_selected(r))
            roles_layout_2.addWidget(card)
        
        content_layout.addLayout(roles_layout_2)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_navbar(self):
        """Crée la barre de navigation."""
        navbar = QWidget()
        navbar.setStyleSheet("""
            QWidget {
                background-color: #1a3a52;
                padding: 10px 20px;
            }
        """)
        navbar.setFixedHeight(60)
        
        layout = QHBoxLayout(navbar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo/Titre
        logo_label = QLabel('🏛️ Système d\'Ordonnancement Académique')
        logo_font = QFont()
        logo_font.setPointSize(14)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet("color: white;")
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        # Menu items
        menu_items = ['Accueil', 'Programmes', 'Témoignages', 'Contact']
        for item in menu_items:
            menu_label = QLabel(item)
            menu_font = QFont()
            menu_font.setPointSize(11)
            menu_label.setFont(menu_font)
            menu_label.setStyleSheet("""
                color: #ecf0f1;
                padding: 5px 15px;
            """)
            layout.addWidget(menu_label)
        
        return navbar
    
    def on_role_selected(self, role_name: str):
        """Ouverture du dialogue de connexion pour le rôle sélectionné."""
        # garder le rôle sélectionné pour comportement post-login
        self.selected_role = role_name
        dialog = LoginDialog(role_name, self)
        dialog.login_successful.connect(self.on_login_successful)
        dialog.exec_()
    
    def on_login_successful(self, user):
        """Appelé quand l'authentification réussit."""
        self.current_user = user
        self.user_authenticated.emit(user)
        try:
            # Étudiant : ouvrir le tableau de bord étudiant
            if self.selected_role and 'etud' in self.selected_role.lower():
                session = db_manager.get_session()
                try:
                    repo = StudentRepository(session)
                    student = repo.get_by_email(user.email)
                finally:
                    session.close()
                if student:
                    self.dashboard = StudentDashboard(student)
                    self.dashboard.show()
                else:
                    QMessageBox.information(
                        self, 'Profil étudiant',
                        'Aucun profil étudiant trouvé pour cet utilisateur.'
                    )
            # Enseignant : ouvrir le tableau de bord enseignant
            elif self.selected_role and 'enseignant' in self.selected_role.lower():
                teacher = get_teacher_for_user(user)
                if teacher:
                    self.dashboard = TeacherDashboard(teacher)
                    self.dashboard.show()
                else:
                    QMessageBox.information(
                        self, 'Profil enseignant',
                        'Aucun profil enseignant trouvé pour cet utilisateur '
                        '(vérifiez que l’email correspond à un enseignant ou liez le compte).'
                    )
        except Exception as e:
            import logging, traceback
            logging.exception('Erreur lors de l\'ouverture du tableau de bord')
            QMessageBox.critical(self, 'Erreur', f"Une erreur est survenue lors de l'ouverture du tableau de bord:\n{e}")
            return

        # Masquer la fenêtre de connexion mais garder la référence au dashboard
        try:
            self.hide()
        except Exception:
            pass
    
    def get_authenticated_user(self):
        """Retourne l'utilisateur authentifié."""
        return self.current_user


def show_login_window():
    """Lance la fenêtre de login et retourne l'utilisateur authentifié."""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    db_manager.initialize()
    db_manager.create_tables()
    
    login_window = LoginWindow()
    login_window.show()
    
    # Boucle pour attendre la connexion
    if app.exec_() == 0:
        return login_window.get_authenticated_user()
    
    return None
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
