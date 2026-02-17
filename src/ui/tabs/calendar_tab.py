"""
Onglet de gestion du calendrier académique - VERSION COMPLÈTE UC2
Toutes les fonctionnalités sont connectées avec design moderne
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QTabWidget, QDialog,
    QFormLayout, QLineEdit, QDateEdit, QSpinBox, QCheckBox,
    QComboBox, QMessageBox, QTextEdit, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, timedelta
import json
from pathlib import Path


class CalendarDialog(QDialog):
    """Dialogue pour créer/modifier un calendrier académique"""
    
    def __init__(self, parent=None, calendar_data=None):
        super().__init__(parent)
        self.calendar_data = calendar_data or {}
        self.edit_mode = calendar_data is not None
        
        self.setWindowTitle("Modifier Calendrier" if self.edit_mode else "Nouveau Calendrier Académique")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(650)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("📅 Configuration du Calendrier Académique")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)
        
        subtitle = QLabel("Définissez l'année académique, les semestres et les paramètres")
        subtitle.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Formulaire principal
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Année académique
        self.annee_edit = QLineEdit(self.calendar_data.get('annee_academique', ''))
        self.annee_edit.setPlaceholderText("Ex: 2025-2026")
        self.annee_edit.setFixedHeight(40)
        form_layout.addRow("Année académique *:", self.annee_edit)
        
        # Heures de cours par jour
        self.heures_spin = QSpinBox()
        self.heures_spin.setRange(1, 12)
        self.heures_spin.setValue(self.calendar_data.get('heures_cours_par_jour', 8))
        self.heures_spin.setSuffix(" heures")
        self.heures_spin.setFixedHeight(40)
        form_layout.addRow("Heures de cours/jour *:", self.heures_spin)
        
        layout.addLayout(form_layout)
        
        # ==========================================
        # SEMESTRE 1
        # ==========================================
        sem1_group = QGroupBox("📘 Semestre 1")
        sem1_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #3498db;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        sem1_layout = QFormLayout(sem1_group)
        sem1_layout.setSpacing(12)
        
        self.sem1_debut = QDateEdit()
        self.sem1_debut.setCalendarPopup(True)
        self.sem1_debut.setDate(QDate.currentDate())
        self.sem1_debut.setFixedHeight(40)
        self.sem1_debut.setDisplayFormat("dd/MM/yyyy")
        if 'semestre1_debut' in self.calendar_data:
            self.sem1_debut.setDate(QDate.fromString(self.calendar_data['semestre1_debut'], "dd/MM/yyyy"))
        sem1_layout.addRow("Date début *:", self.sem1_debut)
        
        self.sem1_fin = QDateEdit()
        self.sem1_fin.setCalendarPopup(True)
        self.sem1_fin.setDate(QDate.currentDate().addMonths(4))
        self.sem1_fin.setFixedHeight(40)
        self.sem1_fin.setDisplayFormat("dd/MM/yyyy")
        if 'semestre1_fin' in self.calendar_data:
            self.sem1_fin.setDate(QDate.fromString(self.calendar_data['semestre1_fin'], "dd/MM/yyyy"))
        sem1_layout.addRow("Date fin *:", self.sem1_fin)
        
        layout.addWidget(sem1_group)
        
        # ==========================================
        # SEMESTRE 2
        # ==========================================
        sem2_group = QGroupBox("📗 Semestre 2")
        sem2_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #27ae60;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        sem2_layout = QFormLayout(sem2_group)
        sem2_layout.setSpacing(12)
        
        self.sem2_debut = QDateEdit()
        self.sem2_debut.setCalendarPopup(True)
        self.sem2_debut.setDate(QDate.currentDate().addMonths(5))
        self.sem2_debut.setFixedHeight(40)
        self.sem2_debut.setDisplayFormat("dd/MM/yyyy")
        if 'semestre2_debut' in self.calendar_data:
            self.sem2_debut.setDate(QDate.fromString(self.calendar_data['semestre2_debut'], "dd/MM/yyyy"))
        sem2_layout.addRow("Date début *:", self.sem2_debut)
        
        self.sem2_fin = QDateEdit()
        self.sem2_fin.setCalendarPopup(True)
        self.sem2_fin.setDate(QDate.currentDate().addMonths(9))
        self.sem2_fin.setFixedHeight(40)
        self.sem2_fin.setDisplayFormat("dd/MM/yyyy")
        if 'semestre2_fin' in self.calendar_data:
            self.sem2_fin.setDate(QDate.fromString(self.calendar_data['semestre2_fin'], "dd/MM/yyyy"))
        sem2_layout.addRow("Date fin *:", self.sem2_fin)
        
        layout.addWidget(sem2_group)
        
        # ==========================================
        # JOURS OUVRABLES
        # ==========================================
        jours_group = QGroupBox("📆 Jours ouvrables de la semaine")
        jours_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #9b59b6;
            }
        """)
        
        jours_layout = QHBoxLayout(jours_group)
        
        self.jours_checks = {}
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        jours_actifs = self.calendar_data.get('jours_ouvrables', ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])
        
        for jour in jours:
            check = QCheckBox(jour)
            check.setChecked(jour in jours_actifs)
            check.setStyleSheet("font-size: 13px; padding: 5px;")
            self.jours_checks[jour] = check
            jours_layout.addWidget(check)
        
        layout.addWidget(jours_group)
        
        layout.addSpacing(10)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.setFixedSize(140, 45)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.setFixedSize(180, 45)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.validate_and_save)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_save(self):
        """Valider et sauvegarder"""
        # Validation
        if not self.annee_edit.text().strip():
            QMessageBox.warning(self, "Validation", "L'année académique est obligatoire !")
            return
        
        # Vérifier cohérence des dates
        sem1_debut = self.sem1_debut.date()
        sem1_fin = self.sem1_fin.date()
        sem2_debut = self.sem2_debut.date()
        sem2_fin = self.sem2_fin.date()
        
        if sem1_fin <= sem1_debut:
            QMessageBox.warning(self, "Validation", 
                              "La date de fin du Semestre 1 doit être après la date de début !")
            return
        
        if sem2_fin <= sem2_debut:
            QMessageBox.warning(self, "Validation",
                              "La date de fin du Semestre 2 doit être après la date de début !")
            return
        
        if sem2_debut <= sem1_fin:
            QMessageBox.warning(self, "Validation",
                              "Le Semestre 2 doit commencer après la fin du Semestre 1 !")
            return
        
        # Vérifier qu'au moins un jour est sélectionné
        jours_selectionnes = [jour for jour, check in self.jours_checks.items() if check.isChecked()]
        if not jours_selectionnes:
            QMessageBox.warning(self, "Validation",
                              "Veuillez sélectionner au moins un jour ouvrable !")
            return
        
        # Calculer D_effectif
        d_effectif = self.calculer_d_effectif(sem1_debut, sem1_fin, sem2_debut, sem2_fin, jours_selectionnes)
        
        # Afficher récapitulatif
        self.show_recap(d_effectif)
    
    def calculer_d_effectif(self, sem1_debut, sem1_fin, sem2_debut, sem2_fin, jours_ouvrables):
        """Calculer le nombre de jours ouvrables effectifs"""
        jours_semaine = {
            "Lundi": 0, "Mardi": 1, "Mercredi": 2,
            "Jeudi": 3, "Vendredi": 4, "Samedi": 5, "Dimanche": 6
        }
        
        jours_indices = [jours_semaine[j] for j in jours_ouvrables]
        
        def compter_jours(date_debut, date_fin):
            count = 0
            current = date_debut.toPyDate()
            end = date_fin.toPyDate()
            
            while current <= end:
                if current.weekday() in jours_indices:
                    count += 1
                current += timedelta(days=1)
            
            return count
        
        jours_sem1 = compter_jours(sem1_debut, sem1_fin)
        jours_sem2 = compter_jours(sem2_debut, sem2_fin)
        
        return jours_sem1 + jours_sem2
    
    def show_recap(self, d_effectif):
        """Afficher le récapitulatif"""
        sem1_debut = self.sem1_debut.date().toString("dd/MM/yyyy")
        sem1_fin = self.sem1_fin.date().toString("dd/MM/yyyy")
        sem2_debut = self.sem2_debut.date().toString("dd/MM/yyyy")
        sem2_fin = self.sem2_fin.date().toString("dd/MM/yyyy")
        
        jours_selectionnes = [jour for jour, check in self.jours_checks.items() if check.isChecked()]
        
        recap = f"""
📅 RÉCAPITULATIF DU CALENDRIER ACADÉMIQUE

Année académique : {self.annee_edit.text()}
Heures de cours/jour : {self.heures_spin.value()}h

📘 SEMESTRE 1 :
   Du {sem1_debut} au {sem1_fin}

📗 SEMESTRE 2 :
   Du {sem2_debut} au {sem2_fin}

📆 JOURS OUVRABLES :
   {', '.join(jours_selectionnes)}

✅ JOURS OUVRABLES EFFECTIFS (D_effectif) :
   {d_effectif} jours

📊 VOLUME HORAIRE TOTAL POSSIBLE :
   {d_effectif * self.heures_spin.value()} heures

Voulez-vous enregistrer ce calendrier ?
        """
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            recap,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.accept()
    
    def get_data(self):
        """Récupérer les données du formulaire"""
        jours_selectionnes = [jour for jour, check in self.jours_checks.items() if check.isChecked()]
        
        sem1_debut = self.sem1_debut.date()
        sem1_fin = self.sem1_fin.date()
        sem2_debut = self.sem2_debut.date()
        sem2_fin = self.sem2_fin.date()
        
        d_effectif = self.calculer_d_effectif(sem1_debut, sem1_fin, sem2_debut, sem2_fin, jours_selectionnes)
        
        return {
            'annee_academique': self.annee_edit.text().strip(),
            'heures_cours_par_jour': self.heures_spin.value(),
            'semestre1_debut': sem1_debut.toString("dd/MM/yyyy"),
            'semestre1_fin': sem1_fin.toString("dd/MM/yyyy"),
            'semestre2_debut': sem2_debut.toString("dd/MM/yyyy"),
            'semestre2_fin': sem2_fin.toString("dd/MM/yyyy"),
            'jours_ouvrables': jours_selectionnes,
            'd_effectif': d_effectif,
            'volume_horaire_total': d_effectif * self.heures_spin.value(),
            'date_creation': datetime.now().isoformat()
        }


