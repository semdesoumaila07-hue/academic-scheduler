# -*- coding: utf-8 -*-
"""
auth_tab.py — Onglet Connexion / Inscription / Mon Compte
Chemin : src/ui/tabs/auth_tab.py

Fonctionnalites :
  - Connexion avec email + mot de passe
  - Création de compte avec choix de role
  - Affichage du profil quand connecte
  - Deconnexion
  - Signal user_changed emis vers AppWindow pour mise a jour des onglets
"""
import hashlib
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QComboBox, QStackedWidget,
    QFormLayout, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.database.db_manager import db_manager
from src.database.models import UserModel, StudentModel, TeacherModel, RoleModel


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _get_or_create_role(session, role_name: str) -> RoleModel:
    """Recupere ou cree un role par son nom."""
    role = session.query(RoleModel).filter_by(name=role_name).first()
    if not role:
        role = RoleModel(name=role_name, description=f"Role {role_name}")
        session.add(role)
        session.flush()
    return role


# ─── Styles communs ──────────────────────────────────────────────────────────

CARD_STYLE = """
    QFrame#card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 14px;
    }
"""

INPUT_STYLE = """
    QLineEdit, QComboBox {
        border: 1px solid #ddd;
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
        background: #f9f9f9;
        min-height: 18px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #1a73e8;
        background: white;
    }
"""

BTN_PRIMARY = """
    QPushButton {
        background: #1a73e8;
        color: white;
        border-radius: 8px;
        font-size: 13px;
        font-weight: bold;
        padding: 10px 0;
    }
    QPushButton:hover { background: #1557b0; }
    QPushButton:disabled { background: #9e9e9e; }
"""

BTN_SECONDARY = """
    QPushButton {
        background: white;
        color: #1a73e8;
        border: 2px solid #1a73e8;
        border-radius: 8px;
        font-size: 12px;
        padding: 8px 0;
    }
    QPushButton:hover { background: #e8f0fe; }
"""

BTN_DANGER = """
    QPushButton {
        background: #d32f2f;
        color: white;
        border-radius: 8px;
        font-size: 13px;
        font-weight: bold;
        padding: 10px 20px;
    }
    QPushButton:hover { background: #b71c1c; }
"""


# ─── Panneau Connexion ────────────────────────────────────────────────────────

