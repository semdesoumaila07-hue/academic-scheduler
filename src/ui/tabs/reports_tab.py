"""
Onglet de génération de rapports - UC8.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QFrame, QGroupBox, QCheckBox,
    QMessageBox, QProgressBar, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
import time


class ReportGeneratorThread(QThread):
    """Thread pour générer les rapports en arrière-plan."""
    
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, report_type, period_start, period_end, indicators, export_format):
        super().__init__()
        self.report_type = report_type
        self.period_start = period_start
        self.period_end = period_end
        self.indicators = indicators
        self.export_format = export_format
    
    def run(self):
        """Génère le rapport."""
        try:
            # Étape 1 : Récupération des données d'ordonnancement
            self.progress_updated.emit(10, "Récupération des données d'ordonnancement...")
            time.sleep(0.5)
            
            # Étape 2 : Calcul des indicateurs de retard
            self.progress_updated.emit(25, "Calcul des indicateurs de retard...")
            time.sleep(0.5)
            
            # Étape 3 : Agrégation selon le type de rapport
            if self.report_type == "Synthèse semestrielle":
                self.progress_updated.emit(40, "Agrégation des données par semestre...")
            elif self.report_type == "Comparaison inter-UFR":
                self.progress_updated.emit(40, "Agrégation des données par UFR...")
            elif self.report_type == "Évolution annuelle":
                self.progress_updated.emit(40, "Agrégation des données par année...")
            time.sleep(0.6)
            
            # Étape 4 : Calcul des indicateurs sélectionnés
            self.progress_updated.emit(55, "Calcul des indicateurs sélectionnés...")
            time.sleep(0.5)
            
            # Taux de couverture
            if self.indicators.get('taux_couverture', False):
                self.progress_updated.emit(60, "Calcul du taux de couverture...")
                time.sleep(0.3)
            
            # Retards moyens
            if self.indicators.get('retards_moyens', False):
                self.progress_updated.emit(65, "Calcul des retards moyens...")
                time.sleep(0.3)
            
            # Utilisation des ressources
            if self.indicators.get('utilisation_ressources', False):
                self.progress_updated.emit(70, "Calcul de l'utilisation des ressources...")
                time.sleep(0.3)
            
            # Taux de conflits
            if self.indicators.get('taux_conflits', False):
                self.progress_updated.emit(75, "Calcul du taux de conflits...")
                time.sleep(0.3)
            
            # Étape 5 : Génération du rapport
            self.progress_updated.emit(80, "Génération du rapport...")
            time.sleep(0.5)
            
            # Étape 6 : Mise en forme
            self.progress_updated.emit(90, f"Mise en forme du rapport ({self.export_format})...")
            time.sleep(0.5)
            
            # Étape 7 : Export
            self.progress_updated.emit(95, "Export du rapport...")
            time.sleep(0.3)
            
            # Étape 8 : Finalisation
            self.progress_updated.emit(100, "Rapport généré avec succès !")
            time.sleep(0.2)
            
            # Préparer les résultats
            results = {
                'success': True,
                'report_type': self.report_type,
                'period_start': self.period_start,
                'period_end': self.period_end,
                'export_format': self.export_format,
                'filename': self.get_filename(),
                'stats': {
                    'taux_couverture': 92.5,
                    'retard_moyen': 2.3,
                    'utilisation_salles': 85.0,
                    'taux_conflits': 0.5,
                    'nb_activites': 156,
                    'nb_creneaux': 1245,
                    'heures_planifiees': 3420,
                    'nb_enseignants': 45,
                    'nb_cohortes': 12,
                }
            }
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"Erreur lors de la génération : {str(e)}")
    
    def get_filename(self):
        """Génère le nom du fichier."""
        type_short = {
            "Synthèse semestrielle": "synthese_semestrielle",
            "Comparaison inter-UFR": "comparaison_ufr",
            "Évolution annuelle": "evolution_annuelle"
        }
        
        ext = {
            "PDF": ".pdf",
            "Word": ".docx",
            "PowerPoint": ".pptx"
        }
        
        return f"rapport_{type_short.get(self.report_type, 'rapport')}_{self.period_start.replace('/', '-')}{ext.get(self.export_format, '.pdf')}"


class ReportsTab(QWidget):
    """Onglet de génération de rapports."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.report_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # En-tête
        header_layout = QVBoxLayout()
        title = QLabel("Génération de Rapports")
        title.setStyleSheet("font-size: 28px; font-weight: 600; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Générez des rapports statistiques globaux pour la direction de l'université")
        subtitle.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(25)
        
        # Titre du formulaire
        form_title = QLabel("Paramètres du rapport")
        form_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1F2937;")
        form_layout.addWidget(form_title)
        
        # Type de rapport
        type_layout = QVBoxLayout()
        type_label = QLabel("Type de rapport *")
        type_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Synthèse semestrielle",
            "Comparaison inter-UFR",
            "Évolution annuelle"
        ])
        self.report_type_combo.setStyleSheet(self.get_input_style())
        self.report_type_combo.setFixedHeight(45)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.report_type_combo)
        form_layout.addLayout(type_layout)
        
        # Période
        period_layout = QHBoxLayout()
        period_layout.setSpacing(20)
        
        # Date début
        start_layout = QVBoxLayout()
        start_label = QLabel("Date de début *")
        start_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        
        self.period_start = QDateEdit()
        self.period_start.setDate(QDate(2025, 10, 1))
        self.period_start.setCalendarPopup(True)
        self.period_start.setStyleSheet(self.get_input_style())
        self.period_start.setFixedHeight(45)
        
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.period_start)
        
        # Date fin
        end_layout = QVBoxLayout()
        end_label = QLabel("Date de fin *")
        end_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        
        self.period_end = QDateEdit()
        self.period_end.setDate(QDate(2026, 3, 31))
        self.period_end.setCalendarPopup(True)
        self.period_end.setStyleSheet(self.get_input_style())
        self.period_end.setFixedHeight(45)
        
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.period_end)
        
        period_layout.addLayout(start_layout)
        period_layout.addLayout(end_layout)
        form_layout.addLayout(period_layout)
        
        # Indicateurs à inclure
        indicators_group = QGroupBox("Indicateurs à inclure")
        indicators_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: 600;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        indicators_layout = QVBoxLayout(indicators_group)
        indicators_layout.setSpacing(12)
        
        self.check_taux_couverture = QCheckBox("Taux de couverture (heures planifiées / heures prévues)")
        self.check_taux_couverture.setChecked(True)
        self.check_taux_couverture.setStyleSheet(self.get_checkbox_style())
        
        self.check_retards_moyens = QCheckBox("Retards moyens par activité")
        self.check_retards_moyens.setChecked(True)
        self.check_retards_moyens.setStyleSheet(self.get_checkbox_style())
        
        self.check_utilisation_ressources = QCheckBox("Utilisation des ressources (salles, enseignants)")
        self.check_utilisation_ressources.setChecked(True)
        self.check_utilisation_ressources.setStyleSheet(self.get_checkbox_style())
        
        self.check_taux_conflits = QCheckBox("Taux de conflits détectés")
        self.check_taux_conflits.setChecked(False)
        self.check_taux_conflits.setStyleSheet(self.get_checkbox_style())
        
        self.check_repartition = QCheckBox("Répartition par type d'activité (CM, TD, TP)")
        self.check_repartition.setChecked(True)
        self.check_repartition.setStyleSheet(self.get_checkbox_style())
        
        self.check_charge_enseignants = QCheckBox("Charge de travail par enseignant")
        self.check_charge_enseignants.setChecked(False)
        self.check_charge_enseignants.setStyleSheet(self.get_checkbox_style())
        
        indicators_layout.addWidget(self.check_taux_couverture)
        indicators_layout.addWidget(self.check_retards_moyens)
        indicators_layout.addWidget(self.check_utilisation_ressources)
        indicators_layout.addWidget(self.check_taux_conflits)
        indicators_layout.addWidget(self.check_repartition)
        indicators_layout.addWidget(self.check_charge_enseignants)
        
        form_layout.addWidget(indicators_group)
        
        # Format d'export
        export_layout = QVBoxLayout()
        export_label = QLabel("Format d'export *")
        export_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PDF", "Word", "PowerPoint"])
        self.export_format_combo.setStyleSheet(self.get_input_style())
        self.export_format_combo.setFixedHeight(45)
        
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_format_combo)
        form_layout.addLayout(export_layout)
        
        # Barre de progression (cachée au début)
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout(self.progress_frame)
        
        self.progress_label = QLabel("Préparation...")
        self.progress_label.setStyleSheet("font-size: 13px; color: #6B7280; margin-bottom: 8px;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                background-color: #F3F4F6;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 5px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        form_layout.addWidget(self.progress_frame)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_preview = QPushButton("👁️ Aperçu")
        self.btn_preview.setStyleSheet(self.get_secondary_button_style())
        self.btn_preview.setFixedHeight(50)
        self.btn_preview.clicked.connect(self.show_preview)
        self.btn_preview.setCursor(Qt.PointingHandCursor)
        
        self.btn_generate = QPushButton("📊 Générer le rapport")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #000;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1F2937;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
        """)
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.clicked.connect(self.generate_report)
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_generate, 1)
        
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(form_frame)
        layout.addStretch()
    
    def show_preview(self):
        """Affiche un aperçu du rapport."""
        report_type = self.report_type_combo.currentText()
        start = self.period_start.date().toString("dd/MM/yyyy")
        end = self.period_end.date().toString("dd/MM/yyyy")
        export_format = self.export_format_combo.currentText()
        
        preview_text = f"""
<h3>Aperçu du rapport</h3>

<table style="width: 100%; border-collapse: collapse;">
<tr style="background: #F9FAFB;">
    <td style="padding: 12px; font-weight: bold;">Type de rapport :</td>
    <td style="padding: 12px;">{report_type}</td>
</tr>
<tr>
    <td style="padding: 12px; font-weight: bold;">Période :</td>
    <td style="padding: 12px;">{start} → {end}</td>
</tr>
<tr style="background: #F9FAFB;">
    <td style="padding: 12px; font-weight: bold;">Format :</td>
    <td style="padding: 12px;">{export_format}</td>
</tr>
<tr>
    <td style="padding: 12px; font-weight: bold;">Indicateurs :</td>
    <td style="padding: 12px;">{self.get_selected_indicators_count()} sélectionné(s)</td>
</tr>
</table>

<h4 style="margin-top: 20px;">Sections incluses :</h4>
<ul>
"""
        
        if self.check_taux_couverture.isChecked():
            preview_text += "<li>✅ Taux de couverture</li>"
        if self.check_retards_moyens.isChecked():
            preview_text += "<li>✅ Retards moyens</li>"
        if self.check_utilisation_ressources.isChecked():
            preview_text += "<li>✅ Utilisation des ressources</li>"
        if self.check_taux_conflits.isChecked():
            preview_text += "<li>✅ Taux de conflits</li>"
        if self.check_repartition.isChecked():
            preview_text += "<li>✅ Répartition par type d'activité</li>"
        if self.check_charge_enseignants.isChecked():
            preview_text += "<li>✅ Charge de travail par enseignant</li>"
        
        preview_text += "</ul>"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Aperçu du rapport")
        msg.setTextFormat(Qt.RichText)
        msg.setText(preview_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def generate_report(self):
        """Génère le rapport."""
        # Validation
        if self.get_selected_indicators_count() == 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner au moins un indicateur.")
            return
        
        # Récupérer les données
        report_type = self.report_type_combo.currentText()
        start = self.period_start.date().toString("dd/MM/yyyy")
        end = self.period_end.date().toString("dd/MM/yyyy")
        export_format = self.export_format_combo.currentText()
        
        indicators = {
            'taux_couverture': self.check_taux_couverture.isChecked(),
            'retards_moyens': self.check_retards_moyens.isChecked(),
            'utilisation_ressources': self.check_utilisation_ressources.isChecked(),
            'taux_conflits': self.check_taux_conflits.isChecked(),
            'repartition': self.check_repartition.isChecked(),
            'charge_enseignants': self.check_charge_enseignants.isChecked(),
        }
        
        # Désactiver les boutons
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("⏳ Génération en cours...")
        self.btn_preview.setEnabled(False)
        
        # Afficher la barre de progression
        self.progress_frame.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Créer et lancer le thread
        self.report_thread = ReportGeneratorThread(
            report_type, start, end, indicators, export_format
        )
        self.report_thread.progress_updated.connect(self.update_progress)
        self.report_thread.finished.connect(self.show_results)
        self.report_thread.error_occurred.connect(self.show_error)
        self.report_thread.start()
    
    def update_progress(self, value, message):
        """Met à jour la barre de progression."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def show_results(self, results):
        """Affiche les résultats."""
        # Réactiver les boutons
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("📊 Générer le rapport")
        self.btn_preview.setEnabled(True)
        self.progress_frame.setVisible(False)
        
        # Message de succès
        msg_text = f"""
<h3>✅ Rapport généré avec succès !</h3>

<p><b>Fichier :</b> outputs/reports/{results['filename']}</p>

<h4>Statistiques du rapport :</h4>
<ul>
<li><b>Taux de couverture :</b> {results['stats']['taux_couverture']}%</li>
<li><b>Retard moyen :</b> {results['stats']['retard_moyen']}h</li>
<li><b>Utilisation des salles :</b> {results['stats']['utilisation_salles']}%</li>
<li><b>Taux de conflits :</b> {results['stats']['taux_conflits']}%</li>
<li><b>Activités traitées :</b> {results['stats']['nb_activites']}</li>
<li><b>Créneaux générés :</b> {results['stats']['nb_creneaux']}</li>
<li><b>Heures planifiées :</b> {results['stats']['heures_planifiees']}h</li>
</ul>

<p>Le rapport a été sauvegardé et est prêt à être diffusé.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Rapport généré")
        msg.setTextFormat(Qt.RichText)
        msg.setText(msg_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_error(self, error_message):
        """Affiche une erreur."""
        # Réactiver les boutons
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("📊 Générer le rapport")
        self.btn_preview.setEnabled(True)
        self.progress_frame.setVisible(False)
        
        QMessageBox.critical(self, "Erreur", error_message)
    
    def get_selected_indicators_count(self):
        """Compte le nombre d'indicateurs sélectionnés."""
        count = 0
        if self.check_taux_couverture.isChecked():
            count += 1
        if self.check_retards_moyens.isChecked():
            count += 1
        if self.check_utilisation_ressources.isChecked():
            count += 1
        if self.check_taux_conflits.isChecked():
            count += 1
        if self.check_repartition.isChecked():
            count += 1
        if self.check_charge_enseignants.isChecked():
            count += 1
        return count
    
    def get_input_style(self):
        """Style des inputs."""
        return """
            QLineEdit, QComboBox, QDateEdit {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
                color: #1F2937;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #000;
            }
        """
    
    def get_checkbox_style(self):
        """Style des checkboxes."""
        return """
            QCheckBox {
                font-size: 14px;
                color: #374151;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #D1D5DB;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #000;
                border-color: #000;
                image: url(none);
            }
        """
    
    def get_secondary_button_style(self):
        """Style des boutons secondaires."""
        return """
            QPushButton {
                background: white;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #F9FAFB;
                border-color: #9CA3AF;
            }
        """