<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
users_tab.py — Onglet Gestion des Utilisateurs (Admin seulement)
Chemin : src/ui/tabs/users_tab.py
"""
import hashlib
import random
import string

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.database.db_manager import db_manager
from src.database.models import UserModel, RoleModel


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _gen_password(length=10) -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choices(chars, k=length))


# ── Dialogue Créer / Modifier utilisateur ────────────────────────
class UserDialog(QDialog):
    def __init__(self, parent=None, user=None, roles=None):
        super().__init__(parent)
        self.user = user
        self.roles = roles or []
        self.setWindowTitle("Modifier utilisateur" if user else "Nouvel utilisateur")
        self.setFixedWidth(420)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(20, 20, 20, 20)

        title = QLabel("✏️ Modifier utilisateur" if self.user else "➕ Nouvel utilisateur")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        title.setStyleSheet("color:#1F4E79;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self._username = QLineEdit()
        self._username.setPlaceholderText("ex: kabore.jean")
        self._username.setStyleSheet("padding:6px; border:1px solid #ddd; border-radius:6px;")
        form.addRow("Nom d'utilisateur :", self._username)

        self._email = QLineEdit()
        self._email.setPlaceholderText("ex: jean@univ.bf")
        self._email.setStyleSheet("padding:6px; border:1px solid #ddd; border-radius:6px;")
        form.addRow("Email :", self._email)

        self._role_combo = QComboBox()
        self._role_combo.setStyleSheet("padding:6px; border:1px solid #ddd; border-radius:6px;")
        for r in self.roles:
            self._role_combo.addItem(r.name, userData=r.id)
        form.addRow("Rôle :", self._role_combo)

        lay.addLayout(form)

        # Pré-remplir si modification
        if self.user:
            self._username.setText(self.user.username or "")
            self._email.setText(self.user.email or "")
            if self.user.roles:
                role_name = self.user.roles[0].name
                idx = self._role_combo.findText(role_name)
                if idx >= 0:
                    self._role_combo.setCurrentIndex(idx)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#1F4E79; color:white; padding:6px 20px; border-radius:6px;")
        lay.addWidget(btns)

    def get_data(self):
        return {
            'username': self._username.text().strip(),
            'email': self._email.text().strip(),
            'role_id': self._role_combo.currentData(),
            'role_name': self._role_combo.currentText(),
        }


# ── Onglet principal ──────────────────────────────────────────────
class UsersTab(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._build_ui()
        self.load_users()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)

        # ── En-tête ──────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("👥 Gestion des Utilisateurs")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color:#1F4E79;")
        header.addWidget(title)
        header.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍 Rechercher un utilisateur...")
        self._search.setFixedWidth(260)
        self._search.setStyleSheet("padding:6px 10px; border:1px solid #ddd; border-radius:8px;")
        self._search.textChanged.connect(self._filter)
        header.addWidget(self._search)

        main.addLayout(header)

        sub = QLabel("UC11 — Gérez les comptes utilisateurs : création, modification, blocage et suppression")
        sub.setStyleSheet("color:#6b7280; font-size:12px;")
        main.addWidget(sub)

        # ── Barre de boutons ─────────────────────────────────────
        btn_bar = QHBoxLayout()

        self._btn_add = QPushButton("➕  Nouvel utilisateur")
        self._btn_add.setFixedHeight(36)
        self._btn_add.setStyleSheet("background:#1F4E79; color:white; border-radius:8px; padding:0 16px; font-weight:bold;")
        self._btn_add.clicked.connect(self._add_user)
        btn_bar.addWidget(self._btn_add)

        self._btn_edit = QPushButton("✏️  Modifier")
        self._btn_edit.setFixedHeight(36)
        self._btn_edit.setStyleSheet("background:#2E75B6; color:white; border-radius:8px; padding:0 16px;")
        self._btn_edit.clicked.connect(self._edit_user)
        btn_bar.addWidget(self._btn_edit)

        self._btn_toggle = QPushButton("⏸️  Désactiver")
        self._btn_toggle.setFixedHeight(36)
        self._btn_toggle.setStyleSheet("background:#F59E0B; color:white; border-radius:8px; padding:0 16px;")
        self._btn_toggle.clicked.connect(self._toggle_active)
        btn_bar.addWidget(self._btn_toggle)

        self._btn_unlock = QPushButton("🔓  Débloquer")
        self._btn_unlock.setFixedHeight(36)
        self._btn_unlock.setStyleSheet("background:#10B981; color:white; border-radius:8px; padding:0 16px;")
        self._btn_unlock.clicked.connect(self._unlock_user)
        btn_bar.addWidget(self._btn_unlock)

        self._btn_reset = QPushButton("🔑  Réinit. MDP")
        self._btn_reset.setFixedHeight(36)
        self._btn_reset.setStyleSheet("background:#8B5CF6; color:white; border-radius:8px; padding:0 16px;")
        self._btn_reset.clicked.connect(self._reset_password)
        btn_bar.addWidget(self._btn_reset)

        self._btn_link = QPushButton("🔗  Lier enseignant")
        self._btn_link.setFixedHeight(36)
        self._btn_link.setStyleSheet("background:#0891B2; color:white; border-radius:8px; padding:0 16px;")
        self._btn_link.clicked.connect(self._link_teacher)
        btn_bar.addWidget(self._btn_link)

        self._btn_delete = QPushButton("🗑️  Supprimer")
        self._btn_delete.setFixedHeight(36)
        self._btn_delete.setStyleSheet("background:#EF4444; color:white; border-radius:8px; padding:0 16px;")
        self._btn_delete.clicked.connect(self._delete_user)
        btn_bar.addWidget(self._btn_delete)

        btn_bar.addStretch()
        main.addLayout(btn_bar)

        # ── Tableau ───────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels([
            "ID", "Nom d'utilisateur", "Email", "Rôle", "Statut", "Bloqué", "Tentatives", "Enseignant lié"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget { border:1px solid #e5e7eb; border-radius:8px; gridline-color:#f3f4f6; }
            QHeaderView::section { background:#1F4E79; color:white; padding:8px; font-weight:bold; }
            QTableWidget::item:selected { background:#EBF3FB; color:#1F4E79; }
        """)
        self._table.verticalHeader().setVisible(False)
        main.addWidget(self._table)

        # ── Compteurs ─────────────────────────────────────────────
        stats = QHBoxLayout()
        self._lbl_total   = self._stat_card("👥 Total", "0", "#EBF3FB", "#1F4E79")
        self._lbl_active  = self._stat_card("✅ Actifs", "0", "#ECFDF5", "#10B981")
        self._lbl_inactive= self._stat_card("⏸️ Inactifs", "0", "#FFFBEB", "#F59E0B")
        self._lbl_locked  = self._stat_card("🔒 Bloqués", "0", "#FEF2F2", "#EF4444")
        for w in [self._lbl_total, self._lbl_active, self._lbl_inactive, self._lbl_locked]:
            stats.addWidget(w)
        stats.addStretch()
        main.addLayout(stats)

    def _stat_card(self, label, value, bg, color):
        frame = QFrame()
        frame.setFixedSize(140, 60)
        frame.setStyleSheet(f"background:{bg}; border-radius:8px; border:1px solid {color}33;")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 8, 12, 8)
        lbl = QLabel(f"{label}\n{value}")
        lbl.setStyleSheet(f"color:{color}; font-weight:bold; font-size:12px;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        frame._label = lbl
        frame._color = color
        frame._prefix = label
        return frame

    def _update_stat(self, frame, value):
        frame._label.setText(f"{frame._prefix}\n{value}")

    def load_users(self):
        try:
            session = db_manager.get_session()
            self._users = session.query(UserModel).all()
            self._roles = session.query(RoleModel).all()
            self._render(self._users)
            # Stats
            total    = len(self._users)
            active   = sum(1 for u in self._users if u.is_active)
            inactive = total - active
            locked   = sum(1 for u in self._users if getattr(u, 'is_locked', False))
            self._update_stat(self._lbl_total,    str(total))
            self._update_stat(self._lbl_active,   str(active))
            self._update_stat(self._lbl_inactive, str(inactive))
            self._update_stat(self._lbl_locked,   str(locked))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Chargement impossible : {e}")

    def _render(self, users):
        self._table.setRowCount(0)
        for u in users:
            row = self._table.rowCount()
            self._table.insertRow(row)

            role_name = u.roles[0].name if u.roles else "—"
            is_locked = getattr(u, 'is_locked', False)
            attempts  = getattr(u, 'login_attempts', 0) or 0
            statut    = "✅ Actif" if u.is_active else "⏸️ Inactif"
            bloque    = "🔒 Oui" if is_locked else "✅ Non"

            teacher_link = "—"
            if getattr(u, 'teacher_id', None):
                try:
                    from src.database.models import TeacherModel
                    t = session.query(TeacherModel).filter_by(id=u.teacher_id).first()
                    teacher_link = t.full_name if t else f"ID:{u.teacher_id}"
                except:
                    pass
            items = [
                str(u.id), u.username or "—", u.email or "—",
                role_name, statut, bloque, str(attempts), teacher_link
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                # Colorier selon statut
                if not u.is_active:
                    item.setBackground(QColor("#FFF9C4"))
                elif is_locked:
                    item.setBackground(QColor("#FFEBEE"))
                self._table.setItem(row, col, item)

            # Stocker l'id user dans la ligne
            self._table.item(row, 0).setData(Qt.UserRole, u.id)

    def _filter(self, text):
        text = text.lower()
        filtered = [u for u in self._users if
                    text in (u.username or "").lower() or
                    text in (u.email or "").lower() or
                    any(text in r.name.lower() for r in u.roles)]
        self._render(filtered)

    def _get_selected_user(self):
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Sélection", "Sélectionnez un utilisateur.")
            return None
        uid = self._table.item(row, 0).data(Qt.UserRole)
        session = db_manager.get_session()
        return session.query(UserModel).filter_by(id=uid).first(), session

    def _add_user(self):
        session = db_manager.get_session()
        roles = session.query(RoleModel).all()
        dlg = UserDialog(self, roles=roles)
        if dlg.exec_() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data['username'] or not data['email']:
            QMessageBox.warning(self, "Erreur", "Nom et email obligatoires.")
            return
        try:
            existing = session.query(UserModel).filter(
                (UserModel.username == data['username']) | (UserModel.email == data['email'])
            ).first()
            if existing:
                QMessageBox.warning(self, "Erreur", "Nom d'utilisateur ou email déjà utilisé.")
                return
            pw_temp = _gen_password()
            user = UserModel(
                username=data['username'],
                email=data['email'],
                password_hash=_hash(pw_temp),
                is_active=True,
            )
            role = session.query(RoleModel).filter_by(id=data['role_id']).first()
            if role:
                user.roles.append(role)
            session.add(user)
            session.commit()
            QMessageBox.information(self, "Compte créé",
                f"✅ Compte créé avec succès !\n\n"
                f"Utilisateur : {data['username']}\n"
                f"Mot de passe temporaire : {pw_temp}\n\n"
                f"Communiquez ce mot de passe à l'utilisateur.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _edit_user(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result
        roles = session.query(RoleModel).all()
        dlg = UserDialog(self, user=user, roles=roles)
        if dlg.exec_() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            user.username = data['username']
            user.email = data['email']
            role = session.query(RoleModel).filter_by(id=data['role_id']).first()
            if role:
                user.roles = [role]
            session.commit()
            QMessageBox.information(self, "Succès", "✅ Utilisateur modifié avec succès.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _toggle_active(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result
        action = "désactiver" if user.is_active else "réactiver"
        rep = QMessageBox.question(self, "Confirmation",
            f"Voulez-vous vraiment {action} le compte de {user.username} ?")
        if rep != QMessageBox.Yes:
            return
        try:
            user.is_active = not user.is_active
            session.commit()
            status = "désactivé" if not user.is_active else "réactivé"
            QMessageBox.information(self, "Succès", f"✅ Compte {status} avec succès.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _unlock_user(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result
        if not getattr(user, 'is_locked', False):
            QMessageBox.information(self, "Info", "Ce compte n'est pas bloqué.")
            return
        try:
            user.is_locked = False
            user.login_attempts = 0
            session.commit()
            QMessageBox.information(self, "Succès",
                f"✅ Compte de {user.username} débloqué avec succès.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _reset_password(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result
        rep = QMessageBox.question(self, "Confirmation",
            f"Réinitialiser le mot de passe de {user.username} ?")
        if rep != QMessageBox.Yes:
            return
        try:
            pw_temp = _gen_password()
            user.password_hash = _hash(pw_temp)
            user.login_attempts = 0
            user.is_locked = False
            session.commit()
            QMessageBox.information(self, "Mot de passe réinitialisé",
                f"✅ Nouveau mot de passe temporaire :\n\n"
                f"🔑  {pw_temp}\n\n"
                f"Communiquez ce mot de passe à {user.username}.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _link_teacher(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result

        # Charger la liste des enseignants
        from src.database.models import TeacherModel
        teachers = session.query(TeacherModel).all()
        if not teachers:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Info", "Aucun enseignant disponible.")
            return

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QDialogButtonBox, QLabel
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Lier {user.username} à un enseignant")
        dlg.setFixedWidth(380)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        lbl = QLabel("Selectionnez l'enseignant correspondant a " + user.username)
        lbl.setStyleSheet("font-size:12px; color:#1f2937;")
        lay.addWidget(lbl)

        combo = QComboBox()
        combo.setStyleSheet("padding:6px; border:1px solid #ddd; border-radius:6px;")
        combo.addItem("-- Aucun lien --", userData=None)
        for t in teachers:
            current = " ✓ (lié)" if getattr(user, 'teacher_id', None) == t.id else ""
            combo.addItem(f"{t.full_name} ({t.email}){current}", userData=t.id)
        # Présélectionner si déjà lié
        if getattr(user, 'teacher_id', None):
            for i in range(combo.count()):
                if combo.itemData(i) == user.teacher_id:
                    combo.setCurrentIndex(i)
                    break
        lay.addWidget(combo)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#0891B2; color:white; padding:6px 20px; border-radius:6px;")
        lay.addWidget(btns)

        if dlg.exec_() != QDialog.Accepted:
            return

        from sqlalchemy import text
        from src.database.db_manager import db_manager
        teacher_id = combo.currentData()
        try:
            db_manager.get_session().execute(
                text("UPDATE users SET teacher_id = :tid WHERE id = :uid"),
                {'tid': teacher_id, 'uid': user.id}
            )
            db_manager.get_session().commit()
            msg = f"✅ {user.username} lié à {combo.currentText()}" if teacher_id else f"✅ Lien supprimé pour {user.username}"
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Succès", msg)
            self.load_users()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erreur", str(e))

    def _delete_user(self):
        result = self._get_selected_user()
        if not result:
            return
        user, session = result
        rep = QMessageBox.question(self, "⚠️ Suppression définitive",
            f"Supprimer définitivement le compte de {user.username} ?\n\nCette action est irréversible !")
        if rep != QMessageBox.Yes:
            return
        try:
            session.delete(user)
            session.commit()
            QMessageBox.information(self, "Succès", f"✅ Compte supprimé définitivement.")
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
=======
"""
Onglet de gestion des utilisateurs - Réservé à l'Administrateur.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QComboBox, QMessageBox, QFormLayout,
    QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import json
import os
import hashlib
import secrets
import string


def hash_password(password):
    """Hash un mot de passe."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_default_password(length=8):
    """Génère un mot de passe par défaut."""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class CreateUserDialog(QDialog):
    """Dialogue pour créer un utilisateur."""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None
        self.generated_password = ""
        
        self.setWindowTitle("Modifier utilisateur" if self.is_edit else "Créer utilisateur")
        self.setMinimumWidth(550)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #F9FAFB;
            }
        """)
        
        self.init_ui()
        
        if self.is_edit:
            self.fill_fields()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel(
            "Modifier utilisateur" if self.is_edit 
            else "Créer un nouvel utilisateur"
        )
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #1F2937;"
        )
        layout.addWidget(title)
        
        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Nom complet
        self.name_input = self.create_field(
            form_layout, "Nom complet *", "Ex: Dr. Marie KABORE"
        )
        
        # Email / Identifiant
        self.email_input = self.create_field(
            form_layout, "Email / Identifiant *", "Ex: marie.kabore@uts.bf"
        )
        
        # Rôle
        role_label = QLabel("Rôle *")
        role_label.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #374151;"
        )
        form_layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "enseignant",
            "etudiant", 
            "responsable_pedagogique",
            "admin"
        ])
        self.role_combo.setStyleSheet(self.get_input_style())
        self.role_combo.setFixedHeight(45)
        form_layout.addWidget(self.role_combo)
        
        # Section mot de passe
        password_group = QGroupBox("Mot de passe")
        password_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        password_layout = QVBoxLayout(password_group)
        
        # Mot de passe personnalisé
        pwd_label = QLabel("Définir un mot de passe *")
        pwd_label.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #374151;"
        )
        password_layout.addWidget(pwd_label)
        
        pwd_row = QHBoxLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez un mot de passe...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.get_input_style())
        self.password_input.setFixedHeight(45)
        
        btn_generate = QPushButton("🔄 Générer")
        btn_generate.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        """)
        btn_generate.setFixedHeight(45)
        btn_generate.clicked.connect(self.generate_password)
        
        btn_show = QPushButton("👁️")
        btn_show.setStyleSheet("""
            QPushButton {
                background: #F3F4F6;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #E5E7EB;
            }
        """)
        btn_show.setFixedSize(45, 45)
        btn_show.setCheckable(True)
        btn_show.clicked.connect(self.toggle_password_visibility)
        
        pwd_row.addWidget(self.password_input, 1)
        pwd_row.addWidget(btn_generate)
        pwd_row.addWidget(btn_show)
        password_layout.addLayout(pwd_row)
        
        # Affichage du mot de passe généré
        self.password_display = QLabel("")
        self.password_display.setStyleSheet("""
            QLabel {
                background: #F0FDF4;
                border: 1px solid #86EFAC;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #166534;
            }
        """)
        self.password_display.setVisible(False)
        password_layout.addWidget(self.password_display)
        
        # Option changer au premier login
        self.force_change_check = QCheckBox(
            "Forcer le changement de mot de passe à la première connexion"
        )
        self.force_change_check.setChecked(True)
        self.force_change_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #374151;
            }
        """)
        password_layout.addWidget(self.force_change_check)
        
        form_layout.addWidget(password_group)
        layout.addWidget(form_frame)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet(self.get_secondary_button_style())
        btn_cancel.setFixedHeight(45)
        btn_cancel.setFixedWidth(120)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        
        btn_save = QPushButton(
            "Enregistrer" if self.is_edit else "Créer l'utilisateur"
        )
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #000;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        btn_save.setFixedHeight(45)
        btn_save.clicked.connect(self.save)
        btn_save.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
    
    def create_field(self, parent_layout, label_text, placeholder):
        """Crée un champ de saisie."""
        label = QLabel(label_text)
        label.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #374151;"
        )
        parent_layout.addWidget(label)
        
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet(self.get_input_style())
        field.setFixedHeight(45)
        parent_layout.addWidget(field)
        
        return field
    
    def generate_password(self):
        """Génère un mot de passe automatique."""
        password = generate_default_password(10)
        self.generated_password = password
        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.Normal)
        
        self.password_display.setText(
            f"🔑 Mot de passe généré : {password}\n"
            f"📋 Communiquez ce mot de passe à l'utilisateur !"
        )
        self.password_display.setVisible(True)
    
    def toggle_password_visibility(self, checked):
        """Affiche/masque le mot de passe."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def fill_fields(self):
        """Remplit les champs en mode édition."""
        if self.user_data:
            self.name_input.setText(self.user_data.get('name', ''))
            self.email_input.setText(self.user_data.get('email', ''))
            
            role = self.user_data.get('role', 'enseignant')
            index = self.role_combo.findText(role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
    
    def save(self):
        """Valide et sauvegarde."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        role = self.role_combo.currentText()
        password = self.password_input.text().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom est requis.")
            return
        
        if not email:
            QMessageBox.warning(self, "Erreur", "L'email est requis.")
            return
        
        # Pour un nouvel utilisateur :
        # - rôles enseignant / responsable / admin : mot de passe obligatoire, généré par défaut si vide
        # - rôle étudiant : pas de mot de passe obligatoire (accès en lecture seule)
        if not self.is_edit and not password:
            if role == "etudiant":
                # Étudiant : pas de mot de passe nécessaire pour la connexion
                password = ""
            else:
                # Générer automatiquement un mot de passe par défaut
                generated = generate_default_password(10)
                self.generated_password = generated
                password = generated
                self.password_input.setText(generated)
                self.password_input.setEchoMode(QLineEdit.Normal)
                self.password_display.setText(
                    f"🔑 Mot de passe généré : {generated}\n"
                    f"📋 Communiquez ce mot de passe à l'utilisateur !"
                )
                self.password_display.setVisible(True)
        
        # Stocker les données
        self.result_data = {
            'name': name,
            'email': email,
            'role': role,
            'password': password,
            'force_change': self.force_change_check.isChecked(),
            'generated_password': self.generated_password
        }
        
        self.accept()
    
    def get_data(self):
        """Retourne les données saisies."""
        return getattr(self, 'result_data', None)
    
    def get_input_style(self):
        """Style des inputs."""
        return """
            QLineEdit, QComboBox {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
                color: #1F2937;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #000;
            }
        """
    
    def get_secondary_button_style(self):
        """Style bouton secondaire."""
        return """
            QPushButton {
                background: white;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #F9FAFB;
            }
        """


class PasswordDialog(QDialog):
    """Dialogue pour réinitialiser le mot de passe."""
    
    def __init__(self, user_name, parent=None):
        super().__init__(parent)
        self.user_name = user_name
        self.setWindowTitle("Réinitialiser le mot de passe")
        self.setMinimumWidth(450)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("🔑 Réinitialiser le mot de passe")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1F2937;"
        )
        layout.addWidget(title)
        
        # Info utilisateur
        user_info = QLabel(f"Utilisateur : {self.user_name}")
        user_info.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
            padding: 10px;
            background: #F3F4F6;
            border-radius: 6px;
        """)
        layout.addWidget(user_info)
        
        # Nouveau mot de passe
        pwd_label = QLabel("Nouveau mot de passe *")
        pwd_label.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #374151;"
        )
        layout.addWidget(pwd_label)
        
        pwd_row = QHBoxLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(
            "Entrez le nouveau mot de passe..."
        )
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
            }
        """)
        self.password_input.setFixedHeight(45)
        
        btn_generate = QPushButton("🔄 Générer")
        btn_generate.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background: #2563EB; }
        """)
        btn_generate.setFixedHeight(45)
        btn_generate.clicked.connect(self.generate)
        
        pwd_row.addWidget(self.password_input, 1)
        pwd_row.addWidget(btn_generate)
        layout.addLayout(pwd_row)
        
        # Affichage du mot de passe
        self.display = QLabel("")
        self.display.setStyleSheet("""
            QLabel {
                background: #F0FDF4;
                border: 1px solid #86EFAC;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                color: #166534;
            }
        """)
        self.display.setVisible(False)
        layout.addWidget(self.display)
        
        # Forcer changement
        self.force_check = QCheckBox(
            "Forcer le changement à la prochaine connexion"
        )
        self.force_check.setChecked(True)
        layout.addWidget(self.force_check)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 10px 20px;
            }
        """)
        btn_cancel.setFixedHeight(40)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Réinitialiser")
        btn_save.setStyleSheet("""
            QPushButton {
                background: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover { background: #DC2626; }
        """)
        btn_save.setFixedHeight(40)
        btn_save.clicked.connect(self.save)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
    
    def generate(self):
        """Génère un mot de passe."""
        pwd = generate_default_password(10)
        self.password_input.setText(pwd)
        self.password_input.setEchoMode(QLineEdit.Normal)
        self.display.setText(
            f"🔑 Nouveau mot de passe : {pwd}\n"
            f"📋 Communiquez ce mot de passe à l'utilisateur !"
        )
        self.display.setVisible(True)
    
    def save(self):
        """Valide et sauvegarde."""
        password = self.password_input.text().strip()
        if not password:
            QMessageBox.warning(
                self, "Erreur", "Veuillez entrer un mot de passe."
            )
            return
        
        self.result = {
            'password': password,
            'force_change': self.force_check.isChecked()
        }
        self.accept()
    
    def get_data(self):
        """Retourne les données."""
        return getattr(self, 'result', None)


class UsersTab(QWidget):
    """Onglet de gestion des utilisateurs."""
    
    USERS_FILE = "data/users.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.users = []
        self.load_users()
        self.init_ui()
    
    def load_users(self):
        """Charge les utilisateurs depuis le fichier JSON."""
        try:
            if os.path.exists(self.USERS_FILE):
                with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Le fichier peut être au format {"users": [...]} (utilisé par LoginDialog)
                    if isinstance(data, dict) and "users" in data:
                        self.users = data.get("users", [])
                    # Ou directement une liste d'utilisateurs (ancien format)
                    elif isinstance(data, list):
                        self.users = data
                    else:
                        self.users = []
            else:
                # Si le fichier n'existe pas encore, laisser LoginDialog le créer
                self.users = []
        except Exception as e:
            print(f"Erreur chargement utilisateurs : {e}")
            self.users = []
    
    def save_users(self):
        """Sauvegarde les utilisateurs dans le fichier JSON."""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                # Harmoniser le format avec LoginDialog : {"users": [...]}
                json.dump({"users": self.users}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde utilisateurs : {e}")
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QVBoxLayout()
        title = QLabel("Gestion des Utilisateurs")
        title.setStyleSheet(
            "font-size: 28px; font-weight: 600; color: #1a1a1a;"
        )
        header_layout.addWidget(title)
        
        subtitle = QLabel(
            "Créez et gérez les comptes des enseignants, "
            "étudiants et responsables pédagogiques"
        )
        subtitle.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        roles = ['admin', 'enseignant', 'etudiant', 'responsable_pedagogique']
        labels = ['Admins', 'Enseignants', 'Étudiants', 'Responsables']
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
        
        for role, label, color in zip(roles, labels, colors):
            count = sum(1 for u in self.users if u.get('role') == role)
            card = self.create_stat_card(label, count, color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Conteneur principal
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)
        
        # En-tête du tableau
        table_header = QHBoxLayout()
        
        count_label = QLabel(f"Utilisateurs ({len(self.users)})")
        count_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        btn_add = QPushButton("+ Créer un utilisateur")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #000;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #333; }
        """)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.create_user)
        
        table_header.addWidget(count_label)
        table_header.addStretch()
        table_header.addWidget(btn_add)
        main_layout.addLayout(table_header)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nom complet", "Email", "Rôle", "Statut", "Forcer MDP", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.Fixed
        )
        self.table.setColumnWidth(5, 180)
        self.table.setStyleSheet(self.get_table_style())
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        
        main_layout.addWidget(self.table)
        layout.addWidget(main_frame)
        
        # Charger les données
        self.refresh_table()
    
    def refresh_table(self):
        """Rafraîchit le tableau."""
        self.table.setRowCount(len(self.users))
        
        role_labels = {
            'Administrateur': ('Administrateur', '#3B82F6'),
            'Enseignant': ('Enseignant', '#10B981'),
            'Étudiant': ('Étudiant', '#F59E0B'),
            'Responsable Pédagogique': ('Responsable', '#8B5CF6')
        }
        
        for i, user in enumerate(self.users):
            # Nom complet : prénom + nom (format utilisé par LoginDialog)
            full_name = f"{user.get('prenom', '')} {user.get('nom', '')}".strip()
            self.table.setItem(i, 0, QTableWidgetItem(full_name))
            # Identifiant = username (login)
            self.table.setItem(i, 1, QTableWidgetItem(user.get('username', '')))
            
            # Rôle avec badge coloré
            role = user.get('role', '')
            role_label, role_color = role_labels.get(role, (role, '#6B7280'))
            role_item = QTableWidgetItem(f"  {role_label}  ")
            role_item.setBackground(QColor(role_color + "22"))
            role_item.setForeground(QColor(role_color))
            self.table.setItem(i, 2, role_item)
            
            # Statut
            active = user.get('active', True)
            status_item = QTableWidgetItem(
                "✅ Actif" if active else "❌ Inactif"
            )
            if active:
                status_item.setForeground(QColor("#10B981"))
            else:
                status_item.setForeground(QColor("#EF4444"))
            self.table.setItem(i, 3, status_item)
            
            # Forcer changement MDP
            force = user.get('force_change', False)
            force_item = QTableWidgetItem(
                "⚠️ Oui" if force else "Non"
            )
            if force:
                force_item.setForeground(QColor("#F59E0B"))
            self.table.setItem(i, 4, force_item)
            
            # Boutons d'action
            actions = self.create_action_buttons(i, user)
            self.table.setCellWidget(i, 5, actions)
        
        self.table.setRowHeight(0, 50)
        for i in range(len(self.users)):
            self.table.setRowHeight(i, 50)
    
    def create_action_buttons(self, row_index, user):
        """Crée les boutons d'action."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # Bouton modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setToolTip("Modifier")
        btn_edit.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #F3F4F6;
                border-radius: 4px;
            }
        """)
        btn_edit.setFixedSize(32, 32)
        btn_edit.clicked.connect(lambda: self.edit_user(row_index))
        btn_edit.setCursor(Qt.PointingHandCursor)
        
        # Bouton réinitialiser MDP
        btn_pwd = QPushButton("🔑")
        btn_pwd.setToolTip("Réinitialiser le mot de passe")
        btn_pwd.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #FEF3C7;
                border-radius: 4px;
            }
        """)
        btn_pwd.setFixedSize(32, 32)
        btn_pwd.clicked.connect(lambda: self.reset_password(row_index))
        btn_pwd.setCursor(Qt.PointingHandCursor)
        
        # Bouton activer/désactiver
        active = user.get('active', True)
        btn_toggle = QPushButton("🔴" if active else "🟢")
        btn_toggle.setToolTip(
            "Désactiver" if active else "Activer"
        )
        btn_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #F3F4F6;
                border-radius: 4px;
            }
        """)
        btn_toggle.setFixedSize(32, 32)
        btn_toggle.clicked.connect(
            lambda: self.toggle_user(row_index)
        )
        btn_toggle.setCursor(Qt.PointingHandCursor)
        
        # Bouton supprimer
        btn_delete = QPushButton("🗑️")
        btn_delete.setToolTip("Supprimer")
        btn_delete.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: #FEE2E2;
                border-radius: 4px;
            }
        """)
        btn_delete.setFixedSize(32, 32)
        btn_delete.clicked.connect(
            lambda: self.delete_user(row_index)
        )
        btn_delete.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_pwd)
        layout.addWidget(btn_toggle)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget
    
    def create_user(self):
        """Crée un nouvel utilisateur."""
        dialog = CreateUserDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                # Vérifier que l'identifiant (username) n'existe pas déjà
                usernames = [u.get('username') for u in self.users]
                if data['email'] in usernames:
                    QMessageBox.warning(
                        self, "Erreur",
                        f"L'identifiant '{data['email']}' existe déjà !"
                    )
                    return
                
                # Mapper le rôle UI vers le rôle utilisé par le système d'authentification
                role_map = {
                    'admin': 'Administrateur',
                    'enseignant': 'Enseignant',
                    'etudiant': 'Étudiant',
                    'responsable_pedagogique': 'Responsable Pédagogique',
                }
                mapped_role = role_map.get(data['role'], data['role'])

                # Tenter de séparer prénom / nom à partir du champ "Nom complet"
                full_name = data['name'].strip()
                parts = full_name.split()
                if len(parts) >= 2:
                    nom = parts[-1]
                    prenom = " ".join(parts[:-1])
                else:
                    prenom = full_name
                    nom = ""

                # Créer l'utilisateur au format attendu par LoginDialog
                new_user = {
                    'id': max([u.get('id', 0) for u in self.users], default=0) + 1,
                    'username': data['email'],  # login / identifiant
                    'password': hash_password(data['password']),
                    'role': mapped_role,
                    'nom': nom,
                    'prenom': prenom,
                    'email': data['email'],
                    'active': True,
                    'force_change': data['force_change']
                }
                
                self.users.append(new_user)
                self.save_users()
                self.refresh_table()
                
                # Message de succès avec les identifiants
                msg_text = (
                    f"✅ Utilisateur créé avec succès !\n\n"
                    f"📋 IDENTIFIANTS À COMMUNIQUER :\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 Nom : {data['name']}\n"
                    f"👤 Identifiant (login) : {data['email']}\n"
                    f"🔑 Mot de passe : {data['password']}\n"
                    f"🎭 Rôle : {mapped_role}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ Communiquez ces informations à l'utilisateur !"
                )
                
                QMessageBox.information(
                    self, "Utilisateur créé", msg_text
                )
    
    def edit_user(self, row_index):
        """Modifie un utilisateur."""
        if row_index < len(self.users):
            user = self.users[row_index]
            dialog = CreateUserDialog(self, user)
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data:
                    # Mapper le rôle UI vers le rôle utilisé par le système d'authentification
                    role_map = {
                        'admin': 'Administrateur',
                        'enseignant': 'Enseignant',
                        'etudiant': 'Étudiant',
                        'responsable_pedagogique': 'Responsable Pédagogique',
                    }
                    mapped_role = role_map.get(data['role'], data['role'])

                    # Mettre à jour le nom complet
                    full_name = data['name'].strip()
                    parts = full_name.split()
                    if len(parts) >= 2:
                        nom = parts[-1]
                        prenom = " ".join(parts[:-1])
                    else:
                        prenom = full_name
                        nom = ""

                    # Mettre à jour
                    self.users[row_index]['username'] = data['email']
                    self.users[row_index]['email'] = data['email']
                    self.users[row_index]['role'] = mapped_role
                    self.users[row_index]['nom'] = nom
                    self.users[row_index]['prenom'] = prenom
                    
                    if data['password']:
                        self.users[row_index]['password'] = hash_password(
                            data['password']
                        )
                        self.users[row_index]['force_change'] = data['force_change']
                    
                    self.save_users()
                    self.refresh_table()
                    QMessageBox.information(
                        self, "Succès", "Utilisateur modifié !"
                    )
    
    def reset_password(self, row_index):
        """Réinitialise le mot de passe."""
        if row_index < len(self.users):
            user = self.users[row_index]
            dialog = PasswordDialog(user.get('name', ''), self)
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                if data:
                    self.users[row_index]['password'] = hash_password(
                        data['password']
                    )
                    self.users[row_index]['force_change'] = data['force_change']
                    
                    self.save_users()
                    self.refresh_table()
                    
                    QMessageBox.information(
                        self, "Succès",
                        f"✅ Mot de passe réinitialisé !\n\n"
                        f"👤 Utilisateur : {user.get('name')}\n"
                        f"🔑 Nouveau mot de passe : {data['password']}\n\n"
                        f"⚠️ Communiquez ce nouveau mot de passe à l'utilisateur !"
                    )
    
    def toggle_user(self, row_index):
        """Active ou désactive un utilisateur."""
        if row_index < len(self.users):
            user = self.users[row_index]
            
            if user.get('role') == 'admin':
                QMessageBox.warning(
                    self, "Erreur",
                    "Impossible de désactiver le compte admin !"
                )
                return
            
            active = user.get('active', True)
            action = "désactiver" if active else "activer"
            
            reply = QMessageBox.question(
                self, f"Confirmer",
                f"Voulez-vous {action} le compte de '{user.get('name')}' ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.users[row_index]['active'] = not active
                self.save_users()
                self.refresh_table()
    
    def delete_user(self, row_index):
        """Supprime un utilisateur."""
        if row_index < len(self.users):
            user = self.users[row_index]
            
            if user.get('role') == 'admin':
                QMessageBox.warning(
                    self, "Erreur",
                    "Impossible de supprimer le compte admin !"
                )
                return
            
            reply = QMessageBox.question(
                self, "Confirmer la suppression",
                f"Supprimer définitivement '{user.get('name')}' ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.users[row_index]
                self.save_users()
                self.refresh_table()
    
    def create_stat_card(self, label, count, color):
        """Crée une carte de statistique."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #E5E7EB;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        count_label = QLabel(str(count))
        count_label.setStyleSheet(
            f"font-size: 28px; font-weight: 700; color: {color};"
        )
        
        name_label = QLabel(label)
        name_label.setStyleSheet("font-size: 13px; color: #6B7280;")
        
        layout.addWidget(count_label)
        layout.addWidget(name_label)
        
        return card
    
    def get_table_style(self):
        """Style de la table."""
        return """
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #F3F4F6;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #F9FAFB;
                color: #1F2937;
            }
            QHeaderView::section {
                background-color: white;
                padding: 12px 16px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-weight: 600;
                font-size: 13px;
                color: #6B7280;
            }
        """
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
