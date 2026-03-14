"""
Onglet Analyse des Retards — UC7 — 100% SQLite
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QComboBox,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from datetime import date

from src.database.db_manager import db_manager
from src.database.models import (
    AcademicActivityModel, CohortModel, ScheduleSlotModel,
    ActivityStatusEnum
)


class AnalysisTab(QWidget):
    """Onglet analyse des retards — UC7 — données réelles depuis SQLite."""

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.session = db_manager.get_session()
        self.retards_data = []
        self.init_ui()
        self.load_data()

    # ══════════════════════════════════════════════════════════
    # CHARGEMENT SQLITE
    # ══════════════════════════════════════════════════════════

    def load_data(self):
        """Charge les données de retard depuis SQLite."""
        try:
            self.retards_data = []
            today = date.today()

            activities = self.session.query(AcademicActivityModel).all()
            for act in activities:
                volume = act.volume_hours or 0
                done = act.hours_done or 0
                progression = round((done / volume * 100) if volume > 0 else 0)

                # Calcul alpha (retard Pfair)
                charge = act.charge_factor or 0
                if charge > 0 and act.activation_date:
                    jours_ecoules = max(0, (today - act.activation_date).days)
                    heures_ideales = charge * jours_ecoules
                    alpha = round(heures_ideales - done, 2) if heures_ideales > 0 else 0.0
                else:
                    alpha = 0.0

                retard_h = max(0, round(volume - done, 1))
                cohorte_nom = act.cohort.name if act.cohort else "?"

                self.retards_data.append({
                    'activite':         act.name,
                    'type':             act.type.value if act.type else "?",
                    'cohorte':          cohorte_nom,
                    'volume_heures':    volume,
                    'heures_realisees': done,
                    'retard_heures':    retard_h,
                    'alpha':            alpha,
                    'progression':      progression,
                })

            # Trier par alpha décroissant (plus urgents en premier)
            self.retards_data.sort(key=lambda x: x['alpha'], reverse=True)
            self.refresh_table(self.retards_data)
            self.update_statistics()

        except Exception as e:
            print(f"Erreur chargement analysis: {e}")

    # ══════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # En-tête
        title = QLabel("Analyse des Retards Académiques")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC7 — Suivi de la progression et détection des activités en retard")
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(subtitle)

        # Statistiques
        stats_layout = QHBoxLayout()
        self.stat_total   = self._make_stat_card("Total activités",   "0", "#3B82F6")
        self.stat_retard  = self._make_stat_card("En retard",         "0", "#EF4444")
        self.stat_urgente = self._make_stat_card("Urgentes (α≥1)",    "0", "#DC2626")
        self.stat_ok      = self._make_stat_card("Dans les délais",   "0", "#10B981")
        for card in [self.stat_total, self.stat_retard, self.stat_urgente, self.stat_ok]:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        # Filtres
        filter_layout = QHBoxLayout()
        self.filter_cohorte = QComboBox()
        self.filter_cohorte.addItem("Toutes les cohortes")
        self.filter_cohorte.setFixedHeight(38)
        self.filter_cohorte.currentTextChanged.connect(self.apply_filter)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet("background:#3B82F6; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_refresh.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("Filtrer :"))
        filter_layout.addWidget(self.filter_cohorte)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_refresh)
        layout.addLayout(filter_layout)

        # Légende couleurs
        legend = QHBoxLayout()
        for color, label in [("#DC2626","🔴 Critique α≥1"), ("#F59E0B","🟠 À surveiller 0.5≤α<1"), ("#10B981","🟢 Dans les délais α<0.5")]:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{color}; font-weight:bold; font-size:12px;")
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Activité", "Type", "Cohorte",
            "Volume (h)", "Réalisé (h)", "Retard (h)",
            "Indice α", "Progression"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 8):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #E5E7EB; border-radius: 8px; }
            QHeaderView::section { background:#F9FAFB; font-weight:bold; padding:8px; border:none; border-bottom:1px solid #E5E7EB; }
            QTableWidget::item { padding: 6px; }
        """)
        layout.addWidget(self.table)

    def _make_stat_card(self, label, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background:{color}; border-radius:12px; padding:16px; }}
        """)
        v = QVBoxLayout(frame)
        lbl_val = QLabel(value)
        lbl_val.setObjectName("val")
        lbl_val.setStyleSheet("font-size:32px; font-weight:bold; color:white;")
        lbl_val.setAlignment(Qt.AlignCenter)
        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet("font-size:13px; color:white; opacity:0.9;")
        lbl_lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl_val)
        v.addWidget(lbl_lbl)
        return frame

    def _set_stat(self, card, value):
        for child in card.findChildren(QLabel):
            if child.objectName() == "val":
                child.setText(str(value))

    # ══════════════════════════════════════════════════════════
    # AFFICHAGE
    # ══════════════════════════════════════════════════════════

    def refresh_table(self, data):
        self.table.setRowCount(0)

        # Mettre à jour le filtre cohortes
        cohortes = sorted(set(d['cohorte'] for d in self.retards_data))
        current = self.filter_cohorte.currentText()
        self.filter_cohorte.blockSignals(True)
        self.filter_cohorte.clear()
        self.filter_cohorte.addItem("Toutes les cohortes")
        for c in cohortes:
            self.filter_cohorte.addItem(c)
        idx = self.filter_cohorte.findText(current)
        if idx >= 0:
            self.filter_cohorte.setCurrentIndex(idx)
        self.filter_cohorte.blockSignals(False)

        for row, d in enumerate(data):
            self.table.insertRow(row)
            alpha = d['alpha']

            # Couleur de fond selon alpha
            if alpha >= 1.0:
                bg = QColor("#FEE2E2")
            elif alpha >= 0.5:
                bg = QColor("#FEF3C7")
            else:
                bg = QColor("#D1FAE5")

            vals = [
                d['activite'], d['type'], d['cohorte'],
                f"{d['volume_heures']}h", f"{d['heures_realisees']}h",
                f"{d['retard_heures']}h", f"{alpha:.2f}",
                f"{d['progression']}%"
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setBackground(bg)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            # Barre de progression dans la colonne Progression
            bar = QProgressBar()
            bar.setValue(d['progression'])
            bar.setStyleSheet("""
                QProgressBar { border:1px solid #ccc; border-radius:4px; background:#f0f0f0; height:20px; }
                QProgressBar::chunk { background: #10B981; border-radius:4px; }
            """)
            self.table.setCellWidget(row, 7, bar)

    def update_statistics(self):
        total   = len(self.retards_data)
        retard  = sum(1 for d in self.retards_data if d['alpha'] >= 0.5)
        urgente = sum(1 for d in self.retards_data if d['alpha'] >= 1.0)
        ok      = sum(1 for d in self.retards_data if d['alpha'] < 0.5)
        self._set_stat(self.stat_total,   total)
        self._set_stat(self.stat_retard,  retard)
        self._set_stat(self.stat_urgente, urgente)
        self._set_stat(self.stat_ok,      ok)

    def apply_filter(self, cohorte):
        if cohorte == "Toutes les cohortes":
            self.refresh_table(self.retards_data)
        else:
            filtre = [d for d in self.retards_data if d['cohorte'] == cohorte]
            self.refresh_table(filtre)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()