"""
Fenêtre principale de l'application.
Système d'Ordonnancement Académique P-équitable.
VERSION AVEC AUTHENTIFICATION ET RESTRICTIONS D'ACCÈS
"""
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QFrame,
    QStatusBar,
    QMessageBox,
)
from PyQt5.QtCore import Qt

# Import des onglets
from .tabs import (
    DashboardTab,
    StructureTab,
    TeachersTab,
    ActivitiesTab,
    CalendarTab,
    SchedulingTab,
    AnalysisTab,
    LeavesTab,
    ReportsTab,
    TimetableTab,
    UsersTab,
)

# Import du gestionnaire de permissions
from .permission_manager import PermissionManager


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application avec gestion des permissions."""
    
    def __init__(self, user_data=None):
        super().__init__()
        
        # Stocker les infos utilisateur
        if user_data is None:
            # Mode sans authentification (développement)
            self.user = {
                'role': 'Administrateur',
                'nom': 'SEMDE',
                'prenom': 'Soumaïla',
                'email': 'admin@univ.bf'
            }
        else:
            self.user = user_data
        
        self.role = self.user.get('role', 'Administrateur')
        
        self.setWindowTitle(f"Système d'Ordonnancement Académique - {self.role}")
        self.setMinimumSize(1400, 900)
        
        # Appliquer le style global
        self.setStyleSheet(self.get_global_style())
        
        self.init_ui()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Afficher message de bienvenue
        if user_data:
            self.show_welcome_message()
    
    def show_welcome_message(self):
        """Afficher un message de bienvenue personnalisé."""
        message = PermissionManager.get_welcome_message(self.user)
        QMessageBox.information(
            self,
            "Bienvenue",
            f"✅ {message}"
        )
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre supérieure
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Contenu principal
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Menu latéral (avec restrictions selon le rôle)
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Zone de contenu (onglets)
        self.tab_widget = self.create_tab_widget()
        content_layout.addWidget(self.tab_widget, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # Barre de statut
        self.create_status_bar()
    
    def create_top_bar(self):
        """Crée la barre supérieure."""
        top_bar = QFrame()
        top_bar.setFixedHeight(70)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
            }
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo et titre
        logo_layout = QHBoxLayout()
        
        # Icône
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 32px;")
        
        # Titre
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        app_name = QLabel("Pfair Scheduler")
        app_name.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #1F2937;
        """)
        
        app_subtitle = QLabel("Ordonnancement académique")
        app_subtitle.setStyleSheet("""
            font-size: 12px;
            color: #6B7280;
        """)
        
        title_layout.addWidget(app_name)
        title_layout.addWidget(app_subtitle)
        
        logo_layout.addWidget(icon_label)
        logo_layout.addLayout(title_layout)
        logo_layout.addStretch()
        
        layout.addLayout(logo_layout)
        layout.addStretch()
        
        # Utilisateur connecté
        user_layout = QHBoxLayout()
        user_layout.setSpacing(15)
        
        # Badge utilisateur avec initiale
        initiale = self.user.get('prenom', 'U')[0].upper()
        user_badge = QLabel(initiale)
        user_badge.setFixedSize(40, 40)
        user_badge.setAlignment(Qt.AlignCenter)
        
        # Couleur selon le rôle
        badge_colors = {
            'Administrateur': '#E74C3C',
            'Responsable Pédagogique': '#3498DB',
            'Enseignant': '#27AE60',
            'Étudiant': '#9B59B6'
        }
        badge_color = badge_colors.get(self.role, '#3B82F6')
        
        user_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {badge_color};
                color: white;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        
        # Nom et rôle
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(2)
        
        user_name = QLabel(f"{self.user.get('prenom', '')} {self.user.get('nom', '')}")
        user_name.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #1F2937;
        """)
        
        user_role = QLabel(self.role)
        user_role.setStyleSheet(f"""
            font-size: 11px;
            color: {badge_color};
            font-weight: 500;
        """)
        
        user_info_layout.addWidget(user_name)
        user_info_layout.addWidget(user_role)
        
        # Bouton déconnexion
        btn_logout = QPushButton("🚪")
        btn_logout.setFixedSize(35, 35)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setToolTip("Se déconnecter")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
                border-radius: 6px;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        
        user_layout.addWidget(user_badge)
        user_layout.addLayout(user_info_layout)
        user_layout.addWidget(btn_logout)
        
        layout.addLayout(user_layout)
        
        return top_bar
    
    def logout(self):
        """Déconnexion."""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            # Relancer l'écran de connexion
            from .login_dialog import LoginDialog
            login = LoginDialog()
            if login.exec_() == LoginDialog.Accepted:
                # Récréer la fenêtre principale avec le nouvel utilisateur
                import sys
                from PyQt5.QtWidgets import QApplication
                QApplication.instance().quit()
                # Note: En production, il faudrait relancer l'application
    
    def create_sidebar(self):
        """Crée le menu latéral AVEC RESTRICTIONS selon le rôle."""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border-right: 1px solid #E5E7EB;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)
        
        # Boutons de navigation (filtrés selon les permissions)
        self.nav_buttons = []
        
        # Définir TOUS les onglets possibles
        all_nav_items = [
            ("📊", "Dashboard", "dashboard", 0),
            ("🏛️", "Structure", "structure", 1),
            ("👨‍🏫", "Enseignants", "teachers", 2),
            ("📚", "Activités", "activities", 3),
            ("📅", "Calendrier", "calendar", 4),
            ("🏖️", "Congés", "leaves", 5),
            ("⏰", "Ordonnancement", "scheduling", 6),
            ("⏱️", "Retards", "analysis", 7),
            ("📈", "Rapports", "reports", 8),
            ("🗓️", "Emplois du temps", "timetable", 9),
            ("👥", "Utilisateurs", "users", 10),
        ]
        
        # Filtrer selon les permissions
        accessible_tabs = PermissionManager.get_accessible_tabs(self.role)
        
        # L'index logique correspond à l'ordre réel des onglets créés
        current_index = 0
        
        for icon, text, tab_name, _original_index in all_nav_items:
            if tab_name in accessible_tabs:
                btn = self.create_nav_button(icon, text, current_index)
                self.nav_buttons.append(btn)
                layout.addWidget(btn)
                current_index += 1
        
        layout.addStretch()
        
        # Info rôle en bas
        role_info = QLabel(f"🔐 Connecté comme\n{self.role}")
        role_info.setAlignment(Qt.AlignCenter)
        role_info.setStyleSheet("""
            font-size: 11px;
            color: #666;
            padding: 10px;
            background: #E8E8E8;
            border-radius: 6px;
            margin: 10px;
        """)
        layout.addWidget(role_info)
        
        # Marquer le premier comme actif
        if self.nav_buttons:
            self.nav_buttons[0].setProperty("active", True)
            self.nav_buttons[0].setStyleSheet(self.get_nav_button_style(True))
        
        return sidebar
    
    def create_nav_button(self, icon, text, tab_index):
        """Crée un bouton de navigation."""
        btn = QPushButton(f"{icon}  {text}")
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self.get_nav_button_style(False))
        
        # Connecter au changement d'onglet
        if tab_index >= 0:
            btn.clicked.connect(lambda: self.switch_tab(tab_index, btn))
        
        return btn
    
    def switch_tab(self, index, button):
        """Change d'onglet et met à jour le menu."""
        self.tab_widget.setCurrentIndex(index)
        
        # Réinitialiser tous les boutons
        for btn in self.nav_buttons:
            btn.setProperty("active", False)
            btn.setStyleSheet(self.get_nav_button_style(False))
        
        # Activer le bouton cliqué
        button.setProperty("active", True)
        button.setStyleSheet(self.get_nav_button_style(True))
    
    def create_tab_widget(self):
        """Crée le widget d'onglets (masqué) AVEC RESTRICTIONS."""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                display: none;
            }
        """)
        
        # Vérifier les permissions pour chaque onglet
        accessible_tabs = PermissionManager.get_accessible_tabs(self.role)
        
        # Ajouter UNIQUEMENT les onglets autorisés
        if 'dashboard' in accessible_tabs:
            tab_widget.addTab(DashboardTab(), "Dashboard")
        
        if 'structure' in accessible_tabs:
            tab_widget.addTab(StructureTab(), "Structure")
        
        if 'teachers' in accessible_tabs:
            tab_widget.addTab(TeachersTab(), "Enseignants")
        
        if 'activities' in accessible_tabs:
            tab_widget.addTab(ActivitiesTab(), "Activités")
        
        if 'calendar' in accessible_tabs:
            tab_widget.addTab(CalendarTab(), "Calendrier")
        
        if 'leaves' in accessible_tabs:
            tab_widget.addTab(LeavesTab(), "Congés")
        
        if 'scheduling' in accessible_tabs:
            tab_widget.addTab(SchedulingTab(), "Ordonnancement")
        
        if 'analysis' in accessible_tabs:
            tab_widget.addTab(AnalysisTab(), "Retards")
        
        if 'reports' in accessible_tabs:
            tab_widget.addTab(ReportsTab(), "Rapports")
        
        if 'timetable' in accessible_tabs:
            tab_widget.addTab(TimetableTab(), "Emplois du temps")
        
        if 'users' in accessible_tabs:
            tab_widget.addTab(UsersTab(), "Utilisateurs")
        
        return tab_widget
    
    def create_status_bar(self):
        """Crée la barre de statut."""
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #F9FAFB;
                border-top: 1px solid #E5E7EB;
                padding: 5px 20px;
                color: #6B7280;
                font-size: 12px;
            }
        """)
        
        status_bar.showMessage(f"Connecté comme {self.role} | Système d'Ordonnancement Académique v1.0.0")
        self.setStatusBar(status_bar)
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        from PyQt5.QtWidgets import QDesktopWidget
        
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def get_nav_button_style(self, active):
        """Retourne le style d'un bouton de navigation."""
        if active:
            return """
                QPushButton {
                    background-color: white;
                    color: #1F2937;
                    border: none;
                    border-left: 3px solid #000;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: transparent;
                    color: #6B7280;
                    border: none;
                    border-left: 3px solid transparent;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                    color: #1F2937;
                }
            """
    
    def get_global_style(self):
        """Retourne le style global de l'application."""
        return """
            QMainWindow {
                background-color: #F9FAFB;
            }
            
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: #F3F4F6;
                height: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal {
                background: #D1D5DB;
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #9CA3AF;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """