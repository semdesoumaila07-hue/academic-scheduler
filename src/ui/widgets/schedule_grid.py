"""
Widget de grille d'emploi du temps.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ScheduleGrid(QWidget):
    """
    Widget pour afficher une grille d'emploi du temps.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QHBoxLayout()
        
        title = QLabel("Emploi du Temps de la Semaine")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        header.addWidget(title)
        
        header.addStretch()
        
        btn_prev = QPushButton("◀ Semaine précédente")
        header.addWidget(btn_prev)
        
        btn_next = QPushButton("Semaine suivante ▶")
        header.addWidget(btn_next)
        
        layout.addLayout(header)
        
        # Grille
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 6 jours (Lundi à Samedi)
        self.table.setRowCount(10)    # 10 créneaux horaires
        
        # En-têtes des colonnes (jours)
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        self.table.setHorizontalHeaderLabels(days)
        
        # En-têtes des lignes (heures)
        hours = [
            "8h-9h", "9h-10h", "10h-11h", "11h-12h",
            "12h-13h", "13h-14h", "14h-15h", "15h-16h",
            "16h-17h", "17h-18h"
        ]
        self.table.setVerticalHeaderLabels(hours)
        
        # Configuration de la table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Style
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Légende
        legend = QHBoxLayout()
        legend.addWidget(QLabel("Légende:"))
        
        legend.addWidget(self.create_legend_item("Cours", "#3498db"))
        legend.addWidget(self.create_legend_item("TD", "#2ecc71"))
        legend.addWidget(self.create_legend_item("TP", "#f39c12"))
        legend.addWidget(self.create_legend_item("Examen", "#e74c3c"))
        legend.addWidget(self.create_legend_item("Bloqué", "#95a5a6"))
        
        legend.addStretch()
        
        layout.addLayout(legend)
        
        # Charger un exemple
        self.load_example_schedule()
    
    def create_legend_item(self, text: str, color: str):
        """Crée un élément de légende."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 10, 0)
        
        color_box = QLabel()
        color_box.setFixedSize(20, 20)
        color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #7f8c8d;")
        layout.addWidget(color_box)
        
        label = QLabel(text)
        layout.addWidget(label)
        
        return widget
    
    def load_example_schedule(self):
        """Charge un exemple d'emploi du temps."""
        # Exemple: Lundi 8h-10h Algorithmique
        item = QTableWidgetItem("Algorithmique\nDr. KABORE\nSalle A101")
        item.setBackground(QColor("#3498db"))
        item.setForeground(QColor("white"))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(0, 0, item)
        self.table.setSpan(0, 0, 2, 1)  # Occupe 2 heures
        
        # Mardi 10h-12h Bases de données
        item = QTableWidgetItem("Bases de données\nDr. TRAORE\nSalle B202")
        item.setBackground(QColor("#2ecc71"))
        item.setForeground(QColor("white"))
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(2, 1, item)
        self.table.setSpan(2, 1, 2, 1)
    
    def clear_schedule(self):
        """Efface la grille."""
        self.table.clearContents()
        self.table.clearSpans()
    
    def add_slot(self, day: int, start_hour: int, duration: int, 
                 activity: str, teacher: str, room: str, color: str = "#3498db"):
        """
        Ajoute un créneau dans la grille.
        
        Args:
            day: Jour (0=Lundi, 1=Mardi, etc.)
            start_hour: Heure de début (0-9)
            duration: Durée en heures
            activity: Nom de l'activité
            teacher: Nom de l'enseignant
            room: Salle
            color: Couleur de fond
        """
        item = QTableWidgetItem(f"{activity}\n{teacher}\n{room}")
        item.setBackground(QColor(color))
        item.setForeground(QColor("white"))
        item.setTextAlignment(Qt.AlignCenter)
        
        self.table.setItem(start_hour, day, item)
        if duration > 1:
            self.table.setSpan(start_hour, day, duration, 1)