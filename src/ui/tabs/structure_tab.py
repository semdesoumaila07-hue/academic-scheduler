"""
Onglet Structure - PyQt5 - VERSION DESIGN MODERNE
UC1: Configurer structure universitaire
Design identique à l'onglet Enseignants
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QTabWidget,
    QDialog, QLineEdit, QComboBox, QMessageBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
from pathlib import Path
from datetime import datetime


class StructureTab(QWidget):
    """Onglet de gestion de la structure universitaire - DESIGN MODERNE."""
    
    def __init__(self):
        super().__init__()
        
        # Données
        self.data = {
            "universites": [],
            "ufrs": [],
            "programmes": [],
            "cohortes": []
        }
        
        self.load_data()
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # ==========================================
        # EN-TÊTE
        # ==========================================
        header_layout = QVBoxLayout()
        
        title = QLabel("Structure Universitaire")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Gestion des universités, UFR, parcours et classes")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # ==========================================
        # BARRE DE RECHERCHE ET FILTRES
        # ==========================================
        search_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher dans la structure...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
        """)
        self.search_box.setFixedHeight(45)
        self.search_box.textChanged.connect(self.apply_search)
        
        self.filter_box = QComboBox()
        self.filter_box.addItems(["Toutes", "Universités", "UFR", "Parcours", "Classes"])
        self.filter_box.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background: white;
                min-width: 150px;
            }
        """)
        self.filter_box.setFixedHeight(45)
        self.filter_box.currentTextChanged.connect(self.apply_search)
        
        search_layout.addWidget(self.search_box, 3)
        search_layout.addWidget(self.filter_box, 1)
        
        layout.addLayout(search_layout)
        
        # ==========================================
        # BOUTONS D'ACTION
        # ==========================================
        btn_layout = QHBoxLayout()
        
        btn_add_univ = QPushButton("➕ Nouvelle Université")
        btn_add_univ.setStyleSheet(self.get_button_style("#3498db"))
        btn_add_univ.setFixedHeight(40)
        btn_add_univ.clicked.connect(self.add_universite)
        
        btn_add_ufr = QPushButton("➕ Nouvelle UFR")
        btn_add_ufr.setStyleSheet(self.get_button_style("#27ae60"))
        btn_add_ufr.setFixedHeight(40)
        btn_add_ufr.clicked.connect(self.add_ufr)
        
        btn_add_prog = QPushButton("➕ Nouveau Parcours")
        btn_add_prog.setStyleSheet(self.get_button_style("#8e44ad"))
        btn_add_prog.setFixedHeight(40)
        btn_add_prog.clicked.connect(self.add_programme)
        
        btn_add_classe = QPushButton("➕ Nouvelle Classe")
        btn_add_classe.setStyleSheet(self.get_button_style("#e67e22"))
        btn_add_classe.setFixedHeight(40)
        btn_add_classe.clicked.connect(self.add_cohorte)
        
        btn_layout.addWidget(btn_add_univ)
        btn_layout.addWidget(btn_add_ufr)
        btn_layout.addWidget(btn_add_prog)
        btn_layout.addWidget(btn_add_classe)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # ==========================================
        # ONGLETS
        # ==========================================
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #F5F5F5;
                color: #666;
                padding: 12px 30px;
                margin-right: 2px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                color: #1976D2;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #E3F2FD;
            }
        """)
        
        # Créer les 4 onglets
        self.tab_universites = self.create_universites_tab()
        self.tab_ufr = self.create_ufr_tab()
        self.tab_parcours = self.create_parcours_tab()
        self.tab_classes = self.create_classes_tab()
        
        self.tab_widget.addTab(self.tab_universites, "🏛️  Universités")
        self.tab_widget.addTab(self.tab_ufr, "🎓  UFR")
        self.tab_widget.addTab(self.tab_parcours, "📚  Parcours")
        self.tab_widget.addTab(self.tab_classes, "👥  Classes")
        
        layout.addWidget(self.tab_widget)
        
        # ==========================================
        # STATISTIQUES EN BAS
        # ==========================================
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        self.stat1 = self.create_stat_box("Universités", "0", "#3498db")
        self.stat2 = self.create_stat_box("UFR", "0", "#27ae60")
        self.stat3 = self.create_stat_box("Parcours", "0", "#8e44ad")
        self.stat4 = self.create_stat_box("Classes", "0", "#e67e22")
        
        self.stats_layout.addWidget(self.stat1)
        self.stats_layout.addWidget(self.stat2)
        self.stats_layout.addWidget(self.stat3)
        self.stats_layout.addWidget(self.stat4)
        
        layout.addLayout(self.stats_layout)
        
        # Rafraîchir l'affichage initial
        self.refresh_all_tabs()
        self.update_statistics()
    
    # ==========================================
    # ONGLET UNIVERSITÉS
    # ==========================================
    
    def create_universites_tab(self):
        """Crée l'onglet Universités."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tableau
        self.table_universites = self.create_table(["Nom", "Code", "Ville", "UFRs", "Actions"])
        layout.addWidget(self.table_universites)
        
        return widget
    
    def refresh_universites_table(self):
        """Rafraîchir le tableau des universités."""
        self.table_universites.setRowCount(0)
        
        for univ in self.data["universites"]:
            row = self.table_universites.rowCount()
            self.table_universites.insertRow(row)
            
            # Nom
            self.table_universites.setItem(row, 0, QTableWidgetItem(univ.get('nom', 'N/A')))
            
            # Code
            self.table_universites.setItem(row, 1, QTableWidgetItem(univ.get('code', 'N/A')))
            
            # Ville
            self.table_universites.setItem(row, 2, QTableWidgetItem(univ.get('ville', 'N/A')))
            
            # Nombre d'UFR
            nb_ufrs = len([u for u in self.data["ufrs"] if u.get("universite_id") == univ.get("id")])
            self.table_universites.setItem(row, 3, QTableWidgetItem(f"{nb_ufrs} UFR"))
            
            # Actions
            actions_widget = self.create_action_buttons(
                lambda u=univ: self.edit_universite(u),
                lambda u=univ: self.delete_universite(u)
            )
            self.table_universites.setCellWidget(row, 4, actions_widget)
    
    # ==========================================
    # ONGLET UFR
    # ==========================================
    
    def create_ufr_tab(self):
        """Crée l'onglet UFR."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tableau
        self.table_ufr = self.create_table(["Nom", "Code", "Université", "Directeur", "Parcours", "Actions"])
        layout.addWidget(self.table_ufr)
        
        return widget
    
    def refresh_ufr_table(self):
        """Rafraîchir le tableau des UFR."""
        self.table_ufr.setRowCount(0)
        
        for ufr in self.data["ufrs"]:
            row = self.table_ufr.rowCount()
            self.table_ufr.insertRow(row)
            
            # Nom
            self.table_ufr.setItem(row, 0, QTableWidgetItem(ufr.get('nom', 'N/A')))
            
            # Code
            self.table_ufr.setItem(row, 1, QTableWidgetItem(ufr.get('code', 'N/A')))
            
            # Université
            univ_nom = "N/A"
            for u in self.data["universites"]:
                if u.get('id') == ufr.get('universite_id'):
                    univ_nom = u.get('nom', 'N/A')
                    break
            self.table_ufr.setItem(row, 2, QTableWidgetItem(univ_nom))
            
            # Directeur
            self.table_ufr.setItem(row, 3, QTableWidgetItem(ufr.get('directeur', 'N/A')))
            
            # Nombre de parcours
            nb_prog = len([p for p in self.data["programmes"] if p.get("ufr_id") == ufr.get("id")])
            self.table_ufr.setItem(row, 4, QTableWidgetItem(f"{nb_prog} Parcours"))
            
            # Actions
            actions_widget = self.create_action_buttons(
                lambda u=ufr: self.edit_ufr(u),
                lambda u=ufr: self.delete_ufr(u)
            )
            self.table_ufr.setCellWidget(row, 5, actions_widget)
    
    # ==========================================
    # ONGLET PARCOURS
    # ==========================================
    
    def create_parcours_tab(self):
        """Crée l'onglet Parcours."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tableau
        self.table_parcours = self.create_table(["Nom", "Code", "Niveau", "UFR", "Classes", "Actions"])
        layout.addWidget(self.table_parcours)
        
        return widget
    
    def refresh_parcours_table(self):
        """Rafraîchir le tableau des parcours."""
        self.table_parcours.setRowCount(0)
        
        for prog in self.data["programmes"]:
            row = self.table_parcours.rowCount()
            self.table_parcours.insertRow(row)
            
            # Nom
            self.table_parcours.setItem(row, 0, QTableWidgetItem(prog.get('nom', 'N/A')))
            
            # Code
            self.table_parcours.setItem(row, 1, QTableWidgetItem(prog.get('code', 'N/A')))
            
            # Niveau
            self.table_parcours.setItem(row, 2, QTableWidgetItem(prog.get('niveau', 'N/A')))
            
            # UFR
            ufr_nom = "N/A"
            for u in self.data["ufrs"]:
                if u.get('id') == prog.get('ufr_id'):
                    ufr_nom = u.get('nom', 'N/A')
                    break
            self.table_parcours.setItem(row, 3, QTableWidgetItem(ufr_nom))
            
            # Nombre de classes
            nb_classes = len([c for c in self.data["cohortes"] if c.get("programme_id") == prog.get("id")])
            self.table_parcours.setItem(row, 4, QTableWidgetItem(f"{nb_classes} Classes"))
            
            # Actions
            actions_widget = self.create_action_buttons(
                lambda p=prog: self.edit_programme(p),
                lambda p=prog: self.delete_programme(p)
            )
            self.table_parcours.setCellWidget(row, 5, actions_widget)
    
    # ==========================================
    # ONGLET CLASSES
    # ==========================================
    
    def create_classes_tab(self):
        """Crée l'onglet Classes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Tableau
        self.table_classes = self.create_table(["Nom", "Parcours", "Année", "Semestre", "Effectif", "Actions"])
        layout.addWidget(self.table_classes)
        
        return widget
    
    def refresh_classes_table(self):
        """Rafraîchir le tableau des classes."""
        self.table_classes.setRowCount(0)
        
        for cohorte in self.data["cohortes"]:
            row = self.table_classes.rowCount()
            self.table_classes.insertRow(row)
            
            # Nom
            self.table_classes.setItem(row, 0, QTableWidgetItem(cohorte.get('nom', 'N/A')))
            
            # Parcours
            prog_nom = "N/A"
            for p in self.data["programmes"]:
                if p.get('id') == cohorte.get('programme_id'):
                    prog_nom = f"{p.get('nom', 'N/A')} ({p.get('niveau', '')})"
                    break
            self.table_classes.setItem(row, 1, QTableWidgetItem(prog_nom))
            
            # Année
            self.table_classes.setItem(row, 2, QTableWidgetItem(cohorte.get('annee_academique', 'N/A')))
            
            # Semestre
            self.table_classes.setItem(row, 3, QTableWidgetItem(cohorte.get('semestre', 'N/A')))
            
            # Effectif
            effectif_item = QTableWidgetItem(f"{cohorte.get('effectif', 0)} étudiants")
            if cohorte.get('effectif', 0) > 50:
                effectif_item.setBackground(Qt.yellow)
            self.table_classes.setItem(row, 4, effectif_item)
            
            # Actions
            actions_widget = self.create_action_buttons(
                lambda c=cohorte: self.edit_cohorte(c),
                lambda c=cohorte: self.delete_cohorte(c)
            )
            self.table_classes.setCellWidget(row, 5, actions_widget)
    
    # ==========================================
    # RECHERCHE ET FILTRES
    # ==========================================
    
    def apply_search(self):
        """Appliquer la recherche et les filtres."""
        search_text = self.search_box.text().lower()
        filter_type = self.filter_box.currentText()
        
        # TODO: Implémenter la recherche dans les tableaux
        # Pour l'instant, juste rafraîchir
        self.refresh_all_tabs()
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def create_table(self, headers):
        """Crée un tableau avec en-têtes."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Style du tableau (identique à teachers_tab)
        table.setStyleSheet("""
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
        """)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        return table
    
    def create_action_buttons(self, edit_callback, delete_callback):
        """Crée les boutons d'action pour une ligne."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Bouton Modifier
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(35, 35)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                border-radius: 5px;
            }
        """)
        btn_edit.clicked.connect(edit_callback)
        
        # Bouton Supprimer
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(35, 35)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
                border-radius: 5px;
            }
        """)
        btn_delete.clicked.connect(delete_callback)
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget
    
    def create_stat_box(self, label, value, color):
        """Crée une petite boîte de statistique (comme teachers_tab)."""
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
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 12px; color: white;")
        label_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return box
    
    def update_stat_box(self, box, value):
        """Mettre à jour une boîte de statistique."""
        labels = box.findChildren(QLabel)
        if labels:
            labels[0].setText(value)
    
    def get_button_style(self, color):
        """Style des boutons (identique à teachers_tab)."""
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
    
    def get_existing_codes(self, entity_type):
        """Obtenir la liste des codes existants."""
        return [item.get('code', '') for item in self.data.get(entity_type, [])]
    
    def refresh_all_tabs(self):
        """Rafraîchir tous les tableaux."""
        self.refresh_universites_table()
        self.refresh_ufr_table()
        self.refresh_parcours_table()
        self.refresh_classes_table()
        
        # Mettre à jour les compteurs dans les onglets
        self.tab_widget.setTabText(0, f"🏛️  Universités ({len(self.data['universites'])})")
        self.tab_widget.setTabText(1, f"🎓  UFR ({len(self.data['ufrs'])})")
        self.tab_widget.setTabText(2, f"📚  Parcours ({len(self.data['programmes'])})")
        self.tab_widget.setTabText(3, f"👥  Classes ({len(self.data['cohortes'])})")
    
    def update_statistics(self):
        """Mettre à jour les statistiques en bas."""
        self.update_stat_box(self.stat1, str(len(self.data["universites"])))
        self.update_stat_box(self.stat2, str(len(self.data["ufrs"])))
        self.update_stat_box(self.stat3, str(len(self.data["programmes"])))
        self.update_stat_box(self.stat4, str(len(self.data["cohortes"])))
    
    # ==========================================
    # FONCTIONS D'AJOUT
    # ==========================================
    
    def add_universite(self):
        """Ajouter une nouvelle université."""
        dialog = UniversiteDialog(self, existing_codes=self.get_existing_codes("universites"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            result["id"] = f"univ_{len(self.data['universites']) + 1}_{datetime.now().timestamp()}"
            self.data["universites"].append(result)
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Université '{result['nom']}' ajoutée avec succès !")
    
    def add_ufr(self):
        """Ajouter une nouvelle UFR."""
        if not self.data["universites"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer une université !")
            return
        
        dialog = UFRDialog(self, self.data["universites"], existing_codes=self.get_existing_codes("ufrs"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            result["id"] = f"ufr_{len(self.data['ufrs']) + 1}_{datetime.now().timestamp()}"
            self.data["ufrs"].append(result)
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ UFR '{result['nom']}' ajoutée avec succès !")
    
    def add_programme(self):
        """Ajouter un nouveau programme."""
        if not self.data["ufrs"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer une UFR !")
            return
        
        dialog = ProgrammeDialog(self, self.data["ufrs"], existing_codes=self.get_existing_codes("programmes"))
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            result["id"] = f"prog_{len(self.data['programmes']) + 1}_{datetime.now().timestamp()}"
            self.data["programmes"].append(result)
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Parcours '{result['nom']}' ajouté avec succès !")
    
    def add_cohorte(self):
        """Ajouter une nouvelle cohorte."""
        if not self.data["programmes"]:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord créer un parcours !")
            return
        
        dialog = CohorteDialog(self, self.data["programmes"])
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            result["id"] = f"cohorte_{len(self.data['cohortes']) + 1}_{datetime.now().timestamp()}"
            self.data["cohortes"].append(result)
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Classe '{result['nom']}' ajoutée avec succès !")
    
    # ==========================================
    # FONCTIONS D'ÉDITION
    # ==========================================
    
    def edit_universite(self, univ):
        """Éditer une université."""
        existing_codes = [u['code'] for u in self.data["universites"] if u.get('id') != univ.get('id')]
        dialog = UniversiteDialog(self, data=univ, existing_codes=existing_codes)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            for key, value in result.items():
                univ[key] = value
            self.save_data()
            self.refresh_all_tabs()
            QMessageBox.information(self, "Succès", f"✅ Université '{univ['nom']}' modifiée avec succès !")
    
    def edit_ufr(self, ufr):
        """Éditer une UFR."""
        existing_codes = [u['code'] for u in self.data["ufrs"] if u.get('id') != ufr.get('id')]
        dialog = UFRDialog(self, self.data["universites"], data=ufr, existing_codes=existing_codes)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            for key, value in result.items():
                ufr[key] = value
            self.save_data()
            self.refresh_all_tabs()
            QMessageBox.information(self, "Succès", f"✅ UFR '{ufr['nom']}' modifiée avec succès !")
    
    def edit_programme(self, prog):
        """Éditer un programme."""
        existing_codes = [p['code'] for p in self.data["programmes"] if p.get('id') != prog.get('id')]
        dialog = ProgrammeDialog(self, self.data["ufrs"], data=prog, existing_codes=existing_codes)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            for key, value in result.items():
                prog[key] = value
            self.save_data()
            self.refresh_all_tabs()
            QMessageBox.information(self, "Succès", f"✅ Parcours '{prog['nom']}' modifié avec succès !")
    
    def edit_cohorte(self, cohorte):
        """Éditer une cohorte."""
        dialog = CohorteDialog(self, self.data["programmes"], data=cohorte)
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_data()
            for key, value in result.items():
                cohorte[key] = value
            self.save_data()
            self.refresh_all_tabs()
            QMessageBox.information(self, "Succès", f"✅ Classe '{cohorte['nom']}' modifiée avec succès !")
    
    # ==========================================
    # FONCTIONS DE SUPPRESSION
    # ==========================================
    
    def delete_universite(self, univ):
        """Supprimer une université."""
        nb_ufrs = len([u for u in self.data["ufrs"] if u.get("universite_id") == univ.get("id")])
        
        msg = f"Êtes-vous sûr de vouloir supprimer l'université '{univ.get('nom')}' ?"
        if nb_ufrs > 0:
            msg += f"\n\n⚠️ Cette action supprimera également {nb_ufrs} UFR associée(s)."
        msg += "\n\nCette action est irréversible."
        
        reply = QMessageBox.question(
            self, 
            "Confirmation de suppression",
            msg, 
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer en cascade
            self.data["universites"].remove(univ)
            self.data["ufrs"] = [u for u in self.data["ufrs"] if u.get("universite_id") != univ.get("id")]
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Université '{univ['nom']}' supprimée avec succès !")
    
    def delete_ufr(self, ufr):
        """Supprimer une UFR."""
        nb_prog = len([p for p in self.data["programmes"] if p.get("ufr_id") == ufr.get("id")])
        
        msg = f"Êtes-vous sûr de vouloir supprimer l'UFR '{ufr.get('nom')}' ?"
        if nb_prog > 0:
            msg += f"\n\n⚠️ Cette action supprimera également {nb_prog} parcours associé(s)."
        msg += "\n\nCette action est irréversible."
        
        reply = QMessageBox.question(
            self,
            "Confirmation de suppression",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data["ufrs"].remove(ufr)
            self.data["programmes"] = [p for p in self.data["programmes"] if p.get("ufr_id") != ufr.get("id")]
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ UFR '{ufr['nom']}' supprimée avec succès !")
    
    def delete_programme(self, prog):
        """Supprimer un programme."""
        nb_cohortes = len([c for c in self.data["cohortes"] if c.get("programme_id") == prog.get("id")])
        
        msg = f"Êtes-vous sûr de vouloir supprimer le parcours '{prog.get('nom')}' ?"
        if nb_cohortes > 0:
            msg += f"\n\n⚠️ Cette action supprimera également {nb_cohortes} classe(s) associée(s)."
        msg += "\n\nCette action est irréversible."
        
        reply = QMessageBox.question(
            self,
            "Confirmation de suppression",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data["programmes"].remove(prog)
            self.data["cohortes"] = [c for c in self.data["cohortes"] if c.get("programme_id") != prog.get("id")]
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Parcours '{prog['nom']}' supprimé avec succès !")
    
    def delete_cohorte(self, cohorte):
        """Supprimer une cohorte."""
        reply = QMessageBox.question(
            self,
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer la classe '{cohorte.get('nom')}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data["cohortes"].remove(cohorte)
            self.save_data()
            self.refresh_all_tabs()
            self.update_statistics()
            QMessageBox.information(self, "Succès", f"✅ Classe '{cohorte['nom']}' supprimée avec succès !")
    
    # ==========================================
    # PERSISTANCE DES DONNÉES
    # ==========================================
    
    def load_data(self):
        """Charger les données depuis le fichier JSON."""
        data_file = Path("data/structure.json")
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data["universites"] = loaded_data.get("universites", [])
                    self.data["ufrs"] = loaded_data.get("ufrs", [])
                    self.data["programmes"] = loaded_data.get("programmes", loaded_data.get("parcours", []))
                    self.data["cohortes"] = loaded_data.get("cohortes", loaded_data.get("classes", []))
            except Exception as e:
                print(f"Erreur de chargement: {e}")
    
    def save_data(self):
        """Sauvegarder les données dans le fichier JSON."""
        data_file = Path("data/structure.json")
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder: {e}")


# ==========================================
# DIALOGUES (gardés identiques)
# ==========================================

class UniversiteDialog(QDialog):
    """Dialogue pour créer/modifier une université."""
    
    def __init__(self, parent, data=None, existing_codes=None):
        super().__init__(parent)
        self.data = data or {}
        self.existing_codes = existing_codes or []
        self.edit_mode = data is not None
        
        self.setWindowTitle("Modifier Université" if self.edit_mode else "Nouvelle Université")
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier Université" if self.edit_mode else "Nouvelle Université")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Université Nazi Boni")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)
        
        # Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: UNB")
        self.code_input.setFixedHeight(40)
        if self.edit_mode:
            self.code_input.setText(self.data.get('code', ''))
        form.addRow("Code *", self.code_input)
        
        # Ville
        self.ville_input = QLineEdit()
        self.ville_input.setPlaceholderText("Ex: Bobo Dioulasso")
        self.ville_input.setFixedHeight(40)
        if self.edit_mode:
            self.ville_input.setText(self.data.get('ville', ''))
        form.addRow("Ville", self.ville_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valider et accepter le dialogue."""
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()
        
        if not nom or not code:
            QMessageBox.warning(self, "Champs obligatoires", "Le nom et le code sont obligatoires !")
            return
        
        # Vérifier l'unicité du code
        if code in self.existing_codes:
            QMessageBox.critical(self, "Code existant", 
                               f"Le code '{code}' est déjà utilisé.\nVeuillez choisir un autre code.")
            return
        
        self.accept()
    
    def get_data(self):
        """Retourne les données du formulaire."""
        result = {
            "nom": self.nom_input.text().strip(),
            "code": self.code_input.text().strip().upper(),
            "ville": self.ville_input.text().strip()
        }
        
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        
        return result


class UFRDialog(QDialog):
    """Dialogue pour créer/modifier une UFR."""
    
    def __init__(self, parent, universites, data=None, existing_codes=None):
        super().__init__(parent)
        # Référence au parent (StructureTab) pour accéder aux UFR existantes
        self.parent_tab = parent
        self.universites = universites
        self.data = data or {}
        self.existing_codes = existing_codes or []
        self.edit_mode = data is not None
        
        self.setWindowTitle("Modifier UFR" if self.edit_mode else "Nouvelle UFR")
        self.setFixedSize(500, 450)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier UFR" if self.edit_mode else "Nouvelle UFR")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Université
        self.univ_combo = QComboBox()
        self.univ_combo.addItems([u["nom"] for u in self.universites])
        self.univ_combo.setFixedHeight(40)
        if self.edit_mode and 'universite_id' in self.data:
            for i, u in enumerate(self.universites):
                if u.get('id') == self.data['universite_id']:
                    self.univ_combo.setCurrentIndex(i)
                    break
        form.addRow("Université *", self.univ_combo)
        
        # Nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Sciences et Techniques")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)
        
        # Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: UFR-ST")
        self.code_input.setFixedHeight(40)
        if self.edit_mode:
            self.code_input.setText(self.data.get('code', ''))
        form.addRow("Code *", self.code_input)
        
        # Directeur
        self.directeur_input = QLineEdit()
        self.directeur_input.setPlaceholderText("Nom du directeur")
        self.directeur_input.setFixedHeight(40)
        if self.edit_mode:
            self.directeur_input.setText(self.data.get('directeur', ''))
        form.addRow("Directeur", self.directeur_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valider et accepter."""
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()
        
        if not nom or not code:
            QMessageBox.warning(self, "Champs obligatoires", 
                               "Le nom et le code sont obligatoires !")
            return
        # Vérification d'unicité du code UFR dans LA MÊME université uniquement
        # (le même code peut exister dans une autre université).
        # On récupère l'université sélectionnée
        univ_nom = self.univ_combo.currentText()
        universite_id = None
        for u in self.universites:
            if u.get("nom") == univ_nom:
                universite_id = u.get("id")
                break
        
        # Si on a accès aux données complètes via le parent, on vérifie par (universite_id, code)
        ufr_list = []
        if hasattr(self.parent_tab, "data"):
            ufr_list = self.parent_tab.data.get("ufrs", [])
        
        for ufr in ufr_list:
            # En mode édition, ignorer l'UFR courante
            if self.edit_mode and ufr.get("id") == self.data.get("id"):
                continue
            if (
                ufr.get("universite_id") == universite_id
                and str(ufr.get("code", "")).upper() == code
            ):
                QMessageBox.critical(
                    self,
                    "Code existant",
                    "Le code d'UFR '{0}' est déjà utilisé dans l'université '{1}'.\n"
                    "Le même code peut exister dans une autre université, "
                    "mais pas deux fois dans la même.".format(code, univ_nom),
                )
                return
        
        self.accept()
    
    def get_data(self):
        """Retourne les données."""
        univ_nom = self.univ_combo.currentText()
        universite_id = None
        for u in self.universites:
            if u['nom'] == univ_nom:
                universite_id = u.get('id')
                break
        
        result = {
            "nom": self.nom_input.text().strip(),
            "code": self.code_input.text().strip().upper(),
            "directeur": self.directeur_input.text().strip(),
            "universite_id": universite_id
        }
        
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        
        return result


class ProgrammeDialog(QDialog):
    """Dialogue pour créer/modifier un programme."""
    
    def __init__(self, parent, ufrs, data=None, existing_codes=None):
        super().__init__(parent)
        self.ufrs = ufrs
        self.data = data or {}
        self.existing_codes = existing_codes or []
        self.edit_mode = data is not None
        
        self.setWindowTitle("Modifier Parcours" if self.edit_mode else "Nouveau Parcours")
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier Parcours" if self.edit_mode else "Nouveau Parcours")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # UFR
        self.ufr_combo = QComboBox()
        self.ufr_combo.addItems([u["nom"] for u in self.ufrs])
        self.ufr_combo.setFixedHeight(40)
        if self.edit_mode and 'ufr_id' in self.data:
            for i, u in enumerate(self.ufrs):
                if u.get('id') == self.data['ufr_id']:
                    self.ufr_combo.setCurrentIndex(i)
                    break
        form.addRow("UFR *", self.ufr_combo)
        
        # Nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Informatique")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)
        
        # Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Ex: INFO")
        self.code_input.setFixedHeight(40)
        if self.edit_mode:
            self.code_input.setText(self.data.get('code', ''))
        form.addRow("Code *", self.code_input)
        
        # Niveau
        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"])
        self.niveau_combo.setFixedHeight(40)
        if self.edit_mode:
            self.niveau_combo.setCurrentText(self.data.get('niveau', 'Licence 1'))
        form.addRow("Niveau *", self.niveau_combo)
        
        # Durée
        self.duree_input = QSpinBox()
        self.duree_input.setRange(1, 10)
        self.duree_input.setValue(3 if not self.edit_mode else self.data.get('duree_annees', 3))
        self.duree_input.setFixedHeight(40)
        form.addRow("Durée (années)", self.duree_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valider et accepter."""
        nom = self.nom_input.text().strip()
        code = self.code_input.text().strip().upper()
        
        if not nom or not code:
            QMessageBox.warning(self, "Champs obligatoires",
                               "Le nom et le code sont obligatoires !")
            return
        
        if code in self.existing_codes:
            QMessageBox.critical(self, "Code existant",
                               f"Le code '{code}' est déjà utilisé.\nVeuillez choisir un autre code.")
            return
        
        self.accept()
    
    def get_data(self):
        """Retourne les données."""
        ufr_nom = self.ufr_combo.currentText()
        ufr_id = None
        for u in self.ufrs:
            if u['nom'] == ufr_nom:
                ufr_id = u.get('id')
                break
        
        result = {
            "nom": self.nom_input.text().strip(),
            "code": self.code_input.text().strip().upper(),
            "niveau": self.niveau_combo.currentText(),
            "ufr_id": ufr_id,
            "duree_annees": self.duree_input.value()
        }
        
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        
        return result


class CohorteDialog(QDialog):
    """Dialogue pour créer/modifier une cohorte."""
    
    def __init__(self, parent, programmes, data=None):
        super().__init__(parent)
        self.programmes = programmes
        self.data = data or {}
        self.edit_mode = data is not None
        
        self.setWindowTitle("Modifier Classe" if self.edit_mode else "Nouvelle Classe")
        self.setFixedSize(500, 520)
        self.setStyleSheet("background-color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Titre
        title = QLabel("Modifier Classe" if self.edit_mode else "Nouvelle Classe")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Formulaire
        form = QFormLayout()
        form.setSpacing(15)
        
        # Programme
        self.prog_combo = QComboBox()
        prog_labels = [f"{p['nom']} ({p['niveau']})" for p in self.programmes]
        self.prog_combo.addItems(prog_labels)
        self.prog_combo.setFixedHeight(40)
        if self.edit_mode and 'programme_id' in self.data:
            for i, p in enumerate(self.programmes):
                if p.get('id') == self.data['programme_id']:
                    self.prog_combo.setCurrentIndex(i)
                    break
        form.addRow("Parcours *", self.prog_combo)
        
        # Nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: L3 INFO A")
        self.nom_input.setFixedHeight(40)
        if self.edit_mode:
            self.nom_input.setText(self.data.get('nom', ''))
        form.addRow("Nom *", self.nom_input)
        
        # Année académique
        self.annee_input = QLineEdit()
        self.annee_input.setPlaceholderText("Ex: 2025-2026")
        self.annee_input.setFixedHeight(40)
        if self.edit_mode:
            self.annee_input.setText(self.data.get('annee_academique', ''))
        form.addRow("Année académique *", self.annee_input)
        
        # Semestre
        self.semestre_combo = QComboBox()
        self.semestre_combo.addItems(["Semestre 1", "Semestre 2"])
        self.semestre_combo.setFixedHeight(40)
        if self.edit_mode:
            self.semestre_combo.setCurrentText(self.data.get('semestre', 'Semestre 1'))
        form.addRow("Semestre *", self.semestre_combo)
        
        # Effectif
        self.effectif_input = QSpinBox()
        self.effectif_input.setRange(1, 1000)
        self.effectif_input.setValue(45 if not self.edit_mode else self.data.get('effectif', 45))
        self.effectif_input.setFixedHeight(40)
        form.addRow("Effectif *", self.effectif_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(140, 40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(160, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_accept(self):
        """Valider et accepter."""
        nom = self.nom_input.text().strip()
        annee = self.annee_input.text().strip()
        
        if not nom or not annee:
            QMessageBox.warning(self, "Champs obligatoires",
                               "Tous les champs sont obligatoires !")
            return
        
        self.accept()
    
    def get_data(self):
        """Retourne les données."""
        prog_label = self.prog_combo.currentText()
        programme_id = None
        for p in self.programmes:
            if f"{p['nom']} ({p['niveau']})" == prog_label:
                programme_id = p.get('id')
                break
        
        result = {
            "nom": self.nom_input.text().strip(),
            "annee_academique": self.annee_input.text().strip(),
            "semestre": self.semestre_combo.currentText(),
            "programme_id": programme_id,
            "effectif": self.effectif_input.value()
        }
        
        if self.edit_mode and 'id' in self.data:
            result['id'] = self.data['id']
        
        return result