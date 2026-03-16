"""
Écran de connexion - Système d'authentification
Gestion des rôles : Administrateur, Enseignant, Étudiant, Responsable Pédagogique
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import json
from pathlib import Path
import hashlib


class LoginDialog(QDialog):
    """Dialogue de connexion avec authentification."""
    
    # Signal émis lors d'une connexion réussie avec les infos utilisateur
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion - Système d'Ordonnancement Académique")
        self.setFixedSize(500, 650)
        self.setModal(True)
        
        # Supprimer les boutons de la fenêtre
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Initialiser l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ==========================================
        # EN-TÊTE (Turquoise comme votre image)
        # ==========================================
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00BFA5,
                    stop:1 #00897B
                );
                border-radius: 0;
            }
        """)
        header.setFixedHeight(120)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Logo/Icône
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Titre
        title = QLabel("Système d'Ordonnancement")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("P-équitable")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # ==========================================
        # CORPS DU FORMULAIRE
        # ==========================================
        body = QFrame()
        body.setStyleSheet("background: white;")
        
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(40, 40, 40, 40)
        body_layout.setSpacing(25)
        
        # Message de bienvenue
        welcome = QLabel("Connexion")
        welcome.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1a1a1a;
        """)
        welcome.setAlignment(Qt.AlignCenter)
        body_layout.addWidget(welcome)
        
        info = QLabel("Veuillez vous identifier pour accéder au système")
        info.setStyleSheet("""
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
        """)
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        body_layout.addWidget(info)
        
        body_layout.addSpacing(10)
        
        # Rôle
        role_label = QLabel("👤 Rôle")
        role_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        body_layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Administrateur",
            "Responsable Pédagogique",
            "Enseignant",
            "Étudiant"
        ])
        self.role_combo.setFixedHeight(45)
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
            QComboBox:focus {
                border-color: #00BFA5;
            }
        """)
        body_layout.addWidget(self.role_combo)
        
        # Identifiant
        username_label = QLabel("📧 Identifiant")
        username_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        body_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre identifiant")
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #00BFA5;
            }
        """)
        body_layout.addWidget(self.username_input)
        
        # Mot de passe
        password_label = QLabel("🔒 Mot de passe")
        password_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        body_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #00BFA5;
            }
        """)
        self.password_input.returnPressed.connect(self.authenticate)
        body_layout.addWidget(self.password_input)
        
        body_layout.addSpacing(10)
        
        # Bouton de connexion
        btn_login = QPushButton("Se connecter")
        btn_login.setFixedHeight(50)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00BFA5,
                    stop:1 #00897B
                );
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00897B,
                    stop:1 #00695C
                );
            }
            QPushButton:pressed {
                background: #00695C;
            }
        """)
        btn_login.clicked.connect(self.authenticate)
        body_layout.addWidget(btn_login)
        
        # Lien mot de passe oublié (optionnel)
        forgot_link = QLabel('<a href="#" style="color: #00BFA5;">Mot de passe oublié ?</a>')
        forgot_link.setAlignment(Qt.AlignCenter)
        forgot_link.setOpenExternalLinks(False)
        forgot_link.linkActivated.connect(self.forgot_password)
        body_layout.addWidget(forgot_link)
        
        body_layout.addStretch()
        
        # Info version
        version = QLabel("Version 1.0.0 | © 2025-2026")
        version.setStyleSheet("font-size: 11px; color: #999;")
        version.setAlignment(Qt.AlignCenter)
        body_layout.addWidget(version)
        
        layout.addWidget(body)
    
    def load_users(self):
        """Charger les utilisateurs depuis le fichier."""
        users_file = Path("data/users.json")
        
        if not users_file.exists():
            # Créer des utilisateurs par défaut
            self.create_default_users()
        
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = data.get('users', [])
        except Exception as e:
            print(f"Erreur chargement utilisateurs: {e}")
            self.create_default_users()
    
    def create_default_users(self):
        """Créer des utilisateurs par défaut."""
        self.users = [
            {
                'id': 1,
                'username': 'admin',
                'password': self.hash_password('admin123'),
                'role': 'Administrateur',
                'nom': 'SEMDE',
                'prenom': 'Soumaïla',
                'email': 'admin@univ.bf'
            },
            {
                'id': 2,
                'username': 'resp.pedago',
                'password': self.hash_password('pedago123'),
                'role': 'Responsable Pédagogique',
                'nom': 'OUEDRAOGO',
                'prenom': 'Aminata',
                'email': 'resp.pedago@univ.bf'
            },
            {
                'id': 3,
                'username': 'kabore.m',
                'password': self.hash_password('prof123'),
                'role': 'Enseignant',
                'nom': 'KABORE',
                'prenom': 'Marie',
                'email': 'marie.kabore@univ.bf'
            }
        ]
        
        # Sauvegarder
        self.save_users()
    
    def save_users(self):
        """Sauvegarder les utilisateurs."""
        users_file = Path("data/users.json")
        users_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump({'users': self.users}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde utilisateurs: {e}")
    
    def hash_password(self, password):
        """Hasher un mot de passe."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self):
        """Authentifier l'utilisateur."""
        role = self.role_combo.currentText()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Cas particulier : les étudiants accèdent en lecture seule SANS mot de passe
        if role == "Étudiant":
            guest_user = {
                'id': -1,
                'username': 'etudiant_invite',
                'password': '',
                'role': 'Étudiant',
                'nom': 'Invité',
                'prenom': 'Étudiant',
                'email': '',
            }
            QMessageBox.information(
                self,
                "Connexion étudiant",
                "✅ Accès étudiant en lecture seule.\n\n"
                "Vous pouvez consulter les emplois du temps."
            )
            # Émettre le signal avec un compte invité
            self.login_successful.emit(guest_user)
            self.accept()
            return
        
        # Pour les autres rôles, identifiant + mot de passe sont requis
        if not username or not password:
            QMessageBox.warning(
                self,
                "Champs requis",
                "⚠️ Veuillez saisir votre identifiant et mot de passe."
            )
            return
        
        # Hasher le mot de passe saisi
        password_hash = self.hash_password(password)
        
        # Chercher l'utilisateur
        user = None
        for u in self.users:
            if (
                u['username'].lower() == username.lower()
                and u['password'] == password_hash
                and u['role'] == role
            ):
                user = u
                break
        
        if user:
            # Connexion réussie
            QMessageBox.information(
                self,
                "Connexion réussie",
                f"✅ Bienvenue {user['prenom']} {user['nom']} !\n\n"
                f"Rôle : {user['role']}"
            )
            
            # Émettre le signal avec les infos utilisateur
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Échec de connexion",
                "❌ Identifiant, mot de passe ou rôle incorrect.\n\n"
                "Veuillez réessayer."
            )
            self.password_input.clear()
            self.password_input.setFocus()
    
    def forgot_password(self):
        """Gérer le mot de passe oublié."""
        QMessageBox.information(
            self,
            "Mot de passe oublié",
            "📧 Pour réinitialiser votre mot de passe,\n"
            "veuillez contacter l'administrateur système.\n\n"
            "Email : admin@univ.bf"
        )
    
    def show_credentials_info(self):
        """Afficher les identifiants par défaut (pour le développement)."""
        info = """
📋 IDENTIFIANTS PAR DÉFAUT :

👨‍💼 Administrateur :
   Identifiant : admin
   Mot de passe : admin123

👔 Responsable Pédagogique :
   Identifiant : resp.pedago
   Mot de passe : pedago123

👨‍🏫 Enseignant :
   Identifiant : kabore.m
   Mot de passe : prof123
        """
        
        QMessageBox.information(
            self,
            "Identifiants de test",
            info
        )


# ==========================================
# TEST STANDALONE
# ==========================================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    login = LoginDialog()
    
    # Afficher les identifiants de test
    login.show_credentials_info()
    
    if login.exec_() == QDialog.Accepted:
        print("Connexion réussie !")
    else:
        print("Connexion annulée")
    
    sys.exit()