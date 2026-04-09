"""
Onglet Analyse des Retards — UC7 — 100% SQLite
Agrégation multi-niveaux : Activité / Cohorte / Parcours / UFR / Université
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QComboBox,
    QProgressBar, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from datetime import date

from src.database.db_manager import db_manager
from src.database.models import (
    AcademicActivityModel, CohortModel, ActivityStatusEnum,
    ProgramModel, UFRModel, UniversityModel
)


class AnalysisTab(QWidget):
    """Onglet analyse des retards — UC7 — agrégation multi-niveaux."""

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.session = db_manager.get_session()
        self.retards_data = []          # données brutes activité par activité
        self.init_ui()
        self.load_data()

    # ══════════════════════════════════════════════════════════
    # CHARGEMENT SQLITE — données brutes
    # ══════════════════════════════════════════════════════════

    def load_data(self):
        """Charge les données de retard depuis SQLite et les agrège à tous les niveaux."""
        try:
            self.retards_data = []
            today = date.today()

            activities = self.session.query(AcademicActivityModel).all()
            for act in activities:
                volume = act.volume_hours or 0
                done   = act.hours_done or 0
                progression = round((done / volume * 100) if volume > 0 else 0)

                # Calcul alpha (retard Pfair) : α = (U×t − H) / U
                charge = act.charge_factor or 0
                if charge > 0 and act.activation_date:
                    jours_ecoules = max(0, (today - act.activation_date).days)
                    heures_ideales = charge * jours_ecoules
                    alpha = round(heures_ideales - done, 2) if heures_ideales > 0 else 0.0
                else:
                    alpha = 0.0

                retard_h = max(0, round(volume - done, 1))

                # Remonte la hiérarchie
                cohorte   = act.cohort
                cohorte_nom = cohorte.name if cohorte else "?"
                programme = cohorte.program if cohorte else None
                programme_nom = programme.name if programme else "?"
                ufr       = programme.ufr if programme else None
                ufr_nom   = ufr.name if ufr else "?"
                universite = ufr.university if ufr else None
                universite_nom = universite.name if universite else "?"

                self.retards_data.append({
                    'activite':         act.name,
                    'type':             act.type.value if act.type else "?",
                    'cohorte':          cohorte_nom,
                    'parcours':         programme_nom,
                    'ufr':              ufr_nom,
                    'universite':       universite_nom,
                    'volume_heures':    volume,
                    'heures_realisees': done,
                    'retard_heures':    retard_h,
                    'alpha':            alpha,
                    'progression':      progression,
                })

            # Trier par alpha décroissant (plus urgents en premier)
            self.retards_data.sort(key=lambda x: x['alpha'], reverse=True)

            # Rafraîchit les 4 vues
            self.refresh_table_activites(self.retards_data)
            self.refresh_table_cohortes()
            self.refresh_table_parcours()
            self.refresh_table_ufr()
            self.refresh_table_universite()
            self.update_statistics()
            self._populate_filters()

        except Exception as e:
            print(f"Erreur chargement analysis: {e}")

    # ══════════════════════════════════════════════════════════
    # AGRÉGATION par niveau
    # ══════════════════════════════════════════════════════════

    def _aggregate(self, key):
        """Agrège les données brutes par la clé donnée (cohorte/parcours/ufr/universite)."""
        agg = {}
        for d in self.retards_data:
            nom = d[key]
            if nom not in agg:
                agg[nom] = {
                    'nom': nom, 'nb_activites': 0,
                    'volume_total': 0, 'heures_total': 0,
                    'retard_total': 0, 'alpha_max': 0, 'alpha_moy': 0,
                    'alphas': []
                }
            agg[nom]['nb_activites']  += 1
            agg[nom]['volume_total']  += d['volume_heures']
            agg[nom]['heures_total']  += d['heures_realisees']
            agg[nom]['retard_total']  += d['retard_heures']
            agg[nom]['alphas'].append(d['alpha'])

        # Calcul des métriques agrégées
        result = []
        for nom, a in agg.items():
            alphas = a['alphas']
            a['alpha_max'] = round(max(alphas), 2)
            a['alpha_moy'] = round(sum(alphas) / len(alphas), 2) if alphas else 0
            a['progression'] = round(
                (a['heures_total'] / a['volume_total'] * 100)
                if a['volume_total'] > 0 else 0
            )
            result.append(a)

        result.sort(key=lambda x: x['alpha_max'], reverse=True)
        return result

    # ══════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # En-tête
        title = QLabel("Analyse des Retards Académiques")
        title.setStyleSheet("font-size:32px; font-weight:bold; color:#1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC7 — Suivi multi-niveaux : Activité / Cohorte / Parcours / UFR / Université")
        subtitle.setStyleSheet("font-size:14px; color:#666;")
        layout.addWidget(subtitle)

        # KPI cards
        stats_layout = QHBoxLayout()
        self.stat_total   = self._make_stat_card("Total activités",  "0", "#3B82F6")
        self.stat_retard  = self._make_stat_card("En retard",        "0", "#EF4444")
        self.stat_urgente = self._make_stat_card("Urgentes (α≥1)",   "0", "#DC2626")
        self.stat_ok      = self._make_stat_card("Dans les délais",  "0", "#10B981")
        for card in [self.stat_total, self.stat_retard, self.stat_urgente, self.stat_ok]:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        # Filtres globaux
        filter_layout = QHBoxLayout()
        self.filter_niveau = QComboBox()
        self.filter_niveau.addItems(["Toutes cohortes", "Tous parcours", "Toutes UFR", "Toutes universités"])
        self.filter_niveau.setFixedHeight(36)

        self.filter_valeur = QComboBox()
        self.filter_valeur.addItem("— Tout afficher —")
        self.filter_valeur.setFixedHeight(36)
        self.filter_valeur.setMinimumWidth(200)
        self.filter_niveau.currentIndexChanged.connect(self._on_niveau_changed)
        self.filter_valeur.currentIndexChanged.connect(self._on_filtre_changed)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedHeight(36)
        btn_refresh.setStyleSheet(
            "background:#3B82F6; color:white; border-radius:6px; padding:0 16px; font-weight:bold;"
        )
        btn_refresh.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("Niveau :"))
        filter_layout.addWidget(self.filter_niveau)
        filter_layout.addWidget(QLabel("Filtrer :"))
        filter_layout.addWidget(self.filter_valeur)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_refresh)
        layout.addLayout(filter_layout)

        # Légende
        legend = QHBoxLayout()
        for color, label in [
            ("#DC2626", "🔴 Critique α≥1"),
            ("#F59E0B", "🟠 À surveiller 0.5≤α<1"),
            ("#10B981", "🟢 Dans les délais α<0.5")
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color:{color}; font-weight:bold; font-size:12px;")
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)

        # ── Onglets multi-niveaux ──────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border:1px solid #E5E7EB; border-radius:8px; }
            QTabBar::tab { background:#F9FAFB; padding:8px 20px; font-size:13px; border:none; }
            QTabBar::tab:selected { background:white; font-weight:bold; color:#3B82F6;
                                    border-bottom:2px solid #3B82F6; }
        """)

        # Onglet 1 — Par activité
        self.table_activites = self._make_table([
            "Activité", "Type", "Cohorte", "Parcours", "UFR",
            "Volume (h)", "Réalisé (h)", "Retard (h)", "Indice α", "Progression"
        ])
        self.tabs.addTab(self._wrap(self.table_activites), "📋 Par activité")

        # Onglet 2 — Par cohorte
        self.table_cohortes = self._make_table([
            "Cohorte", "Nb activités", "Volume (h)", "Réalisé (h)",
            "Retard (h)", "α max", "α moyen", "Progression"
        ])
        self.tabs.addTab(self._wrap(self.table_cohortes), "🎓 Par cohorte")

        # Onglet 3 — Par parcours
        self.table_parcours = self._make_table([
            "Parcours", "Nb activités", "Volume (h)", "Réalisé (h)",
            "Retard (h)", "α max", "α moyen", "Progression"
        ])
        self.tabs.addTab(self._wrap(self.table_parcours), "📚 Par parcours")

        # Onglet 4 — Par UFR
        self.table_ufr = self._make_table([
            "UFR", "Nb activités", "Volume (h)", "Réalisé (h)",
            "Retard (h)", "α max", "α moyen", "Progression"
        ])
        self.tabs.addTab(self._wrap(self.table_ufr), "🏛️ Par UFR")

        # Onglet 5 — Par université
        self.table_universite = self._make_table([
            "Université", "Nb activités", "Volume (h)", "Réalisé (h)",
            "Retard (h)", "α max", "α moyen", "Progression"
        ])
        self.tabs.addTab(self._wrap(self.table_universite), "🎓 Par université")

        layout.addWidget(self.tabs)

    def _make_table(self, headers):
        """Crée un QTableWidget stylisé avec les en-têtes donnés."""
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, len(headers)):
            t.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setStyleSheet("""
            QTableWidget { border:1px solid #E5E7EB; border-radius:8px; }
            QHeaderView::section { background:#F9FAFB; font-weight:bold; padding:8px;
                                   border:none; border-bottom:1px solid #E5E7EB; }
            QTableWidget::item { padding:6px; }
        """)
        return t

    def _wrap(self, widget):
        """Enveloppe un widget dans un QWidget avec padding."""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(8, 8, 8, 8)
        l.addWidget(widget)
        return w

    def _make_stat_card(self, label, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background:{color}; border-radius:12px; padding:16px; }}")
        v = QVBoxLayout(frame)
        lbl_val = QLabel(value)
        lbl_val.setObjectName("val")
        lbl_val.setStyleSheet("font-size:32px; font-weight:bold; color:white;")
        lbl_val.setAlignment(Qt.AlignCenter)
        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet("font-size:13px; color:white;")
        lbl_lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl_val)
        v.addWidget(lbl_lbl)
        return frame

    def _set_stat(self, card, value):
        for child in card.findChildren(QLabel):
            if child.objectName() == "val":
                child.setText(str(value))

    # ══════════════════════════════════════════════════════════
    # REMPLISSAGE DES TABLES
    # ══════════════════════════════════════════════════════════

    def _bg(self, alpha):
        if alpha >= 1.0:   return QColor("#FEE2E2")
        if alpha >= 0.5:   return QColor("#FEF3C7")
        return                    QColor("#D1FAE5")

    def refresh_table_activites(self, data):
        t = self.table_activites
        t.setRowCount(0)
        for row, d in enumerate(data):
            t.insertRow(row)
            bg = self._bg(d['alpha'])
            vals = [
                d['activite'], d['type'], d['cohorte'], d['parcours'], d['ufr'],
                f"{d['volume_heures']}h", f"{d['heures_realisees']}h",
                f"{d['retard_heures']}h", f"{d['alpha']:.2f}", f"{d['progression']}%"
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setBackground(bg)
                item.setTextAlignment(Qt.AlignCenter)
                t.setItem(row, col, item)
            bar = QProgressBar()
            bar.setValue(d['progression'])
            bar.setStyleSheet("""
                QProgressBar { border:1px solid #ccc; border-radius:4px;
                               background:#f0f0f0; height:20px; }
                QProgressBar::chunk { background:#10B981; border-radius:4px; }
            """)
            t.setCellWidget(row, 9, bar)

    def _fill_agg_table(self, table, data):
        """Remplit une table d'agrégation (cohorte/parcours/UFR/université)."""
        table.setRowCount(0)
        for row, d in enumerate(data):
            table.insertRow(row)
            bg = self._bg(d['alpha_max'])
            vals = [
                d['nom'],
                str(d['nb_activites']),
                f"{d['volume_total']:.1f}h",
                f"{d['heures_total']:.1f}h",
                f"{d['retard_total']:.1f}h",
                f"{d['alpha_max']:.2f}",
                f"{d['alpha_moy']:.2f}",
                f"{d['progression']}%"
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setBackground(bg)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
            bar = QProgressBar()
            bar.setValue(d['progression'])
            bar.setStyleSheet("""
                QProgressBar { border:1px solid #ccc; border-radius:4px;
                               background:#f0f0f0; height:20px; }
                QProgressBar::chunk { background:#10B981; border-radius:4px; }
            """)
            table.setCellWidget(row, 7, bar)

    def refresh_table_cohortes(self):
        self._fill_agg_table(self.table_cohortes, self._aggregate('cohorte'))

    def refresh_table_parcours(self):
        self._fill_agg_table(self.table_parcours, self._aggregate('parcours'))

    def refresh_table_ufr(self):
        self._fill_agg_table(self.table_ufr, self._aggregate('ufr'))

    def refresh_table_universite(self):
        self._fill_agg_table(self.table_universite, self._aggregate('universite'))

    # ══════════════════════════════════════════════════════════
    # FILTRES DYNAMIQUES
    # ══════════════════════════════════════════════════════════

    def _populate_filters(self):
        """Remplit le ComboBox de valeurs selon le niveau sélectionné."""
        niveau_idx = self.filter_niveau.currentIndex()
        key = ['cohorte', 'parcours', 'ufr', 'universite'][niveau_idx]
        valeurs = sorted(set(d[key] for d in self.retards_data))

        self.filter_valeur.blockSignals(True)
        self.filter_valeur.clear()
        self.filter_valeur.addItem("— Tout afficher —")
        for v in valeurs:
            self.filter_valeur.addItem(v)
        self.filter_valeur.blockSignals(False)

    def _on_niveau_changed(self):
        self._populate_filters()
        self._on_filtre_changed()

    def _on_filtre_changed(self):
        niveau_idx = self.filter_niveau.currentIndex()
        key = ['cohorte', 'parcours', 'ufr', 'universite'][niveau_idx]
        valeur = self.filter_valeur.currentText()

        if valeur == "— Tout afficher —":
            data_filtree = self.retards_data
        else:
            data_filtree = [d for d in self.retards_data if d[key] == valeur]

        self.refresh_table_activites(data_filtree)

        # Redirige vers l'onglet activité pour montrer le résultat du filtre
        if valeur != "— Tout afficher —":
            self.tabs.setCurrentIndex(0)

    def update_statistics(self):
        total   = len(self.retards_data)
        retard  = sum(1 for d in self.retards_data if d['alpha'] >= 0.5)
        urgente = sum(1 for d in self.retards_data if d['alpha'] >= 1.0)
        ok      = sum(1 for d in self.retards_data if d['alpha'] < 0.5)
        self._set_stat(self.stat_total,   total)
        self._set_stat(self.stat_retard,  retard)
        self._set_stat(self.stat_urgente, urgente)
        self._set_stat(self.stat_ok,      ok)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()