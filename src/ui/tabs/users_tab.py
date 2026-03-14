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