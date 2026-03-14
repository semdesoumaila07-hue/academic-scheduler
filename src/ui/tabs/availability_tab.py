"""
Onglet Disponibilités — UC10 — 100% SQLite
Permet à un enseignant de déclarer ses disponibilités hebdomadaires.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QComboBox,
    QTimeEdit, QMessageBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QColor
from datetime import date, time

from src.database.db_manager import db_manager
from src.database.models import (
    TeacherModel, TeacherAvailabilityModel
)


JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
JOURS_IDX = {j: i for i, j in enumerate(JOURS)}


class AvailabilityTab(QWidget):
    """Onglet de gestion des disponibilités enseignants — SQLite."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.session = db_manager.get_session()
        self.enseignants = []
        self.dispos = []
        self.init_ui()
        self.load_enseignants()

    def load_enseignants(self):
        try:
            rows = self.session.query(TeacherModel).order_by(TeacherModel.full_name).all()
            self.enseignants = rows
            self.teacher_combo.clear()
            self.teacher_combo.addItem("— Sélectionner un enseignant —")
            for t in rows:
                self.teacher_combo.addItem(t.full_name, t.id)
        except Exception as e:
            print(f"Erreur chargement enseignants: {e}")

    def load_dispos(self, teacher_id):
        try:
            self.dispos = self.session.query(TeacherAvailabilityModel).filter_by(
                teacher_id=teacher_id
            ).order_by(TeacherAvailabilityModel.day_of_week).all()
            self.refresh_table()
        except Exception as e:
            print(f"Erreur chargement dispos: {e}")

    def add_dispo(self):
        teacher_id = self.teacher_combo.currentData()
        if not teacher_id:
            QMessageBox.warning(self, "Attention", "Sélectionnez un enseignant.")
            return
        dialog = DispoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            try:
                dispo = TeacherAvailabilityModel(
                    teacher_id=teacher_id,
                    day_of_week=JOURS_IDX.get(d['jour'], 0),
                    start_time=d['debut'],
                    end_time=d['fin'],
                    period_start=date(2025, 9, 1),
                    period_end=date(2026, 7, 31),
                )
                self.session.add(dispo)
                self.session.commit()
                self.load_dispos(teacher_id)
                QMessageBox.information(self, "Succès", f"✅ Disponibilité ajoutée : {d['jour']} {d['debut']}–{d['fin']}")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    def delete_dispo(self):
        teacher_id = self.teacher_combo.currentData()
        row = self.table.currentRow()
        if row < 0 or row >= len(self.dispos):
            QMessageBox.warning(self, "Attention", "Sélectionnez une disponibilité à supprimer.")
            return
        dispo = self.dispos[row]
        jour = JOURS[dispo.day_of_week] if dispo.day_of_week < len(JOURS) else "?"
        if QMessageBox.question(self, "Confirmation",
                f"Supprimer la disponibilité du {jour} ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.session.delete(dispo)
                self.session.commit()
                self.load_dispos(teacher_id)
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    def on_teacher_changed(self, index):
        teacher_id = self.teacher_combo.currentData()
        if teacher_id:
            self.load_dispos(teacher_id)
        else:
            self.table.setRowCount(0)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Gestion des Disponibilités Enseignants")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC10 — Déclarez les créneaux horaires disponibles pour chaque enseignant")
        subtitle.setStyleSheet("font-size:14px; color:#666;")
        layout.addWidget(subtitle)

        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Enseignant :"))
        self.teacher_combo = QComboBox()
        self.teacher_combo.setFixedHeight(40)
        self.teacher_combo.setMinimumWidth(300)
        self.teacher_combo.currentIndexChanged.connect(self.on_teacher_changed)
        sel_layout.addWidget(self.teacher_combo)
        sel_layout.addStretch()

        btn_add = QPushButton("➕ Ajouter disponibilité")
        btn_add.setFixedHeight(40)
        btn_add.setStyleSheet("background:#10B981; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_add.clicked.connect(self.add_dispo)

        btn_del = QPushButton("🗑️ Supprimer")
        btn_del.setFixedHeight(40)
        btn_del.setStyleSheet("background:#EF4444; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_del.clicked.connect(self.delete_dispo)

        sel_layout.addWidget(btn_add)
        sel_layout.addWidget(btn_del)
        layout.addLayout(sel_layout)

        grid_title = QLabel("Grille hebdomadaire")
        grid_title.setStyleSheet("font-size:16px; font-weight:bold; color:#374151;")
        layout.addWidget(grid_title)

        self.grid_frame = QFrame()
        self.grid_frame.setStyleSheet("background:white; border:1px solid #E5E7EB; border-radius:8px; padding:10px;")
        self.grid_layout = QHBoxLayout(self.grid_frame)
        for jour in JOURS:
            col = QVBoxLayout()
            lbl = QLabel(jour)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight:bold; color:#1a1a1a; font-size:13px; padding:4px;")
            col.addWidget(lbl)
            col.addStretch()
            self.grid_layout.addLayout(col)
        layout.addWidget(self.grid_frame)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Jour", "Heure début", "Heure fin", "Période"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { border:1px solid #E5E7EB; border-radius:8px; }
            QHeaderView::section { background:#F9FAFB; font-weight:bold; padding:8px; border:none; border-bottom:1px solid #E5E7EB; }
        """)
        layout.addWidget(self.table)

    def refresh_table(self):
        self.table.setRowCount(0)
        for row, d in enumerate(self.dispos):
            self.table.insertRow(row)
            jour = JOURS[d.day_of_week] if d.day_of_week < len(JOURS) else str(d.day_of_week)
            debut = str(d.start_time)[:5] if d.start_time else "?"
            fin   = str(d.end_time)[:5]   if d.end_time   else "?"
            periode = f"{d.period_start} → {d.period_end}" if d.period_start and d.period_end else "—"
            for col, val in enumerate([jour, debut, fin, periode]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor("#D1FAE5"))
                self.table.setItem(row, col, item)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_enseignants()


class DispoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Disponibilité")
        self.setMinimumWidth(380)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("🗓️ Ajouter une Disponibilité")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.jour_combo = QComboBox()
        self.jour_combo.addItems(JOURS)
        self.jour_combo.setFixedHeight(36)

        self.debut = QTimeEdit()
        self.debut.setTime(QTime(8, 0))
        self.debut.setFixedHeight(36)
        self.debut.setDisplayFormat("HH:mm")

        self.fin = QTimeEdit()
        self.fin.setTime(QTime(18, 0))
        self.fin.setFixedHeight(36)
        self.fin.setDisplayFormat("HH:mm")

        form.addRow("Jour :", self.jour_combo)
        form.addRow("Début :", self.debut)
        form.addRow("Fin :", self.fin)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedSize(110, 38)
        btn_cancel.setStyleSheet("background:#e0e0e0; border:none; border-radius:6px;")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("✅ Enregistrer")
        btn_ok.setFixedSize(140, 38)
        btn_ok.setStyleSheet("background:#10B981; color:white; border:none; border-radius:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.validate)

        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def validate(self):
        if self.debut.time() >= self.fin.time():
            QMessageBox.warning(self, "Erreur", "L'heure de début doit être avant l'heure de fin.")
            return
        self.accept()

    def get_data(self):
        t_debut = self.debut.time()
        t_fin   = self.fin.time()
        return {
            'jour':  self.jour_combo.currentText(),
            'debut': time(t_debut.hour(), t_debut.minute()),
            'fin':   time(t_fin.hour(),   t_fin.minute()),
        }