"""
<<<<<<< HEAD
Onglet du tableau de bord — VERSION SQLite
Toutes les données viennent de DashboardService / SQLAlchemy.
=======
Onglet du tableau de bord moderne.
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
<<<<<<< HEAD
from PyQt5.QtChart import (
    QChart, QChartView, QPieSeries,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
)
from PyQt5.QtGui import QPainter, QColor

from src.database.db_manager import db_manager
from src.services.dashboard_service import DashboardService


class StatCard(QFrame):
    """Carte statistique moderne avec icône et couleur."""

=======
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter, QColor


class StatCard(QFrame):
    """Carte statistique moderne avec icône et couleur."""
    
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
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
<<<<<<< HEAD
            QLabel {{ border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 40px;")
        icon_label.setAlignment(Qt.AlignLeft)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 42px; font-weight: bold; color: #333;")
        self.value_label.setAlignment(Qt.AlignLeft)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        title_label.setAlignment(Qt.AlignLeft)

        layout.addWidget(icon_label)
        layout.addWidget(self.value_label)
        layout.addWidget(title_label)
        layout.addStretch()

    def set_value(self, value):
        """Met à jour la valeur affichée."""
        self.value_label.setText(str(value))


class DashboardTab(QWidget):
    """Onglet du tableau de bord — données depuis SQLite via DashboardService."""

    CARD_COLORS = [
        "#E3F2FD", "#E8F5E9", "#F3E5F5", "#FFF3E0",
        "#E1F5FE", "#FCE4EC", "#E0F2F1", "#FFF8E1",
    ]

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._dashboard_data = None
        self.stats = {}
        self._load_dashboard_data()   # ✅ SQLite dès l'ouverture
        self.init_ui()

    def showEvent(self, event):
        """Rafraîchit automatiquement quand on revient sur cet onglet."""
        super().showEvent(event)
        self.refresh_stats()

    # ==========================================
    # CHARGEMENT DEPUIS SQLITE
    # ==========================================

    def _load_dashboard_data(self):
        """Charge toutes les données depuis SQLite via DashboardService."""
        try:
            db_manager.initialize()
            session = db_manager.get_session()
            try:
                service = DashboardService(session)
                data = service.get_dashboard_data()
                self._dashboard_data = data
                # Construire self.stats depuis les KPIs retournés
                kpis = data.get('kpis', [])
                kpi_map = {k['label']: k['value'] for k in kpis}
                self.stats = {
                    'universites': kpi_map.get('Universités', 0),
                    'ufrs': kpi_map.get('UFR', 0),
                    'cohortes': kpi_map.get('Classes', 0),
                    'enseignants': kpi_map.get('Enseignants', 0),
                    'activites': kpi_map.get('Activités', 0),
                    'etudiants': kpi_map.get('Étudiants', 0),
                    'heures_planifiees': kpi_map.get('Heures planifiées', '0h'),
                    'volume_total': kpi_map.get('Volume total', '0h'),
                }
            finally:
                session.close()
        except Exception as e:
            print(f"⚠️ Dashboard: impossible de charger les données ({e})")
            self._dashboard_data = None
            self.stats = {}

    def refresh_stats(self):
        """Recharge depuis SQLite et met à jour toutes les cartes."""
        self._load_dashboard_data()
        self._update_all_cards()

    def _update_all_cards(self):
        """Met à jour chaque StatCard avec les valeurs fraîches."""
        if not self._dashboard_data:
            return
        kpis = self._dashboard_data.get('kpis', [])
        card_map = {
            'Universités': 'card_universites',
            'UFR': 'card_ufr',
            'Classes': 'card_classes',
            'Enseignants': 'card_enseignants',
            'Activités': 'card_activites',
            'Étudiants': 'card_etudiants',
            'Heures planifiées': 'card_heures',
            'Volume total': 'card_volume',
        }
        for kpi in kpis:
            attr = card_map.get(kpi['label'])
            if attr and hasattr(self, attr):
                getattr(self, attr).set_value(kpi['value'])

    # ==========================================
    # INTERFACE
    # ==========================================

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        # En-tête
        title = QLabel("Tableau de bord")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        subtitle = QLabel("Système d'Ordonnancement Académique P-équitable")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(30)

        # Cartes KPI depuis SQLite
        kpis = self._dashboard_data.get('kpis', []) if self._dashboard_data else []
        if not kpis:
            kpis = [
                {'label': 'Universités', 'value': self.stats.get('universites', 0), 'icon': '🎓'},
                {'label': 'UFR', 'value': self.stats.get('ufrs', 0), 'icon': '🏛️'},
                {'label': 'Enseignants', 'value': self.stats.get('enseignants', 0), 'icon': '👨‍🏫'},
                {'label': 'Activités', 'value': self.stats.get('activites', 0), 'icon': '📚'},
                {'label': 'Classes', 'value': self.stats.get('cohortes', 0), 'icon': '👥'},
                {'label': 'Étudiants', 'value': self.stats.get('etudiants', 0), 'icon': '🎓'},
                {'label': 'Heures planifiées', 'value': self.stats.get('heures_planifiees', '0h'), 'icon': '⏱️'},
                {'label': 'Volume total', 'value': self.stats.get('volume_total', '0h'), 'icon': '📊'},
            ]

        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        card_attr_map = {
            'Universités': 'card_universites',
            'UFR': 'card_ufr',
            'Classes': 'card_classes',
            'Enseignants': 'card_enseignants',
            'Activités': 'card_activites',
            'Étudiants': 'card_etudiants',
            'Heures planifiées': 'card_heures',
            'Volume total': 'card_volume',
        }
        for i, kpi in enumerate(kpis):
            row, col = i // 4, i % 4
            color = self.CARD_COLORS[i % len(self.CARD_COLORS)]
            card = StatCard(kpi['label'], kpi['value'], kpi['icon'], color)
            attr = card_attr_map.get(kpi['label'])
            if attr:
                setattr(self, attr, card)
            stats_grid.addWidget(card, row, col)
        content_layout.addLayout(stats_grid)

        # Graphiques
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        charts_layout.addWidget(self.create_pie_chart())
        charts_layout.addWidget(self.create_bar_chart())
        content_layout.addLayout(charts_layout)

        # Sections inférieures
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.addWidget(self.create_recent_activities())
        bottom_layout.addWidget(self.create_alerts_section())
        content_layout.addLayout(bottom_layout)
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_pie_chart(self):
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: white; border-radius: 12px; padding: 20px; }")
        layout = QVBoxLayout(container)
        title = QLabel("Répartition par type d'activité")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        series = QPieSeries()
        by_type = self._dashboard_data.get('activities_by_type', {}) if self._dashboard_data else {}
        colors = [QColor("#2196F3"), QColor("#4CAF50"), QColor("#FFC107"),
                  QColor("#F44336"), QColor("#9C27B0"), QColor("#00BCD4")]
        if by_type and sum(by_type.values()) > 0:
            for i, (label, count) in enumerate(by_type.items()):
                if count > 0:
                    series.append(label, count)
            for i, sl in enumerate(series.slices()):
                if i < len(colors):
                    sl.setBrush(colors[i])
                sl.setLabelVisible(True)
                sl.setLabel(f"{sl.label()} ({sl.percentage()*100:.0f}%)")
        else:
            series.append("Aucune donnée", 1)
            series.slices()[0].setBrush(QColor("#E0E0E0"))
            series.slices()[0].setLabelVisible(True)

=======
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
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.setBackgroundVisible(False)
<<<<<<< HEAD
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        layout.addWidget(chart_view)
        return container

    def create_bar_chart(self):
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: white; border-radius: 12px; padding: 20px; }")
        layout = QVBoxLayout(container)
        title = QLabel("Statut des activités")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        by_status = self._dashboard_data.get('activities_status', {}) if self._dashboard_data else {}
        categories = list(by_status.keys()) if by_status else ["En attente", "En cours", "Terminé"]
        values = list(by_status.values()) if by_status else [0, 0, 0]
        axis_y_max = max(8, max(values) + 2) if values else 8

        set0 = QBarSet("Activités")
        set0.append(values)
        set0.setColor(QColor("#FFC107"))
        series = QBarSeries()
        series.append(set0)

=======
        
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
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
<<<<<<< HEAD

=======
        
        # Axes
        categories = ["Créées", "Validées", "Planifiées", "En cours", "Terminées"]
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
<<<<<<< HEAD

        axis_y = QValueAxis()
        axis_y.setRange(0, axis_y_max)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        chart.legend().setVisible(False)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        layout.addWidget(chart_view)
        return container

    def create_recent_activities(self):
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: white; border-radius: 12px; padding: 20px; }")
        layout = QVBoxLayout(container)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("✅"))
        t = QLabel("Activités récentes")
        t.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(t)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        activities = self._dashboard_data.get('recent_activities', []) if self._dashboard_data else []
        for act in activities:
            name = act.get('name', '—')
            act_type = act.get('type', '')
            volume = act.get('volume_hours', 0)
            status = act.get('status', '')
            info = f"{act_type} - {int(volume)}h" if act_type else f"{int(volume)}h"

            item = QFrame()
            item.setStyleSheet("QFrame { background: #F5F5F5; border-radius: 8px; padding: 12px; margin: 5px 0; }")
            item_layout = QHBoxLayout(item)
            name_layout = QVBoxLayout()
            n = QLabel(name)
            n.setStyleSheet("font-weight: bold; font-size: 14px;")
            i_lbl = QLabel(info)
            i_lbl.setStyleSheet("color: #666; font-size: 12px;")
            name_layout.addWidget(n)
            name_layout.addWidget(i_lbl)
            badge = QLabel(status or "—")
            badge.setStyleSheet("""
                background-color: #E3F2FD; color: #2196F3;
                padding: 6px 14px; border-radius: 12px;
                font-size: 11px; font-weight: bold;
            """)
            badge.setFixedHeight(28)
            item_layout.addLayout(name_layout)
            item_layout.addStretch()
            item_layout.addWidget(badge)
            layout.addWidget(item)

        if not activities:
            empty = QLabel("Aucune activité récente")
            empty.setStyleSheet("color: #999; font-style: italic; margin-top: 16px;")
            layout.addWidget(empty)
        layout.addStretch()
        return container

    def create_alerts_section(self):
        container = QFrame()
        container.setStyleSheet("QFrame { background-color: white; border-radius: 12px; padding: 20px; }")
        layout = QVBoxLayout(container)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("⚠️"))
        t = QLabel("Alertes et notifications")
        t.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_layout.addWidget(t)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        delayed = self._dashboard_data.get('delayed_activities', []) if self._dashboard_data else []
        if delayed:
            for act in delayed:
                name = act.get('name', '—')
                delay_hours = act.get('delay_hours', 0)
                item = QFrame()
                item.setStyleSheet("QFrame { background: #FFF3E0; border-radius: 8px; padding: 12px; margin: 5px 0; }")
                item_layout = QHBoxLayout(item)
                lbl = QLabel(f"{name} — retard : {delay_hours:.0f}h")
                lbl.setStyleSheet("font-size: 13px;")
                item_layout.addWidget(lbl)
                layout.addWidget(item)
        else:
            empty = QLabel("Aucune alerte pour le moment")
            empty.setStyleSheet("color: #999; font-style: italic; margin-top: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
        layout.addStretch()
=======
        
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
        
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        return container