class HolidayDialog(QDialog):
    """Dialogue pour ajouter un jour férié"""
    
    def __init__(self, parent=None, holiday_data=None):
        super().__init__(parent)
        self.holiday_data = holiday_data or {}
        self.edit_mode = holiday_data is not None
        
        self.setWindowTitle("Modifier Jour Férié" if self.edit_mode else "Nouveau Jour Férié")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("🎉 " + ("Modifier" if self.edit_mode else "Ajouter") + " un Jour Férié")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        self.nom_edit = QLineEdit(self.holiday_data.get('nom', ''))
        self.nom_edit.setPlaceholderText("Ex: Jour de l'An")
        self.nom_edit.setFixedHeight(40)
        form.addRow("Nom *:", self.nom_edit)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(40)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        if 'date' in self.holiday_data:
            self.date_edit.setDate(QDate.fromString(self.holiday_data['date'], "dd/MM/yyyy"))
        form.addRow("Date *:", self.date_edit)
        
        self.recurrent_check = QCheckBox("Récurrent chaque année")
        self.recurrent_check.setChecked(self.holiday_data.get('recurrent', True))
        form.addRow("", self.recurrent_check)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["National", "Local", "Religieux", "Autre"])
        self.type_combo.setFixedHeight(40)
        if 'type' in self.holiday_data:
            self.type_combo.setCurrentText(self.holiday_data['type'])
        form.addRow("Type:", self.type_combo)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(120, 40)
        btn_cancel.setStyleSheet("background-color: #e0e0e0; border-radius: 5px;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Enregistrer")
        btn_save.setFixedSize(140, 40)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold;")
        btn_save.clicked.connect(self.validate_and_save)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_save(self):
        """Valider et sauvegarder"""
        if not self.nom_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire !")
            return
        self.accept()
    
    def get_data(self):
        """Récupérer les données"""
        return {
            'nom': self.nom_edit.text().strip(),
            'date': self.date_edit.date().toString("dd/MM/yyyy"),
            'recurrent': self.recurrent_check.isChecked(),
            'type': self.type_combo.currentText()
        }


