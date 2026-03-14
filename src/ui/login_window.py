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