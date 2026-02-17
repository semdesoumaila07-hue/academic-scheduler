"""
Dialogue pour ajouter/modifier une université.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt


class UniversityDialog(QDialog):
    """Dialogue pour gérer une université."""
    
    def __init__(self, parent=None, university_data=None):
        super().__init__(parent)
        self.university_data = university_data
        self.is_edit_mode = university_data is not None
        
        self.setWindowTitle("Modifier l'université" if self.is_edit_mode else "Nouvelle université")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self.init_ui()
        
        # Si mode édition, remplir les champs
        if self.is_edit_mode:
            self.fill_fields()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier l'université" if self.is_edit_mode else "Nouvelle université")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1F2937;")
        layout.addWidget(title)
        
        # Nom
        self.name_input = self.create_input_field(layout, "Nom de l'université *", "Ex: Université Thomas Sankara")
        
        # Code
        self.code_input = self.create_input_field(layout, "Code *", "Ex: UTS")
        
        # Adresse
        self.address_input = self.create_input_field(layout, "Adresse *", "Ex: Avenue de l'Indépendance")
        
        # Ville
        self.city_input = self.create_input_field(layout, "Ville *", "Ex: Ouagadougou")
        
        # Pays
        self.country_input = self.create_input_field(layout, "Pays", "Ex: Burkina Faso")
        self.country_input.setText("Burkina Faso")  # Valeur par défaut
        
        layout.addSpacing(10)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setStyleSheet(self.get_secondary_button_style())
        btn_cancel.setFixedHeight(45)
        btn_cancel.setFixedWidth(120)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        
        btn_save = QPushButton("Enregistrer")
        btn_save.setStyleSheet(self.get_primary_button_style())
        btn_save.setFixedHeight(45)
        btn_save.setFixedWidth(140)
        btn_save.clicked.connect(self.save)
        btn_save.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def create_input_field(self, parent_layout, label_text, placeholder):
        """Crée un champ de saisie avec label."""
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        parent_layout.addWidget(label)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #000;
            }
        """)
        input_field.setFixedHeight(45)
        parent_layout.addWidget(input_field)
        
        return input_field
    
    def fill_fields(self):
        """Remplit les champs en mode édition."""
        if self.university_data:
            self.name_input.setText(self.university_data.get('name', ''))
            self.code_input.setText(self.university_data.get('code', ''))
            self.address_input.setText(self.university_data.get('address', ''))
            self.city_input.setText(self.university_data.get('city', ''))
            self.country_input.setText(self.university_data.get('country', 'Burkina Faso'))
    
    def save(self):
        """Valide et sauvegarde les données."""
        # Récupérer les valeurs
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()
        address = self.address_input.text().strip()
        city = self.city_input.text().strip()
        country = self.country_input.text().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom de l'université est requis.")
            self.name_input.setFocus()
            return
        
        if not code:
            QMessageBox.warning(self, "Erreur", "Le code est requis.")
            self.code_input.setFocus()
            return
        
        if not address:
            QMessageBox.warning(self, "Erreur", "L'adresse est requise.")
            self.address_input.setFocus()
            return
        
        if not city:
            QMessageBox.warning(self, "Erreur", "La ville est requise.")
            self.city_input.setFocus()
            return
        
        # Stocker les données
        self.result_data = {
            'name': name,
            'code': code,
            'address': address,
            'city': city,
            'country': country or 'Burkina Faso'
        }
        
        # Accepter le dialogue
        self.accept()
    
    def get_data(self):
        """Retourne les données saisies."""
        return getattr(self, 'result_data', None)
    
    def get_primary_button_style(self):
        """Style du bouton principal."""
        return """
            QPushButton {
                background-color: #000;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """
    
    def get_secondary_button_style(self):
        """Style du bouton secondaire."""
        return """
            QPushButton {
                background: white;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #F9FAFB;
            }
        """