class LoginPanel(QWidget):
    """Formulaire de connexion."""
    login_success = pyqtSignal(object, str)  # (user_object, role_str)
    goto_register = pyqtSignal()

    ROLE_MAP = {
        'admin':        ['Admin', 'Administrator', 'admin'],
        'responsable':  ['Pedagogical', 'Responsable', 'pedagogical', 'responsable'],
        'teacher':      ['Teacher', 'Enseignant', 'teacher'],
        'student':      [],  # géré séparément via StudentModel
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 20, 0, 20)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(CARD_STYLE)
        card.setFixedWidth(420)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(30, 28, 30, 28)
        cl.setSpacing(14)

        # Titre
        t = QLabel("🔐 Connexion")
        t.setFont(QFont("Arial", 18, QFont.Bold))
        t.setStyleSheet("color: #1a237e;")
        t.setAlignment(Qt.AlignCenter)
        cl.addWidget(t)

        sub = QLabel("Entrez vos identifiants pour acceder au systeme")
        sub.setStyleSheet("color: #777; font-size: 11px;")
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Formulaire
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self._id = QLineEdit()
        self._id.setPlaceholderText("Votre email (ex: kabore.eric@univ.bf)")
        self._id.setStyleSheet(INPUT_STYLE)
        form.addRow("Email :", self._id)

        self._pw = QLineEdit()
        self._pw.setEchoMode(QLineEdit.Password)
        self._pw.setPlaceholderText("Votre mot de passe")
        self._pw.setStyleSheet(INPUT_STYLE)
        self._pw.returnPressed.connect(self._login)
        form.addRow("Mot de passe :", self._pw)

        cl.addLayout(form)

        self._err = QLabel("")
        self._err.setStyleSheet("color: #c62828; font-size: 11px;")
        self._err.setAlignment(Qt.AlignCenter)
        self._err.setVisible(False)
        cl.addWidget(self._err)

        btn = QPushButton("Se connecter")
        btn.setStyleSheet(BTN_PRIMARY)
        btn.clicked.connect(self._login)
        cl.addWidget(btn)

        sep = QLabel("─────────── ou ───────────")
        sep.setStyleSheet("color: #aaa; font-size: 11px;")
        sep.setAlignment(Qt.AlignCenter)
        cl.addWidget(sep)

        reg_btn = QPushButton("Créer un compte")
        reg_btn.setStyleSheet(BTN_SECONDARY)
        reg_btn.clicked.connect(self.goto_register.emit)
        cl.addWidget(reg_btn)

        outer.addWidget(card, alignment=Qt.AlignCenter)

    def _login(self):
        ident = self._id.text().strip()
        pw    = self._pw.text()

        if not ident or not pw:
            self._show_err("Remplissez tous les champs.")
            return

        try:
            session = db_manager.get_session()

            # ── 1. Chercher UserModel : email OU username (auto-généré depuis email) ──
            # Le username = partie avant @ de l'email (généré à l'inscription)
            user = session.query(UserModel).filter(
                (UserModel.email    == ident) |
                (UserModel.username == ident)
            ).first()

            if user:
                # Verifier blocage
                if getattr(user, "is_locked", False):
                    self._show_err("Compte bloque apres trop de tentatives. Contactez l administrateur.")
                    return
                if not user.is_active:
                    self._show_err("Compte desactive. Contactez l administrateur.")
                    return
                if user.password_hash == _hash(pw):
                    # Succes - reinitialiser compteur
                    user.login_attempts = 0
                    user.is_locked = False
                    session.commit()
                    role_names = {getattr(r, 'name', '').lower() for r in user.roles}
                    # Déterminer le rôle
                    if any(x in role_names for x in ('pedagogical','responsable','responsible')):
                        role_str = 'responsable'
                    elif any(x in role_names for x in ('teacher','enseignant')):
                        role_str = 'teacher'
                    elif any(x in role_names for x in ('student','etudiant')):
                        role_str = 'student'
                        # Retrouver le StudentModel lié par email
                        student = session.query(StudentModel).filter(
                            StudentModel.email == user.email
                        ).first()
                        if student:
                            self.login_success.emit(student, 'student')
                            self._id.clear(); self._pw.clear()
                            self._err.setVisible(False)
                            return
                    else:
                        role_str = 'admin'
                    self.login_success.emit(user, role_str)
                    self._id.clear(); self._pw.clear()
                    self._err.setVisible(False)
                    return

            # ── 2. Chercher étudiant par matricule ou email + mot de passe haché ──
            student = session.query(StudentModel).filter(
                (StudentModel.student_id == ident) |
                (StudentModel.email      == ident)
            ).first()
            if student:
                # Vérifier le mot de passe via UserModel lié au même email
                user_linked = session.query(UserModel).filter(
                    UserModel.email == student.email
                ).first()
                pw_ok = (user_linked and user_linked.password_hash == _hash(pw)) \
                        or (pw == student.student_id)   # fallback matricule
                if pw_ok:
                    self.login_success.emit(student, 'student')
                    self._id.clear(); self._pw.clear()
                    self._err.setVisible(False)
                    return

            # ── 3. Chercher enseignant par email ──
            teacher = session.query(TeacherModel).filter(
                TeacherModel.email == ident
            ).first()
            if teacher and pw == teacher.email.split('@')[0]:
                self.login_success.emit(teacher, 'teacher')
                self._id.clear(); self._pw.clear()
                self._err.setVisible(False)
                return

        except Exception as e:
            self._show_err(f"Erreur système : {e}")
            return

        # Compter echec si user trouve
        if "user" in dir() and user is not None:
            attempts = getattr(user, "login_attempts", 0) or 0
            attempts += 1
            user.login_attempts = attempts
            remaining = max(0, 3 - attempts)
            if attempts >= 3:
                user.is_locked = True
                from datetime import datetime
                user.locked_at = datetime.now()
                session.commit()
                self._show_err("Compte bloque apres 3 tentatives. Contactez l administrateur.")
                return
            else:
                session.commit()
                self._show_err(f"Mot de passe incorrect. {remaining} tentative(s) restante(s).")
                return
        self._show_err("Email ou mot de passe incorrect.")

    def _show_err(self, msg):
        self._err.setText("⚠️  " + msg)
        self._err.setVisible(True)


