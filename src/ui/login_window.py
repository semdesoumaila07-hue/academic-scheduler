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
