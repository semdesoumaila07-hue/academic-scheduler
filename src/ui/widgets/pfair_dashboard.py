"""
Tableau de bord style Pfair Scheduler.
KPI, graphiques (répartition par type, statut), activités récentes, alertes.
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# Couleurs des icônes KPI (style Pfair)
KPI_COLORS = {
    'universities': '#4A90E2',   # bleu
    'ufr': '#7ED321',            # vert
    'teachers': '#BD10E0',       # violet
    'activities': '#F5A623',     # orange
    'classes': '#BD10E0',        # violet
    'students': '#F8E71C',       # jaune/rose
    'hours_planned': '#50E3C2',  # bleu clair
    'volume_total': '#F5A623',   # orange
}


def create_kpi_card(label: str, value: str, color_key: str = 'activities'):
    """Crée une carte KPI style Pfair (fond clair, icône colorée à droite).
    Retourne (card, value_label) pour permettre la mise à jour."""
    card = QFrame()
    card.setObjectName("kpi_card")
    card.setStyleSheet("""
        QFrame#kpi_card {
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            padding: 16px;
        }
    """)
    card.setMinimumHeight(100)

    layout = QHBoxLayout(card)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(12)

    # Texte à gauche
    text_widget = QWidget()
    text_layout = QVBoxLayout(text_widget)
    text_layout.setSpacing(4)
    text_layout.setContentsMargins(0, 0, 0, 0)

    value_label = QLabel(value)
    value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
    value_label.setObjectName("kpi_value")
    text_layout.addWidget(value_label)

    label_widget = QLabel(label)
    label_widget.setStyleSheet("font-size: 12px; color: #6c757d;")
    text_layout.addWidget(label_widget)

    layout.addWidget(text_widget)
    layout.addStretch()

    # Icône colorée à droite (cercle simulé par un label)
    color = KPI_COLORS.get(color_key, '#4A90E2')
    icon_circle = QLabel("●")
    icon_circle.setStyleSheet(f"font-size: 36px; color: {color};")
    icon_circle.setAlignment(Qt.AlignCenter)
    layout.addWidget(icon_circle)

    return card, value_label


class ActivityTypeChart(QWidget):
    """Graphique camembert - Répartition par type d'activité."""

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data or {'CM': 50, 'TD': 33, 'TP': 17}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if HAS_MATPLOTLIB:
            fig = Figure(figsize=(4, 3), facecolor='white')
            ax = fig.add_subplot(111)

            labels = list(self.data.keys())
            sizes = list(self.data.values())
            colors = ['#4A90E2', '#50E3C2', '#F5A623'][:len(labels)]

            ax.pie(sizes, labels=[f"{l} ({s}%)" for l, s in zip(labels, sizes)],
                   colors=colors, autopct='', startangle=90)
            ax.axis('equal')

            canvas = FigureCanvasQTAgg(fig)
            canvas.setMinimumHeight(220)
            layout.addWidget(canvas)
        else:
            placeholder = QLabel("Graphique non disponible (matplotlib requis)")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #6c757d; padding: 40px;")
            layout.addWidget(placeholder)