# ─── Panneau Inscription ──────────────────────────────────────────────────────

class RegisterPanel(QWidget):
    """Formulaire de creation de compte."""
    register_success = pyqtSignal(object, str)  # (user, role_str)
    goto_login       = pyqtSignal()

    ROLES = [
        ("Administrateur Académique",  "admin",       "👨‍💼"),
        ("Responsable Pédagogique",    "responsable", "📋"),
        ("Enseignant",                 "teacher",     "👨‍🏫"),
        ("Étudiant",                   "student",     "🎓"),
    ]

    # Correspondance role_str → nom dans la table roles
    ROLE_DB_NAMES = {
        'admin':       'Admin',
        'responsable': 'Pedagogical',
        'teacher':     'Teacher',
        'student':     'Student',
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        outer = QVBoxLayout(inner)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 20, 0, 30)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(CARD_STYLE)
        card.setFixedWidth(460)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(30, 26, 30, 26)
        cl.setSpacing(13)

        # Titre
        t = QLabel("📝 Créer un compte")
        t.setFont(QFont("Arial", 17, QFont.Bold))
        t.setStyleSheet("color: #1a237e;")
        t.setAlignment(Qt.AlignCenter)
        cl.addWidget(t)

        sub = QLabel("Remplissez le formulaire pour creer votre compte")
        sub.setStyleSheet("color: #777; font-size: 11px;")
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        # Champs
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self._name = QLineEdit()
        self._name.setPlaceholderText("Prénom et Nom")
        self._name.setStyleSheet(INPUT_STYLE)
        form.addRow("Nom complet * :", self._name)

        self._email = QLineEdit()
        self._email.setPlaceholderText("votre@email.com")
        self._email.setStyleSheet(INPUT_STYLE)
        form.addRow("Email * :", self._email)

        self._pw1 = QLineEdit()
        self._pw1.setEchoMode(QLineEdit.Password)
        self._pw1.setPlaceholderText("Minimum 6 caractères")
        self._pw1.setStyleSheet(INPUT_STYLE)
        form.addRow("Mot de passe * :", self._pw1)

        self._pw2 = QLineEdit()
        self._pw2.setEchoMode(QLineEdit.Password)
        self._pw2.setPlaceholderText("Répetez le mot de passe")
        self._pw2.setStyleSheet(INPUT_STYLE)
        self._pw2.returnPressed.connect(self._register)
        form.addRow("Confirmer * :", self._pw2)

        # Choix du rôle
        self._role_combo = QComboBox()
        self._role_combo.setStyleSheet(INPUT_STYLE)
        for label, key, icon in self.ROLES:
            self._role_combo.addItem(f"{icon}  {label}", userData=key)
        form.addRow("Mon rôle * :", self._role_combo)

        # Champs etudiant (matricule + cohorte) — visibles seulement si Etudiant
        self._matricule = QLineEdit()
        self._matricule.setPlaceholderText("ex: ETU2025001")
        self._matricule.setStyleSheet(INPUT_STYLE)
        self._mat_lbl = QLabel("Matricule * :")
        form.addRow(self._mat_lbl, self._matricule)

        self._cohort_combo = QComboBox()
        self._cohort_combo.setStyleSheet(INPUT_STYLE)
        self._cohort_lbl = QLabel("Cohorte * :")
        form.addRow(self._cohort_lbl, self._cohort_combo)

        cl.addLayout(form)

        # Masquer/afficher champs etudiant selon role
        self._role_combo.currentIndexChanged.connect(self._on_role_change)
        self._on_role_change(0)
        self._load_cohorts()

        self._err = QLabel("")
        self._err.setStyleSheet("color: #c62828; font-size: 11px;")
        self._err.setAlignment(Qt.AlignCenter)
        self._err.setWordWrap(True)
        self._err.setVisible(False)
        cl.addWidget(self._err)

        self._ok = QLabel("")
        self._ok.setStyleSheet("color: #2e7d32; font-size: 11px; font-weight: bold;")
        self._ok.setAlignment(Qt.AlignCenter)
        self._ok.setVisible(False)
        cl.addWidget(self._ok)

        btn = QPushButton("Créer mon compte")
        btn.setStyleSheet(BTN_PRIMARY)
        btn.clicked.connect(self._register)
        cl.addWidget(btn)

        back = QPushButton("← Retour à la connexion")
        back.setStyleSheet(BTN_SECONDARY)
        back.clicked.connect(self.goto_login.emit)
        cl.addWidget(back)

        outer.addWidget(card, alignment=Qt.AlignCenter)
        scroll.setWidget(inner)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

    def _on_role_change(self, idx):
        key = self._role_combo.itemData(idx)
        is_student = (key == 'student')
        self._mat_lbl.setVisible(is_student)
        self._matricule.setVisible(is_student)
        self._cohort_lbl.setVisible(is_student)
        self._cohort_combo.setVisible(is_student)

    def _load_cohorts(self):
        try:
            from src.database.models import CohortModel
            session = db_manager.get_session()
            cohorts = session.query(CohortModel).all()
            self._cohort_combo.clear()
            for c in cohorts:
                self._cohort_combo.addItem(f"{c.name} ({c.academic_year})", userData=c.id)
        except Exception:
            self._cohort_combo.addItem("Aucune cohorte disponible", userData=None)

    def _register(self):
        name     = self._name.text().strip()
        email    = self._email.text().strip()
        pw1      = self._pw1.text()
        pw2      = self._pw2.text()
        role_key = self._role_combo.currentData()

        # Générer username automatiquement depuis l'email (partie avant @)
        username = email.split('@')[0] if '@' in email else email

        # Validations
        if not all([name, email, pw1, pw2]):
            self._show_err("Tous les champs obligatoires (*) doivent être remplis.")
            return
        if '@' not in email:
            self._show_err("Adresse email invalide.")
            return
        if len(pw1) < 6:
            self._show_err("Le mot de passe doit contenir au moins 6 caractères.")
            return
        if pw1 != pw2:
            self._show_err("Les mots de passe ne correspondent pas.")
            return

        try:
            session = db_manager.get_session()

            # Vérifier doublons
            if session.query(UserModel).filter(
                (UserModel.username == username) | (UserModel.email == email)
            ).first():
                self._show_err("Ce nom d'utilisateur ou cet email est déjà utilisé.")
                return

            if role_key == 'student':
                # Créer un compte étudiant
                mat = self._matricule.text().strip()
                cohort_id = self._cohort_combo.currentData()
                if not mat:
                    self._show_err("Le matricule est obligatoire pour les étudiants.")
                    return
                if not cohort_id:
                    self._show_err("Sélectionnez une cohorte.")
                    return
                if session.query(StudentModel).filter_by(student_id=mat).first():
                    self._show_err("Ce matricule est déjà utilisé.")
                    return

                # Créer StudentModel + UserModel lié
                student = StudentModel(
                    full_name  = name,
                    student_id = mat,
                    email      = email,
                    cohort_id  = cohort_id,
                )
                session.add(student)

                # UserModel pour l'auth
                user = UserModel(
                    username      = username,
                    email         = email,
                    password_hash = _hash(pw1),
                    is_active     = True,
                )
                role_obj = _get_or_create_role(session, 'Student')
                user.roles.append(role_obj)
                session.add(user)
                session.commit()
                session.refresh(student)

                self._show_ok(f"✅ Compte créé ! Bienvenue {name}.")
                self.register_success.emit(student, 'student')

            else:
                # Créer UserModel standard
                user = UserModel(
                    username      = username,
                    email         = email,
                    password_hash = _hash(pw1),
                    is_active     = True,
                )
                db_role_name = self.ROLE_DB_NAMES.get(role_key, 'Admin')
                role_obj = _get_or_create_role(session, db_role_name)
                user.roles.append(role_obj)
                session.add(user)
                session.commit()
                session.refresh(user)

                self._show_ok(f"✅ Compte créé ! Bienvenue {name}.")
                self.register_success.emit(user, role_key)

        except Exception as e:
            self._show_err(f"Erreur : {e}")

    def _show_err(self, msg):
        self._err.setText("⚠️  " + msg)
        self._err.setVisible(True)
        self._ok.setVisible(False)

    def _show_ok(self, msg):
        self._ok.setText(msg)
        self._ok.setVisible(True)
        self._err.setVisible(False)


