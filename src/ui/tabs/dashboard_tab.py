"""
Onglet du tableau de bord moderne.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter, QColor


class StatCard(QFrame):
    """Carte statistique moderne avec icône et couleur."""
    
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 20px;
                min-width: 180px;
                min-height: 120px;
                border: none;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Icône en haut
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 40px;")
        icon_label.setAlignment(Qt.AlignLeft)
        
        # Valeur au centre
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 42px; font-weight: bold; color: #333;")
        value_label.setAlignment(Qt.AlignLeft)
        
        # Titre en bas
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        title_label.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(icon_label)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        layout.addStretch()


class DashboardTab(QWidget):
    """Onglet du tableau de bord principal."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        
        # === EN-TÊTE ===
        header_layout = QVBoxLayout()
        
        title = QLabel("Tableau de bord")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Système d'Ordonnancement Académique P-équitable")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)
        
        main_layout.addLayout(header_layout)
        
        # === SCROLL AREA ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(30)
        
        # === CARTES STATISTIQUES ===
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Ligne 1
        stats_grid.addWidget(StatCard("Universités", 2, "🎓", "#E3F2FD"), 0, 0)
        stats_grid.addWidget(StatCard("UFR", 3, "🏛️", "#E8F5E9"), 0, 1)
        stats_grid.addWidget(StatCard("Enseignants", 5, "👨‍🏫", "#F3E5F5"), 0, 2)
        stats_grid.addWidget(StatCard("Activités", 6, "📚", "#FFF3E0"), 0, 3)
        
        # Ligne 2
        stats_grid.addWidget(StatCard("Classes", 4, "👥", "#E1F5FE"), 1, 0)
        stats_grid.addWidget(StatCard("Étudiants", 250, "🎓", "#FCE4EC"), 1, 1)
        stats_grid.addWidget(StatCard("Heures planifiées", "140h", "⏱️", "#E0F2F1"), 1, 2)
        stats_grid.addWidget(StatCard("Volume total", "140h", "📊", "#FFF8E1"), 1, 3)
        
        content_layout.addLayout(stats_grid)
        
        # === GRAPHIQUES ===
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Graphique camembert
        pie_widget = self.create_pie_chart()
        charts_layout.addWidget(pie_widget)
        
        # Graphique barres
        bar_widget = self.create_bar_chart()
        charts_layout.addWidget(bar_widget)
        
        content_layout.addLayout(charts_layout)
        
        # === SECTIONS INFÉRIEURES ===
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Activités récentes
        recent_widget = self.create_recent_activities()
        bottom_layout.addWidget(recent_widget)
        
        # Alertes
        alerts_widget = self.create_alerts_section()
        bottom_layout.addWidget(alerts_widget)
        
        content_layout.addLayout(bottom_layout)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_pie_chart(self):
        """Crée le graphique camembert de répartition."""
        # Conteneur
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        
        # Titre
        title = QLabel("Répartition par type d'activité")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Série
        series = QPieSeries()
        series.append("CM", 50)
        series.append("TD", 33)
        series.append("TP", 17)
        
        # Couleurs et labels
        slices = series.slices()
        colors = [QColor("#2196F3"), QColor("#4CAF50"), QColor("#FFC107")]
        
        for i, slice in enumerate(slices):
            slice.setBrush(colors[i])
            slice.setLabelVisible(True)
            slice.setLabel(f"{slice.label()} ({slice.percentage()*100:.0f}%)")
        
        # Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.setBackgroundVisible(False)
        
        # View
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        layout.addWidget(chart_view)
        
        return container
    
    def create_bar_chart(self):
        """Crée le graphique en barres du statut."""
        # Conteneur
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        
        # Titre
        title = QLabel("Statut des activités")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Série
        set0 = QBarSet("Activités")
        set0.append([0, 0, 6, 0, 0])
        set0.setColor(QColor("#FFC107"))
        
        series = QBarSeries()
        series.append(set0)
        
        # Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        
        # Axes
        categories = ["Créées", "Validées", "Planifiées", "En cours", "Terminées"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 8)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        # View
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        layout.addWidget(chart_view)
        
        return container
    
    def create_recent_activities(self):
        """Crée la section activités récentes."""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        
        # Titre
        title_layout = QHBoxLayout()
        icon = QLabel("✅")
        icon.setStyleSheet("font-size: 24px;")
        title = QLabel("Activités récentes")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Liste
        activities = [
            ("Algorithmique avancée", "CM - 30h"),
            ("Algorithmique avancée TD", "TD - 20h"),
            ("Base de données", "CM - 25h"),
            ("Base de données TD", "TD - 20h"),
            ("Réseaux informatiques", "CM - 20h"),
        ]
        
        for name, info in activities:
            item = QFrame()
            item.setStyleSheet("QFrame { background: #F5F5F5; border-radius: 8px; padding: 12px; margin: 5px 0; }")
            item_layout = QHBoxLayout(item)
            
            # Nom
            name_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            info_label = QLabel(info)
            info_label.setStyleSheet("color: #666; font-size: 12px;")
            name_layout.addWidget(name_label)
            name_layout.addWidget(info_label)
            
            # Badge
            badge = QLabel("scheduled")
            badge.setStyleSheet("""
                background-color: #E3F2FD;
                color: #2196F3;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            """)
            badge.setFixedHeight(28)
            
            item_layout.addLayout(name_layout)
            item_layout.addStretch()
            item_layout.addWidget(badge)
            
            layout.addWidget(item)
        
        layout.addStretch()
        
        return container
    
    def create_alerts_section(self):
        """Crée la section alertes."""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(container)
        
        # Titre
        title_layout = QHBoxLayout()
        icon = QLabel("⚠️")
        icon.setStyleSheet("font-size: 24px;")
        title = QLabel("Alertes et notifications")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Message vide
        empty = QLabel("Aucune alerte pour le moment")
        empty.setStyleSheet("color: #999; font-style: italic; margin-top: 40px;")
        empty.setAlignment(Qt.AlignCenter)
        layout.addWidget(empty)
        
        layout.addStretch()
        
        return container