class ActivityStatusChart(QWidget):
    """Graphique en barres - Statut des activités."""

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data or {
            'Créées': 0, 'Validées': 0, 'Planifiées': 6,
            'En cours': 0, 'Terminées': 0
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if HAS_MATPLOTLIB:
            fig = Figure(figsize=(4, 3), facecolor='white')
            ax = fig.add_subplot(111)

            labels = list(self.data.keys())
            values = list(self.data.values())

            bars = ax.bar(labels, values, color='#F5A623', edgecolor='none')
            ax.set_ylabel('Nombre')
            ax.set_ylim(0, max(values) * 1.2 + 1 if values else 8)
            fig.autofmt_xdate()

            canvas = FigureCanvasQTAgg(fig)
            canvas.setMinimumHeight(220)
            layout.addWidget(canvas)
        else:
            placeholder = QLabel("Graphique non disponible (matplotlib requis)")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #6c757d; padding: 40px;")
            layout.addWidget(placeholder)


def create_activity_card(name: str, subtitle: str, status: str = "scheduled"):
    """Crée une carte d'activité récente style Pfair."""
    card = QFrame()
    card.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            padding: 12px;
        }
    """)
    layout = QHBoxLayout(card)
    layout.setContentsMargins(12, 10, 12, 10)

    text_layout = QVBoxLayout()
    text_layout.setSpacing(4)
    name_label = QLabel(name)
    name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
    sub_label = QLabel(subtitle)
    sub_label.setStyleSheet("font-size: 12px; color: #6c757d;")
    text_layout.addWidget(name_label)
    text_layout.addWidget(sub_label)
    layout.addLayout(text_layout)
    layout.addStretch()

    status_tag = QLabel(status)
    status_tag.setStyleSheet("""
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
    """)
    layout.addWidget(status_tag)
    return card


class PfairDashboard(QWidget):
    """Tableau de bord principal style Pfair Scheduler."""

    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.load_data()

    def set_session(self, session):
        """Définit la session BD et recharge les données."""
        self.session = session
        self.load_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Titre
        title = QLabel("Tableau de bord")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        subtitle = QLabel("Système d'Ordonnancement Académique P-équitable")
        subtitle.setStyleSheet("color: #6c757d; font-size: 14px;")
        layout.addWidget(subtitle)

        # KPI cards (2 lignes de 4)
        kpi_grid = QGridLayout()
        self.kpi_value_labels = {}
        kpis = [
            ("Universités", "universities", "universities"),
            ("UFR", "ufr", "ufr"),
            ("Enseignants", "teachers", "teachers"),
            ("Activités", "activities", "activities"),
            ("Classes", "classes", "classes"),
            ("Étudiants", "students", "students"),
            ("Heures planifiées", "hours_planned", "hours_planned"),
            ("Volume total", "volume_total", "volume_total"),
        ]
        for i, (label, key, color_key) in enumerate(kpis):
            card, value_label = create_kpi_card("0", label, color_key)
            self.kpi_value_labels[key] = value_label
            kpi_grid.addWidget(card, i // 4, i % 4)
        layout.addLayout(kpi_grid)

        # Rangée charts + activités récentes
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # Répartition par type d'activité
        type_card = QFrame()
        type_card.setStyleSheet("""
            QFrame { background: white; border-radius: 8px; padding: 16px;
                     border: 1px solid #e9ecef; }
        """)
        type_layout = QVBoxLayout(type_card)
        type_title = QLabel("Répartition par type d'activité")
        type_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        type_title.setAlignment(Qt.AlignCenter)
        type_layout.addWidget(type_title)
        self.type_chart = ActivityTypeChart({})
        type_layout.addWidget(self.type_chart)
        type_card.setMinimumWidth(320)
        charts_row.addWidget(type_card)

        # Statut des activités
        status_card = QFrame()
        status_card.setStyleSheet("""
            QFrame { background: white; border-radius: 8px; padding: 16px;
                     border: 1px solid #e9ecef; }
        """)
        status_layout = QVBoxLayout(status_card)
        status_title = QLabel("Statut des activités")
        status_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        status_title.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(status_title)
        self.status_chart = ActivityStatusChart({})
        status_layout.addWidget(self.status_chart)
        status_card.setMinimumWidth(320)
        charts_row.addWidget(status_card)

        layout.addLayout(charts_row)

        # Activités récentes + Alertes
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        # Activités récentes
        recent_card = QFrame()
        recent_card.setStyleSheet("""
            QFrame { background: white; border-radius: 8px; padding: 16px;
                     border: 1px solid #e9ecef; }
        """)
        recent_layout = QVBoxLayout(recent_card)
        recent_header = QLabel("✓ Activités récentes")
        recent_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        recent_layout.addWidget(recent_header)
        self.recent_activities_container = QVBoxLayout()
        self.recent_activities_container.setSpacing(10)
        recent_layout.addLayout(self.recent_activities_container)
        recent_card.setMinimumWidth(400)
        bottom_row.addWidget(recent_card)

        # Alertes et notifications
        alerts_card = QFrame()
        alerts_card.setStyleSheet("""
            QFrame { background: white; border-radius: 8px; padding: 16px;
                     border: 1px solid #e9ecef; }
        """)
        alerts_layout = QVBoxLayout(alerts_card)
        alerts_header = QLabel("⚠ Alertes et notifications")
        alerts_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        alerts_layout.addWidget(alerts_header)
        self.alerts_placeholder = QLabel("Aucune alerte pour le moment.")
        self.alerts_placeholder.setStyleSheet("color: #6c757d; font-size: 13px; padding: 20px;")
        alerts_layout.addWidget(self.alerts_placeholder)
        alerts_card.setMinimumWidth(400)
        bottom_row.addWidget(alerts_card)

        layout.addLayout(bottom_row)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def load_data(self):
        """Charge les données depuis la base et met à jour les widgets."""
        if not self.session:
            self._set_default_data()
            return

        try:
            from ..database.repositories import (
                UniversityRepository, UFRRepository, TeacherRepository,
                ActivityRepository, CohortRepository, StudentRepository
            )
            from ..database.models import ActivityTypeEnum, ActivityStatusEnum
            from sqlalchemy import func

            univ_repo = UniversityRepository(self.session)
            ufr_repo = UFRRepository(self.session)
            teacher_repo = TeacherRepository(self.session)
            activity_repo = ActivityRepository(self.session)
            cohort_repo = CohortRepository(self.session)
            student_repo = StudentRepository(self.session)

            n_univ = univ_repo.count()
            n_ufr = ufr_repo.count()
            n_teachers = teacher_repo.count()
            n_activities = activity_repo.count()
            n_cohorts = cohort_repo.count()
            cohorts = cohort_repo.get_all(limit=1000)
            n_students = sum(c.student_count for c in cohorts)

            activities = activity_repo.get_all(limit=1000)
            total_volume = sum(a.volume_hours for a in activities)
            total_done = sum(a.hours_done for a in activities)
            hours_planned = int(total_done)

            self._update_kpis(
                universities=n_univ, ufr=n_ufr, teachers=n_teachers,
                activities=n_activities, classes=n_cohorts, students=n_students,
                hours_planned=hours_planned, volume_total=int(total_volume)
            )

            # Répartition par type
            type_counts = {}
            for a in activities:
                t = a.type.value if hasattr(a.type, 'value') else str(a.type)
                short = {'Cours Magistral': 'CM', 'Travaux Dirigés': 'TD',
                         'Travaux Pratiques': 'TP'}.get(t, t[:2] if len(t) >= 2 else t)
                type_counts[short] = type_counts.get(short, 0) + 1
            total_t = sum(type_counts.values()) or 1
            type_data = {k: round(v / total_t * 100) for k, v in type_counts.items()}
            if not type_data:
                type_data = {'CM': 50, 'TD': 33, 'TP': 17}
            self._update_type_chart(type_data)

            # Statut
            status_labels = {
                ActivityStatusEnum.PENDING: 'Créées',
                ActivityStatusEnum.SCHEDULED: 'Planifiées',
                ActivityStatusEnum.IN_PROGRESS: 'En cours',
                ActivityStatusEnum.COMPLETED: 'Terminées',
            }
            status_data = {v: 0 for v in status_labels.values()}
            status_data['Validées'] = 0
            for a in activities:
                s = a.status
                lbl = status_labels.get(s, 'Créées')
                status_data[lbl] = status_data.get(lbl, 0) + 1
            self._update_status_chart(status_data)

            # Activités récentes (5 dernières)
            if activities:
                def _sort_key(a):
                    dt = getattr(a, 'updated_at', None) or getattr(a, 'created_at', None)
                    return dt if dt else datetime.min
                recent = sorted(activities, key=_sort_key, reverse=True)[:5]
                self._update_recent_activities(recent)
            else:
                self._update_recent_activities([])
        except Exception as e:
            self._set_default_data()

    def _update_kpis(self, **kwargs):
        """Met à jour les valeurs des cartes KPI."""
        for key, val in kwargs.items():
            if key not in getattr(self, 'kpi_value_labels', {}):
                continue
            if key == 'hours_planned' or key == 'volume_total':
                display = f"{val}h"
            else:
                display = str(val)
            self.kpi_value_labels[key].setText(display)

    def _update_type_chart(self, data: dict):
        """Met à jour le graphique des types."""
        if hasattr(self.type_chart, 'data'):
            self.type_chart.data = data
        # Rebuild chart (simplification: on recrée le widget)
        old = self.type_chart
        parent = old.parent()
        layout = parent.layout()
        idx = layout.indexOf(old)
        self.type_chart = ActivityTypeChart(data)
        layout.replaceWidget(old, self.type_chart)
        old.deleteLater()

    def _update_status_chart(self, data: dict):
        old = self.status_chart
        parent = old.parent()
        layout = parent.layout()
        self.status_chart = ActivityStatusChart(data)
        layout.replaceWidget(old, self.status_chart)
        old.deleteLater()

    def _update_recent_activities(self, activities: list):
        """Efface et réaffiche les activités récentes."""
        while self.recent_activities_container.count():
            item = self.recent_activities_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        status_map = {'PENDING': 'created', 'SCHEDULED': 'scheduled', 'IN_PROGRESS': 'in progress',
                      'COMPLETED': 'completed'}
        for a in activities:
            st = getattr(a.status, 'name', str(a.status)) if hasattr(a, 'status') else 'PENDING'
            status = status_map.get(st, 'scheduled')
            type_val = getattr(a.type, 'value', str(a.type)) if hasattr(a, 'type') else ''
            short = {'Cours Magistral': 'CM', 'Travaux Dirigés': 'TD',
                     'Travaux Pratiques': 'TP'}.get(type_val, type_val[:2] if type_val else '')
            sub = f"{short} - {int(a.volume_hours)}h" if hasattr(a, 'volume_hours') else ""
            card = create_activity_card(a.name, sub, status)
            self.recent_activities_container.addWidget(card)

    def _set_default_data(self):
        """Données par défaut si pas de session."""
        self._update_kpis(
            universities=2, ufr=3, teachers=5, activities=6,
            classes=4, students=250, hours_planned=140, volume_total=140
        )
        self._update_type_chart({'CM': 50, 'TD': 33, 'TP': 17})
        self._update_status_chart({'Créées': 0, 'Validées': 0, 'Planifiées': 6, 'En cours': 0, 'Terminées': 0})
        examples = [
            ("Algorithmique avancée", "CM - 30h", "scheduled"),
            ("Algorithmique avancée TD", "TD - 20h", "scheduled"),
            ("Base de données", "CM - 25h", "scheduled"),
            ("Base de données TD", "TD - 20h", "scheduled"),
            ("Réseaux informatiques", "CM - 20h", "scheduled"),
        ]
        while self.recent_activities_container.count():
            item = self.recent_activities_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for name, sub, st in examples:
            self.recent_activities_container.addWidget(create_activity_card(name, sub, st))
