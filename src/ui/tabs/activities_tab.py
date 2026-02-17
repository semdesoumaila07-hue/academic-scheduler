"""
Onglet de gestion des activités académiques - VERSION CORRIGÉE
Toutes les fonctionnalités sont maintenant connectées
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox,
    QProgressBar, QDialog, QFormLayout, QSpinBox, QTextEdit,
    QMessageBox, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, timedelta
import json


class ActivityDialog(QDialog):
    """Dialogue pour ajouter/modifier une activité académique"""
    
    def __init__(self, parent=None, activity_data=None, cohortes=None, enseignants=None):
        super().__init__(parent)
        self.activity_data = activity_data or {}
        self.cohortes = cohortes or []
        self.enseignants = enseignants or []
        self.edit_mode = activity_data is not None
        
        self.setWindowTitle("Modifier Activité" if self.edit_mode else "Nouvelle Activité")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface du dialogue"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier Activité" if self.edit_mode else "Nouvelle Activité Académique")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Code
        self.code_edit = QLineEdit(self.activity_data.get('code', ''))
        self.code_edit.setPlaceholderText("Ex: ALGO-301")
        self.code_edit.setFixedHeight(40)
        form.addRow("Code *:", self.code_edit)
        
        # Nom
        self.nom_edit = QLineEdit(self.activity_data.get('nom', ''))
        self.nom_edit.setPlaceholderText("Ex: Algorithmique avancée")
        self.nom_edit.setFixedHeight(40)
        form.addRow("Nom *:", self.nom_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["CM", "TD", "TP", "Examen", "Projet"])
        self.type_combo.setFixedHeight(40)
        if 'type' in self.activity_data:
            idx = self.type_combo.findText(self.activity_data['type'])
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        form.addRow("Type *:", self.type_combo)
        
        # Volume horaire
        self.volume_spin = QSpinBox()
        self.volume_spin.setRange(1, 200)
        self.volume_spin.setValue(self.activity_data.get('volume_heures', 20))
        self.volume_spin.setSuffix(" heures")
        self.volume_spin.setFixedHeight(40)
        form.addRow("Volume horaire *:", self.volume_spin)
        
        # Heures réalisées
        self.realise_spin = QSpinBox()
        self.realise_spin.setRange(0, 200)
        self.realise_spin.setValue(self.activity_data.get('heures_realisees', 0))
        self.realise_spin.setSuffix(" heures")
        self.realise_spin.setFixedHeight(40)
        form.addRow("Heures réalisées:", self.realise_spin)
        
        # Cohorte
        self.cohorte_combo = QComboBox()
        if self.cohortes:
            self.cohorte_combo.addItems([f"{c.get('nom', 'N/A')}" for c in self.cohortes])
        else:
            self.cohorte_combo.addItem("Aucune cohorte disponible")
        self.cohorte_combo.setFixedHeight(40)
        if 'cohorte' in self.activity_data:
            idx = self.cohorte_combo.findText(self.activity_data['cohorte'])
            if idx >= 0:
                self.cohorte_combo.setCurrentIndex(idx)
        form.addRow("Cohorte *:", self.cohorte_combo)
        
        # Enseignant
        self.enseignant_combo = QComboBox()
        if self.enseignants:
            self.enseignant_combo.addItems([f"{e.get('nom', '')} {e.get('prenom', '')}" for e in self.enseignants])
        else:
            self.enseignant_combo.addItem("Aucun enseignant disponible")
        self.enseignant_combo.setFixedHeight(40)
        if 'enseignant' in self.activity_data:
            idx = self.enseignant_combo.findText(self.activity_data['enseignant'])
            if idx >= 0:
                self.enseignant_combo.setCurrentIndex(idx)
        form.addRow("Enseignant *:", self.enseignant_combo)
        
        # Priorité
        self.priorite_combo = QComboBox()
        self.priorite_combo.addItems(["Normale", "Haute", "Urgente"])
        self.priorite_combo.setFixedHeight(40)
        if 'priorite' in self.activity_data:
            idx = self.priorite_combo.findText(self.activity_data['priorite'])
            if idx >= 0:
                self.priorite_combo.setCurrentIndex(idx)
        form.addRow("Priorité:", self.priorite_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Description de l'activité...")
        self.description_edit.setMaximumHeight(80)
        if 'description' in self.activity_data:
            self.description_edit.setPlainText(self.activity_data['description'])
        form.addRow("Description:", self.description_edit)
        
        layout.addLayout(form)
        layout.addSpacing(10)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def get_data(self):
        """Récupérer les données du formulaire"""
        volume = self.volume_spin.value()
        realise = self.realise_spin.value()
        progression = int((realise / volume) * 100) if volume > 0 else 0
        
        # Déterminer le statut
        if progression == 0:
            statut = "En attente"
        elif progression == 100:
            statut = "Terminée"
        elif progression > 0:
            statut = "En cours"
        else:
            statut = "Planifiée"
        
        return {
            'code': self.code_edit.text().strip(),
            'nom': self.nom_edit.text().strip(),
            'type': self.type_combo.currentText(),
            'volume_heures': volume,
            'heures_realisees': realise,
            'progression': progression,
            'cohorte': self.cohorte_combo.currentText(),
            'enseignant': self.enseignant_combo.currentText(),
            'priorite': self.priorite_combo.currentText(),
            'description': self.description_edit.toPlainText().strip(),
            'statut': statut
        }
    
    def validate(self):
        """Valider les données"""
        data = self.get_data()
        
        if not data['code']:
            QMessageBox.warning(self, "Validation", "Le code est obligatoire !")
            return False
        
        if not data['nom']:
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire !")
            return False
        
        if data['heures_realisees'] > data['volume_heures']:
            QMessageBox.warning(self, "Validation", 
                              "Les heures réalisées ne peuvent pas dépasser le volume horaire !")
            return False
        
        return True
    
    def accept(self):
        """Accepter si validation OK"""
        if self.validate():
            super().accept()


class ActivitiesTab(QWidget):
    """Onglet pour gérer les activités académiques - VERSION CORRIGÉE"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self.filtered_activities = []
        
        # Charger les données nécessaires
        self.load_related_data()
        
        self.init_ui()
        self.load_sample_data()
    
    def load_related_data(self):
        """Charger les cohortes et enseignants depuis les fichiers"""
        # Charger les cohortes
        try:
            import json
            from pathlib import Path
            
            # Cohortes
            structure_file = Path("data/structure.json")
            if structure_file.exists():
                with open(structure_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cohortes = data.get('cohortes', [])
            else:
                self.cohortes = []
            
            # Enseignants (créer quelques exemples si pas de fichier)
            self.enseignants = [
                {'nom': 'KABORE', 'prenom': 'Marie'},
                {'nom': 'TRAORE', 'prenom': 'Moussa'},
                {'nom': 'SAWADOGO', 'prenom': 'Fatimata'},
                {'nom': 'OUATTARA', 'prenom': 'Ibrahim'},
                {'nom': 'ZONGO', 'prenom': 'Aminata'}
            ]
        except:
            self.cohortes = []
            self.enseignants = []
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QVBoxLayout()
        title = QLabel("Activités Académiques")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Gérez les cours, TD, TP et leur ordonnancement")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Barre de recherche et filtres
        search_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher une activité...")
        self.search_box.setStyleSheet(self.get_input_style())
        self.search_box.setFixedHeight(45)
        self.search_box.textChanged.connect(self.apply_filters)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tous types", "CM", "TD", "TP", "Examen", "Projet"])
        self.filter_type.setStyleSheet(self.get_input_style())
        self.filter_type.setFixedHeight(45)
        self.filter_type.currentTextChanged.connect(self.apply_filters)
        
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tous statuts", "En attente", "Planifiée", "En cours", "Terminée"])
        self.filter_status.setStyleSheet(self.get_input_style())
        self.filter_status.setFixedHeight(45)
        self.filter_status.currentTextChanged.connect(self.apply_filters)
        
        search_layout.addWidget(self.search_box, 3)
        search_layout.addWidget(self.filter_type, 1)
        search_layout.addWidget(self.filter_status, 1)
        
        layout.addLayout(search_layout)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Nouvelle Activité")
        self.btn_add.setStyleSheet(self.get_button_style("#4CAF50"))
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self.add_activity)  # ✅ CONNECTÉ
        
        self.btn_urgent = QPushButton("⚠️ Activités Urgentes")
        self.btn_urgent.setStyleSheet(self.get_button_style("#FF5722"))
        self.btn_urgent.setFixedHeight(40)
        self.btn_urgent.clicked.connect(self.show_urgent_activities)  # ✅ CONNECTÉ
        
        self.btn_delays = QPushButton("📊 Calculer Retards")
        self.btn_delays.setStyleSheet(self.get_button_style("#FF9800"))
        self.btn_delays.setFixedHeight(40)
        self.btn_delays.clicked.connect(self.calculate_delays)  # ✅ CONNECTÉ
        
        self.btn_export = QPushButton("📥 Exporter")
        self.btn_export.setStyleSheet(self.get_button_style("#2196F3"))
        self.btn_export.setFixedHeight(40)
        self.btn_export.clicked.connect(self.export_activities)  # ✅ CONNECTÉ
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_urgent)
        btn_layout.addWidget(self.btn_delays)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Table des activités
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Code", "Nom", "Type", "Volume (h)", "Réalisé (h)", 
            "Progression", "Enseignant", "Cohorte", "Priorité", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(self.get_table_style())
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addWidget(self.table)
        
        # Statistiques en bas
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(15)
        
        self.stat1 = self.create_stat_box("Total activités", "0", "#2196F3")
        self.stat2 = self.create_stat_box("CM", "0", "#3F51B5")
        self.stat3 = self.create_stat_box("TD", "0", "#4CAF50")
        self.stat4 = self.create_stat_box("TP", "0", "#FF9800")
        self.stat5 = self.create_stat_box("Volume total", "0h", "#9C27B0")
        self.stat6 = self.create_stat_box("Réalisées", "0h", "#4CAF50")
        
        self.stats_layout.addWidget(self.stat1)
        self.stats_layout.addWidget(self.stat2)
        self.stats_layout.addWidget(self.stat3)
        self.stats_layout.addWidget(self.stat4)
        self.stats_layout.addWidget(self.stat5)
        self.stats_layout.addWidget(self.stat6)
        
        layout.addLayout(self.stats_layout)
    
    def load_sample_data(self):
        """Charger des données exemple"""
        self.activities = [
            {
                'id': 1,
                'code': 'ALGO-301',
                'nom': 'Algorithmique avancée',
                'type': 'CM',
                'volume_heures': 30,
                'heures_realisees': 30,
                'progression': 100,
                'enseignant': 'KABORE Marie',
                'cohorte': 'L3 Info',
                'priorite': 'Normale',
                'statut': 'Terminée',
                'description': 'Cours d\'algorithmique niveau avancé'
            },
            {
                'id': 2,
                'code': 'ALGO-TD-301',
                'nom': 'TD Algorithmique',
                'type': 'TD',
                'volume_heures': 20,
                'heures_realisees': 20,
                'progression': 100,
                'enseignant': 'KABORE Marie',
                'cohorte': 'L3 Info',
                'priorite': 'Normale',
                'statut': 'Terminée',
                'description': 'Travaux dirigés d\'algorithmique'
            },
            {
                'id': 3,
                'code': 'BD-301',
                'nom': 'Bases de données',
                'type': 'CM',
                'volume_heures': 25,
                'heures_realisees': 15,
                'progression': 60,
                'enseignant': 'TRAORE Moussa',
                'cohorte': 'L3 Info',
                'priorite': 'Haute',
                'statut': 'En cours',
                'description': 'Introduction aux bases de données relationnelles'
            },
            {
                'id': 4,
                'code': 'BD-TP-301',
                'nom': 'TP Bases de données',
                'type': 'TP',
                'volume_heures': 20,
                'heures_realisees': 10,
                'progression': 50,
                'enseignant': 'TRAORE Moussa',
                'cohorte': 'L3 Info',
                'priorite': 'Urgente',
                'statut': 'En cours',
                'description': 'Travaux pratiques sur PostgreSQL'
            },
            {
                'id': 5,
                'code': 'WEB-301',
                'nom': 'Développement Web',
                'type': 'CM',
                'volume_heures': 25,
                'heures_realisees': 0,
                'progression': 0,
                'enseignant': 'OUATTARA Ibrahim',
                'cohorte': 'L3 Info',
                'priorite': 'Urgente',
                'statut': 'En attente',
                'description': 'HTML, CSS, JavaScript'
            },
        ]
        self.apply_filters()
    
    def apply_filters(self):
        """Appliquer les filtres de recherche"""
        search_text = self.search_box.text().lower()
        filter_type = self.filter_type.currentText()
        filter_status = self.filter_status.currentText()
        
        self.filtered_activities = []
        
        for activity in self.activities:
            # Filtre de recherche
            if search_text:
                searchable = f"{activity['code']} {activity['nom']} {activity['enseignant']} {activity['cohorte']}".lower()
                if search_text not in searchable:
                    continue
            
            # Filtre de type
            if filter_type != "Tous types" and activity['type'] != filter_type:
                continue
            
            # Filtre de statut
            if filter_status != "Tous statuts" and activity['statut'] != filter_status:
                continue
            
            self.filtered_activities.append(activity)
        
        self.refresh_table()
        self.update_statistics()
    
    def refresh_table(self):
        """Rafraîchir l'affichage de la table"""
        self.table.setRowCount(len(self.filtered_activities))
        
        for i, activity in enumerate(self.filtered_activities):
            # Code
            self.table.setItem(i, 0, QTableWidgetItem(activity['code']))
            
            # Nom
            self.table.setItem(i, 1, QTableWidgetItem(activity['nom']))
            
            # Type
            type_item = QTableWidgetItem(activity['type'])
            if activity['type'] == "CM":
                type_item.setBackground(QColor("#E3F2FD"))
            elif activity['type'] == "TD":
                type_item.setBackground(QColor("#E8F5E9"))
            elif activity['type'] == "TP":
                type_item.setBackground(QColor("#FFF3E0"))
            self.table.setItem(i, 2, type_item)
            
            # Volume
            self.table.setItem(i, 3, QTableWidgetItem(f"{activity['volume_heures']}h"))
            
            # Réalisé
            self.table.setItem(i, 4, QTableWidgetItem(f"{activity['heures_realisees']}h"))
            
            # Progression (barre)
            progress = QProgressBar()
            progress.setValue(activity['progression'])
            progress.setTextVisible(True)
            progress.setFormat(f"{activity['progression']}%")
            
            if activity['progression'] == 100:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
            elif activity['progression'] > 50:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
            else:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
            
            self.table.setCellWidget(i, 5, progress)
            
            # Enseignant
            self.table.setItem(i, 6, QTableWidgetItem(activity['enseignant']))
            
            # Cohorte
            self.table.setItem(i, 7, QTableWidgetItem(activity['cohorte']))
            
            # Priorité
            priorite_item = QTableWidgetItem(activity['priorite'])
            if activity['priorite'] == "Urgente":
                priorite_item.setBackground(QColor("#FFCDD2"))
            elif activity['priorite'] == "Haute":
                priorite_item.setBackground(QColor("#FFECB3"))
            self.table.setItem(i, 8, priorite_item)
            
            # Actions
            actions_widget = self.create_action_buttons(activity)
            self.table.setCellWidget(i, 9, actions_widget)
    
    def create_action_buttons(self, activity):
        """Créer les boutons d'action pour une ligne"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                border-radius: 4px;
            }
        """)
        btn_edit.clicked.connect(lambda: self.edit_activity(activity))
        
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(30, 30)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
                border-radius: 4px;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_activity(activity))
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget
    
    def update_statistics(self):
        """Mettre à jour les statistiques"""
        total = len(self.filtered_activities)
        cm = sum(1 for a in self.filtered_activities if a['type'] == 'CM')
        td = sum(1 for a in self.filtered_activities if a['type'] == 'TD')
        tp = sum(1 for a in self.filtered_activities if a['type'] == 'TP')
        volume_total = sum(a['volume_heures'] for a in self.filtered_activities)
        realisees = sum(a['heures_realisees'] for a in self.filtered_activities)
        
        self.update_stat_box(self.stat1, str(total))
        self.update_stat_box(self.stat2, str(cm))
        self.update_stat_box(self.stat3, str(td))
        self.update_stat_box(self.stat4, str(tp))
        self.update_stat_box(self.stat5, f"{volume_total}h")
        self.update_stat_box(self.stat6, f"{realisees}h")
    
    def update_stat_box(self, box, value):
        """Mettre à jour une boîte de statistique"""
        labels = box.findChildren(QLabel)
        if labels:
            labels[0].setText(value)
    
    # ==========================================
    # MÉTHODES D'ACTION
    # ==========================================
    
    def add_activity(self):
        """Ajouter une nouvelle activité"""
        dialog = ActivityDialog(self, cohortes=self.cohortes, enseignants=self.enseignants)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Générer un nouvel ID
            new_id = max([a['id'] for a in self.activities], default=0) + 1
            data['id'] = new_id
            
            # Ajouter à la liste
            self.activities.append(data)
            
            # Rafraîchir
            self.apply_filters()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ L'activité '{data['nom']}' a été ajoutée avec succès !"
            )
    
    def edit_activity(self, activity):
        """Modifier une activité"""
        dialog = ActivityDialog(self, activity, self.cohortes, self.enseignants)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            activity.update(data)
            
            self.apply_filters()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ L'activité '{activity['nom']}' a été modifiée avec succès !"
            )
    
    def delete_activity(self, activity):
        """Supprimer une activité"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer l'activité '{activity['nom']}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.activities.remove(activity)
            self.apply_filters()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ L'activité '{activity['nom']}' a été supprimée avec succès !"
            )
    
    def show_urgent_activities(self):
        """Afficher uniquement les activités urgentes"""
        urgent = [a for a in self.activities if a['priorite'] == 'Urgente']
        
        if not urgent:
            QMessageBox.information(
                self,
                "Activités Urgentes",
                "✅ Aucune activité urgente pour le moment !"
            )
            return
        
        # Créer un message détaillé
        message = f"⚠️ {len(urgent)} activité(s) urgente(s) détectée(s) :\n\n"
        
        for a in urgent:
            status = "🔴" if a['progression'] < 50 else "🟡"
            message += f"{status} {a['code']} - {a['nom']}\n"
            message += f"   Progression: {a['progression']}% | Enseignant: {a['enseignant']}\n\n"
        
        QMessageBox.warning(
            self,
            "Activités Urgentes",
            message
        )
        
        # Filtrer pour afficher seulement les urgentes
        self.filter_status.setCurrentText("Tous statuts")
        self.search_box.clear()
        self.filtered_activities = urgent
        self.refresh_table()
    
    def calculate_delays(self):
        """Calculer les retards des activités"""
        total_volume = sum(a['volume_heures'] for a in self.activities)
        total_realise = sum(a['heures_realisees'] for a in self.activities)
        retard_heures = total_volume - total_realise
        
        pourcentage_global = int((total_realise / total_volume) * 100) if total_volume > 0 else 0
        
        # Calculer les activités en retard
        en_retard = []
        for a in self.activities:
            if a['progression'] < 100 and a['statut'] != 'En attente':
                retard_act = a['volume_heures'] - a['heures_realisees']
                en_retard.append({
                    'nom': a['nom'],
                    'retard': retard_act,
                    'progression': a['progression']
                })
        
        # Créer le rapport
        message = "📊 RAPPORT DE RETARDS\n\n"
        message += f"Volume horaire total: {total_volume}h\n"
        message += f"Heures réalisées: {total_realise}h\n"
        message += f"Retard global: {retard_heures}h\n"
        message += f"Progression globale: {pourcentage_global}%\n\n"
        
        if en_retard:
            message += f"⚠️ {len(en_retard)} activité(s) en retard:\n\n"
            for item in sorted(en_retard, key=lambda x: x['retard'], reverse=True)[:5]:
                message += f"• {item['nom']}\n"
                message += f"  Retard: {item['retard']}h ({item['progression']}% complété)\n\n"
        else:
            message += "✅ Aucune activité en retard !"
        
        QMessageBox.information(
            self,
            "Calcul des Retards",
            message
        )
    
    def export_activities(self):
        """Exporter les activités"""
        reply = QMessageBox.question(
            self,
            "Format d'export",
            "Choisissez le format d'export :\n\n"
            "Oui = Excel (.xlsx)\n"
            "Non = JSON (.json)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.export_to_excel()
        else:
            self.export_to_json()
    
    def export_to_excel(self):
        """Exporter en Excel"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en Excel",
            f"activites_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not filename:
            return
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Activités"
            
            # En-têtes
            headers = ["Code", "Nom", "Type", "Volume (h)", "Réalisé (h)", 
                      "Progression (%)", "Enseignant", "Cohorte", "Priorité", "Statut"]
            ws.append(headers)
            
            # Style des en-têtes
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Données
            for activity in self.filtered_activities:
                ws.append([
                    activity['code'],
                    activity['nom'],
                    activity['type'],
                    activity['volume_heures'],
                    activity['heures_realisees'],
                    activity['progression'],
                    activity['enseignant'],
                    activity['cohorte'],
                    activity['priorite'],
                    activity['statut']
                ])
            
            # Ajuster les colonnes
            for column in ws.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column[0].column_letter].width = adjusted_width
            
            wb.save(filename)
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Export Excel réussi !\n\nFichier : {filename}\nActivités exportées : {len(self.filtered_activities)}"
            )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Module manquant",
                "Le module 'openpyxl' n'est pas installé.\n\n"
                "Installez-le avec : pip install openpyxl"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export Excel :\n\n{str(e)}"
            )
    
    def export_to_json(self):
        """Exporter en JSON"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en JSON",
            f"activites_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.filtered_activities, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Export JSON réussi !\n\nFichier : {filename}\nActivités exportées : {len(self.filtered_activities)}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export JSON :\n\n{str(e)}"
            )
    
    # ==========================================
    # STYLES
    # ==========================================
    
    def create_stat_box(self, label, value, color):
        """Crée une boîte de statistique."""
        box = QWidget()
        box.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(box)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 11px; color: white;")
        label_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return box
    
    def get_input_style(self):
        """Style des inputs."""
        return """
            QLineEdit, QComboBox {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
        """
    
    def get_button_style(self, color):
        """Style des boutons."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """
    
    def get_table_style(self):
        """Style de la table."""
        return """
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #333;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """