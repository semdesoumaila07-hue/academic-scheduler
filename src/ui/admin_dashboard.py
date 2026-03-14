"""
Interface d’administration pour la gestion des rôles utilisateurs.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from src.database.db_manager import db_manager
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.role_repository import RoleRepository

class AdminDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administration des rôles utilisateurs")
        self.resize(800, 500)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Gestion des rôles des utilisateurs"))
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom d'utilisateur", "Email", "Rôles", "Action"])
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        db_manager.initialize()
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            role_repo = RoleRepository(session)
            users = user_repo.get_all()
            roles = role_repo.list_roles()
            self.table.setRowCount(0)
            for user in users:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(user.username))
                self.table.setItem(row, 1, QTableWidgetItem(user.email))
                # ComboBox pour les rôles
                combo = QComboBox()
                for role in roles:
                    combo.addItem(role.name)
                if user.roles:
                    combo.setCurrentText(user.roles[0].name)
                self.table.setCellWidget(row, 2, combo)
                # Bouton pour appliquer le rôle
                btn = QPushButton("Attribuer")
                btn.clicked.connect(lambda checked, u=user, c=combo: self.assign_role(u, c))
                self.table.setCellWidget(row, 3, btn)
        finally:
            session.close()

    def assign_role(self, user, combo):
        db_manager.initialize()
        session = db_manager.get_session()
        try:
            user_repo = UserRepository(session)
            role_repo = RoleRepository(session)
            role = role_repo.get_by_name(combo.currentText())
            if role:
                user_repo.add_role(user, role)
                QMessageBox.information(self, "Succès", f"Rôle '{role.name}' attribué à {user.username}")
            else:
                QMessageBox.warning(self, "Erreur", "Rôle introuvable")
        finally:
            session.close()
        self.load_users()