# ─── Panneau Profil (connecté) ────────────────────────────────────────────────

class ProfilePanel(QWidget):
    """Affichage du profil utilisateur connecte."""
    logout_requested = pyqtSignal()

    ROLE_LABELS = {
        'admin':       ("👨‍💼", "Administrateur Académique", "#1565C0"),
        'responsable': ("📋",   "Responsable Pédagogique",   "#2E7D32"),
        'teacher':     ("👨‍🏫", "Enseignant",                "#E65100"),
        'student':     ("🎓",   "Étudiant",                  "#6A1B9A"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user = None
        self._role = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 20, 0, 20)

        self._card = QFrame()
        self._card.setObjectName("card")
        self._card.setStyleSheet(CARD_STYLE)
        self._card.setFixedWidth(420)
        self._cl = QVBoxLayout(self._card)
        self._cl.setContentsMargins(30, 28, 30, 28)
        self._cl.setSpacing(16)

        # Avatar
        self._avatar = QLabel("?")
        self._avatar.setFixedSize(80, 80)
        self._avatar.setAlignment(Qt.AlignCenter)
        self._avatar.setStyleSheet("""
            QLabel {
                background: #1a73e8; color: white;
                border-radius: 40px; font-size: 32px; font-weight: bold;
            }
        """)
        self._cl.addWidget(self._avatar, alignment=Qt.AlignCenter)

        self._name_lbl = QLabel("")
        self._name_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        self._name_lbl.setStyleSheet("color: #1a1a1a;")
        self._name_lbl.setAlignment(Qt.AlignCenter)
        self._cl.addWidget(self._name_lbl)

        self._role_badge = QLabel("")
        self._role_badge.setFixedHeight(32)
        self._role_badge.setAlignment(Qt.AlignCenter)
        self._role_badge.setStyleSheet("border-radius:8px; font-size:13px; padding:4px 16px;")
        self._cl.addWidget(self._role_badge, alignment=Qt.AlignCenter)

        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("color:#666; font-size:12px;")
        self._info_lbl.setAlignment(Qt.AlignCenter)
        self._info_lbl.setWordWrap(True)
        self._cl.addWidget(self._info_lbl)

        # Acces
        access_frame = QFrame()
        access_frame.setStyleSheet("QFrame{background:#f5f5f5;border-radius:8px;padding:4px;}")
        af = QVBoxLayout(access_frame)
        self._access_lbl = QLabel("")
        self._access_lbl.setStyleSheet("color:#444; font-size:12px;")
        self._access_lbl.setWordWrap(True)
        af.addWidget(self._access_lbl)
        self._cl.addWidget(access_frame)

        logout_btn = QPushButton("🚪  Se déconnecter")
        logout_btn.setStyleSheet(BTN_DANGER)
        logout_btn.clicked.connect(self.logout_requested.emit)
        self._cl.addWidget(logout_btn)

        outer.addWidget(self._card, alignment=Qt.AlignCenter)

    def set_user(self, user_obj, role_str):
        self._user = user_obj
        self._role = role_str

        icon, label, color = self.ROLE_LABELS.get(role_str, ("👤","Utilisateur","#555"))

        # Nom
        if hasattr(user_obj, 'full_name'):
            name = user_obj.full_name
        elif hasattr(user_obj, 'username'):
            name = user_obj.username
        elif isinstance(user_obj, dict):
            name = user_obj.get('name', 'Utilisateur')
        else:
            name = str(user_obj)

        self._avatar.setText((name or "?")[0].upper())
        self._avatar.setStyleSheet(f"""
            QLabel {{
                background: {color}; color: white;
                border-radius: 40px; font-size: 32px; font-weight: bold;
            }}
        """)
        self._name_lbl.setText(name)
        self._role_badge.setText(f"{icon}  {label}")
        self._role_badge.setStyleSheet(f"""
            QLabel {{
                background: {color}22;
                color: {color};
                border: 1px solid {color};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 16px;
            }}
        """)

        # Email / Matricule
        if hasattr(user_obj, 'email'):
            self._info_lbl.setText(f"📧 {user_obj.email}")
        if hasattr(user_obj, 'student_id'):
            self._info_lbl.setText(
                f"📧 {user_obj.email}\n"
                f"🪪 Matricule : {user_obj.student_id}"
            )

        # Accès résumé
        access_map = {
            'admin':       "✅ Accès complet — UC1 UC2 UC3 UC5 UC7 UC8 UC9 UC10",
            'responsable': "✅ Activités · Ordonnancement · Retards · Congés · Emplois du temps",
            'teacher':     "✅ Disponibilités (UC4) · Soumettre congé (UC9)",
            'student':     "✅ Emploi du temps (UC6) · Retards académiques (UC7)",
        }
        self._access_lbl.setText(access_map.get(role_str, "✅ Accès standard"))


# ─── Onglet Auth principal ────────────────────────────────────────────────────

class AuthTab(QWidget):
    """
    Onglet Connexion / Mon Compte — a ajouter dans AppWindow.
    Emet user_changed(user_obj, role_str) quand l'utilisateur
    se connecte ou se deconnecte.
    """
    user_changed = pyqtSignal(object, str)   # (user_obj, role_str) ou (None, '')

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_user = None
        self._current_role = ''
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()

        # Page 0 : Connexion
        self._login_panel = LoginPanel()
        self._login_panel.login_success.connect(self._on_login)
        self._login_panel.goto_register.connect(lambda: self._stack.setCurrentIndex(1))
        self._stack.addWidget(self._login_panel)

        # Page 1 : Inscription
        self._reg_panel = RegisterPanel()
        self._reg_panel.register_success.connect(self._on_login)
        self._reg_panel.goto_login.connect(lambda: self._stack.setCurrentIndex(0))
        self._stack.addWidget(self._reg_panel)

        # Page 2 : Profil
        self._profile_panel = ProfilePanel()
        self._profile_panel.logout_requested.connect(self._on_logout)
        self._stack.addWidget(self._profile_panel)

        lay.addWidget(self._stack)

    def _on_login(self, user_obj, role_str):
        self._current_user = user_obj
        self._current_role = role_str
        self._profile_panel.set_user(user_obj, role_str)
        self._stack.setCurrentIndex(2)
        self.user_changed.emit(user_obj, role_str)

    def _on_logout(self):
        self._current_user = None
        self._current_role = ''
        self._stack.setCurrentIndex(0)
        self.user_changed.emit(None, '')

    def get_user(self):  return self._current_user
    def get_role(self):  return self._current_role
    def is_logged_in(self): return self._current_user is not None