class VacationDialog(QDialog):
    """Dialogue pour ajouter une période de vacances"""
    
    def __init__(self, parent=None, vacation_data=None):
        super().__init__(parent)
        self.vacation_data = vacation_data or {}
        self.edit_mode = vacation_data is not None
        
        self.setWindowTitle("Modifier Vacances" if self.edit_mode else "Nouvelle Période de Vacances")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("🏖️ " + ("Modifier" if self.edit_mode else "Ajouter") + " une Période de Vacances")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(20)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        self.nom_edit = QLineEdit(self.vacation_data.get('nom', ''))
        self.nom_edit.setPlaceholderText("Ex: Vacances de Noël")
        self.nom_edit.setFixedHeight(40)
        form.addRow("Nom *:", self.nom_edit)
        
        self.debut_edit = QDateEdit()
        self.debut_edit.setCalendarPopup(True)
        self.debut_edit.setDate(QDate.currentDate())
        self.debut_edit.setFixedHeight(40)
        self.debut_edit.setDisplayFormat("dd/MM/yyyy")
        if 'date_debut' in self.vacation_data:
            self.debut_edit.setDate(QDate.fromString(self.vacation_data['date_debut'], "dd/MM/yyyy"))
        form.addRow("Date début *:", self.debut_edit)
        
        self.fin_edit = QDateEdit()
        self.fin_edit.setCalendarPopup(True)
        self.fin_edit.setDate(QDate.currentDate().addDays(14))
        self.fin_edit.setFixedHeight(40)
        self.fin_edit.setDisplayFormat("dd/MM/yyyy")
        if 'date_fin' in self.vacation_data:
            self.fin_edit.setDate(QDate.fromString(self.vacation_data['date_fin'], "dd/MM/yyyy"))
        form.addRow("Date fin *:", self.fin_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Hiver", "Printemps", "Été", "Autre"])
        self.type_combo.setFixedHeight(40)
        if 'type' in self.vacation_data:
            self.type_combo.setCurrentText(self.vacation_data['type'])
        form.addRow("Type:", self.type_combo)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(120, 40)
        btn_cancel.setStyleSheet("background-color: #e0e0e0; border-radius: 5px;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Enregistrer")
        btn_save.setFixedSize(140, 40)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold;")
        btn_save.clicked.connect(self.validate_and_save)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def validate_and_save(self):
        """Valider et sauvegarder"""
        if not self.nom_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire !")
            return
        
        if self.fin_edit.date() <= self.debut_edit.date():
            QMessageBox.warning(self, "Validation", "La date de fin doit être après la date de début !")
            return
        
        self.accept()
    
    def get_data(self):
        """Récupérer les données"""
        return {
            'nom': self.nom_edit.text().strip(),
            'date_debut': self.debut_edit.date().toString("dd/MM/yyyy"),
            'date_fin': self.fin_edit.date().toString("dd/MM/yyyy"),
            'type': self.type_combo.currentText()
        }


class CalendarTab(QWidget):
    """Onglet pour gérer le calendrier académique - VERSION COMPLÈTE"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Données
        self.calendars = []
        self.holidays = []
        self.vacations = []
        
        self.load_data()
        self.init_ui()
        self.load_sample_data()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QVBoxLayout()
        title = QLabel("Calendrier Académique")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Gestion des calendriers, jours fériés et périodes de vacances")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                padding: 12px 30px;
                margin-right: 4px;
                background: #F5F5F5;
                border: none;
                font-size: 14px;
                color: #666;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:selected {
                color: #1976D2;
                font-weight: bold;
                background: white;
            }
            QTabBar::tab:hover {
                background: #E3F2FD;
            }
        """)
        
        # Tab Calendriers
        self.calendars_tab = self.create_calendars_tab()
        self.tabs.addTab(self.calendars_tab, "📅 Calendriers")
        
        # Tab Jours fériés
        self.holidays_tab = self.create_holidays_tab()
        self.tabs.addTab(self.holidays_tab, "🎉 Jours fériés")
        
        # Tab Vacances
        self.vacations_tab = self.create_vacations_tab()
        self.tabs.addTab(self.vacations_tab, "🏖️ Périodes de vacances")
        
        layout.addWidget(self.tabs)
    
    def create_calendars_tab(self):
        """Crée l'onglet des calendriers."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête avec bouton
        header = QHBoxLayout()
        header_label = QLabel(f"Calendriers ({len(self.calendars)})")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_add_calendar = QPushButton("➕ Nouveau Calendrier")
        self.btn_add_calendar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_add_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_add_calendar.clicked.connect(self.add_calendar)  # ✅ CONNECTÉ
        
        header.addWidget(header_label)
        header.addStretch()
        header.addWidget(self.btn_add_calendar)
        
        layout.addLayout(header)
        
        # Table
        self.table_calendars = QTableWidget()
        self.table_calendars.setColumnCount(6)
        self.table_calendars.setHorizontalHeaderLabels([
            "Année", "Semestre 1", "Semestre 2", "Jours ouvrables", "D_effectif", "Actions"
        ])
        self.table_calendars.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_calendars.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_calendars.setColumnWidth(5, 100)
        self.table_calendars.setStyleSheet(self.get_modern_table_style())
        self.table_calendars.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_calendars)
        
        return widget
    
    def create_holidays_tab(self):
        """Crée l'onglet des jours fériés."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QHBoxLayout()
        header_label = QLabel(f"Jours fériés ({len(self.holidays)})")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_add_holiday = QPushButton("➕ Nouveau Jour Férié")
        self.btn_add_holiday.setStyleSheet(self.get_add_button_style())
        self.btn_add_holiday.setCursor(Qt.PointingHandCursor)
        self.btn_add_holiday.clicked.connect(self.add_holiday)  # ✅ CONNECTÉ
        
        header.addWidget(header_label)
        header.addStretch()
        header.addWidget(self.btn_add_holiday)
        
        layout.addLayout(header)
        
        # Table
        self.table_holidays = QTableWidget()
        self.table_holidays.setColumnCount(5)
        self.table_holidays.setHorizontalHeaderLabels(["Nom", "Date", "Type", "Récurrent", "Actions"])
        self.table_holidays.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_holidays.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_holidays.setColumnWidth(4, 100)
        self.table_holidays.setStyleSheet(self.get_modern_table_style())
        self.table_holidays.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_holidays)
        
        return widget
    
    def create_vacations_tab(self):
        """Crée l'onglet des périodes de vacances."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête
        header = QHBoxLayout()
        header_label = QLabel(f"Périodes de vacances ({len(self.vacations)})")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_add_vacation = QPushButton("➕ Nouvelle Période")
        self.btn_add_vacation.setStyleSheet(self.get_add_button_style())
        self.btn_add_vacation.setCursor(Qt.PointingHandCursor)
        self.btn_add_vacation.clicked.connect(self.add_vacation)  # ✅ CONNECTÉ
        
        header.addWidget(header_label)
        header.addStretch()
        header.addWidget(self.btn_add_vacation)
        
        layout.addLayout(header)
        
        # Table
        self.table_vacations = QTableWidget()
        self.table_vacations.setColumnCount(5)
        self.table_vacations.setHorizontalHeaderLabels(["Nom", "Date début", "Date fin", "Type", "Actions"])
        self.table_vacations.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_vacations.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_vacations.setColumnWidth(4, 100)
        self.table_vacations.setStyleSheet(self.get_modern_table_style())
        self.table_vacations.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_vacations)
        
        return widget
    
    def load_sample_data(self):
        """Charger des données exemple"""
        # Calendriers
        if not self.calendars:
            self.calendars = [
                {
                    'id': 1,
                    'annee_academique': '2025-2026',
                    'heures_cours_par_jour': 8,
                    'semestre1_debut': '01/10/2025',
                    'semestre1_fin': '28/02/2026',
                    'semestre2_debut': '01/03/2026',
                    'semestre2_fin': '31/07/2026',
                    'jours_ouvrables': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
                    'd_effectif': 230,
                    'volume_horaire_total': 1840
                }
            ]
        
        # Jours fériés
        if not self.holidays:
            self.holidays = [
                {'id': 1, 'nom': "Jour de l'An", 'date': '01/01/2026', 'type': 'National', 'recurrent': True},
                {'id': 2, 'nom': "Fête du Travail", 'date': '01/05/2026', 'type': 'National', 'recurrent': True},
                {'id': 3, 'nom': "Fête Nationale", 'date': '05/08/2026', 'type': 'National', 'recurrent': True},
                {'id': 4, 'nom': "Noël", 'date': '25/12/2025', 'type': 'Religieux', 'recurrent': True},
            ]
        
        # Vacances
        if not self.vacations:
            self.vacations = [
                {'id': 1, 'nom': 'Vacances de Noël', 'date_debut': '20/12/2025', 'date_fin': '05/01/2026', 'type': 'Hiver'},
                {'id': 2, 'nom': 'Vacances de Pâques', 'date_debut': '10/04/2026', 'date_fin': '20/04/2026', 'type': 'Printemps'},
            ]
        
        self.refresh_all_tables()
    
    def refresh_all_tables(self):
        """Rafraîchir toutes les tables"""
        self.refresh_calendars_table()
        self.refresh_holidays_table()
        self.refresh_vacations_table()
        
        # Mettre à jour les compteurs
        self.tabs.setTabText(0, f"📅 Calendriers ({len(self.calendars)})")
        self.tabs.setTabText(1, f"🎉 Jours fériés ({len(self.holidays)})")
        self.tabs.setTabText(2, f"🏖️ Périodes de vacances ({len(self.vacations)})")
    
    def refresh_calendars_table(self):
        """Rafraîchir la table des calendriers"""
        self.table_calendars.setRowCount(len(self.calendars))
        
        for i, cal in enumerate(self.calendars):
            self.table_calendars.setItem(i, 0, QTableWidgetItem(cal['annee_academique']))
            self.table_calendars.setItem(i, 1, QTableWidgetItem(f"{cal['semestre1_debut']} → {cal['semestre1_fin']}"))
            self.table_calendars.setItem(i, 2, QTableWidgetItem(f"{cal['semestre2_debut']} → {cal['semestre2_fin']}"))
            self.table_calendars.setItem(i, 3, QTableWidgetItem(f"{len(cal['jours_ouvrables'])} jours"))
            
            # D_effectif en surbrillance
            d_eff_item = QTableWidgetItem(f"{cal['d_effectif']} jours")
            d_eff_item.setBackground(QColor("#E8F5E9"))
            self.table_calendars.setItem(i, 4, d_eff_item)
            
            # Actions
            actions_widget = self.create_action_buttons(
                lambda c=cal: self.edit_calendar(c),
                lambda c=cal: self.delete_calendar(c)
            )
            self.table_calendars.setCellWidget(i, 5, actions_widget)
    
    def refresh_holidays_table(self):
        """Rafraîchir la table des jours fériés"""
        self.table_holidays.setRowCount(len(self.holidays))
        
        for i, holiday in enumerate(self.holidays):
            self.table_holidays.setItem(i, 0, QTableWidgetItem(holiday['nom']))
            self.table_holidays.setItem(i, 1, QTableWidgetItem(holiday['date']))
            self.table_holidays.setItem(i, 2, QTableWidgetItem(holiday['type']))
            self.table_holidays.setItem(i, 3, QTableWidgetItem("Oui" if holiday['recurrent'] else "Non"))
            
            actions_widget = self.create_action_buttons(
                lambda h=holiday: self.edit_holiday(h),
                lambda h=holiday: self.delete_holiday(h)
            )
            self.table_holidays.setCellWidget(i, 4, actions_widget)
    
    def refresh_vacations_table(self):
        """Rafraîchir la table des vacances"""
        self.table_vacations.setRowCount(len(self.vacations))
        
        for i, vac in enumerate(self.vacations):
            self.table_vacations.setItem(i, 0, QTableWidgetItem(vac['nom']))
            self.table_vacations.setItem(i, 1, QTableWidgetItem(vac['date_debut']))
            self.table_vacations.setItem(i, 2, QTableWidgetItem(vac['date_fin']))
            self.table_vacations.setItem(i, 3, QTableWidgetItem(vac['type']))
            
            actions_widget = self.create_action_buttons(
                lambda v=vac: self.edit_vacation(v),
                lambda v=vac: self.delete_vacation(v)
            )
            self.table_vacations.setCellWidget(i, 4, actions_widget)
    
    # ==========================================
    # ACTIONS - CALENDRIERS
    # ==========================================
    
    def add_calendar(self):
        """Ajouter un calendrier"""
        dialog = CalendarDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            new_id = max([c['id'] for c in self.calendars], default=0) + 1
            data['id'] = new_id
            self.calendars.append(data)
            self.save_data()
            self.refresh_all_tables()
            
            QMessageBox.information(
                self,
                "Succès",
                f"✅ Calendrier académique {data['annee_academique']} créé avec succès !\n\n"
                f"D_effectif = {data['d_effectif']} jours ouvrables"
            )
    
    def edit_calendar(self, calendar):
        """Modifier un calendrier"""
        dialog = CalendarDialog(self, calendar)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            calendar.update(data)
            self.save_data()
            self.refresh_all_tables()
            
            QMessageBox.information(self, "Succès", "✅ Calendrier modifié avec succès !")
    
    def delete_calendar(self, calendar):
        """Supprimer un calendrier"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer le calendrier {calendar['annee_academique']} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.calendars.remove(calendar)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", "✅ Calendrier supprimé !")
    
    # ==========================================
    # ACTIONS - JOURS FÉRIÉS
    # ==========================================
    
    def add_holiday(self):
        """Ajouter un jour férié"""
        dialog = HolidayDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            new_id = max([h['id'] for h in self.holidays], default=0) + 1
            data['id'] = new_id
            self.holidays.append(data)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", f"✅ Jour férié '{data['nom']}' ajouté !")
    
    def edit_holiday(self, holiday):
        """Modifier un jour férié"""
        dialog = HolidayDialog(self, holiday)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            holiday.update(data)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", "✅ Jour férié modifié !")
    
    def delete_holiday(self, holiday):
        """Supprimer un jour férié"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer le jour férié '{holiday['nom']}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.holidays.remove(holiday)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", "✅ Jour férié supprimé !")
    
    # ==========================================
    # ACTIONS - VACANCES
    # ==========================================
    
    def add_vacation(self):
        """Ajouter une période de vacances"""
        dialog = VacationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            new_id = max([v['id'] for v in self.vacations], default=0) + 1
            data['id'] = new_id
            self.vacations.append(data)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", f"✅ Période '{data['nom']}' ajoutée !")
    
    def edit_vacation(self, vacation):
        """Modifier une période de vacances"""
        dialog = VacationDialog(self, vacation)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            vacation.update(data)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", "✅ Période modifiée !")
    
    def delete_vacation(self, vacation):
        """Supprimer une période de vacances"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer '{vacation['nom']}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.vacations.remove(vacation)
            self.save_data()
            self.refresh_all_tables()
            QMessageBox.information(self, "Succès", "✅ Période supprimée !")
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def create_action_buttons(self, edit_callback, delete_callback):
        """Créer les boutons d'action"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                border-radius: 4px;
            }
        """)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(edit_callback)
        
        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(30, 30)
        btn_delete.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FFEBEE;
                border-radius: 4px;
            }
        """)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(delete_callback)
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget
    
    def get_add_button_style(self):
        """Style du bouton Ajouter."""
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
    
    def get_modern_table_style(self):
        """Style moderne de la table."""
        return """
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 12px;
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
                font-size: 13px;
                color: #333;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """
    
    # ==========================================
    # PERSISTANCE
    # ==========================================
    
    def load_data(self):
        """Charger les données"""
        data_file = Path("data/calendar.json")
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.calendars = data.get('calendars', [])
                    self.holidays = data.get('holidays', [])
                    self.vacations = data.get('vacations', [])
            except Exception as e:
                print(f"Erreur chargement: {e}")
    
    def save_data(self):
        """Sauvegarder les données"""
        data_file = Path("data/calendar.json")
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                'calendars': self.calendars,
                'holidays': self.holidays,
                'vacations': self.vacations
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur sauvegarde: {e}")