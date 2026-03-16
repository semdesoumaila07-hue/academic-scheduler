"""
<<<<<<< HEAD
UC9 - Onglet Consultation des Emplois du Temps
100% SQLite : lit ScheduleSlotModel au lieu de schedules.json
Correction : _reload_all et _populate_target_combo préservent la sélection actuelle
"""
import csv
from datetime import date, datetime, timedelta
from datetime import time as dtime
from PyQt5.QtCore import QDate

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QFileDialog, QMessageBox, QFrame,
    QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor

from src.database.db_manager import db_manager
from src.database.models import ScheduleSlotModel
from src.database.repositories.cohort_repository import CohortRepository
from src.database.repositories.teacher_repository import TeacherRepository


JOURS     = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
HEURE_DEBUT = 8
HEURE_FIN   = 19
SLOT_H      = 65  # pixels par heure

TYPE_COLORS = {
    "CM":         ("#BBDEFB", "#1565C0"),
    "TD":         ("#C8E6C9", "#2E7D32"),
    "TP":         ("#FFE0B2", "#E65100"),
    "Examen":     ("#FCE4EC", "#880E4F"),
    "Soutenance": ("#E1BEE7", "#6A1B9A"),
}


def _alpha_to_border(alpha):
    if alpha is None:   return "#9E9E9E"
    if alpha >= 1.0:    return "#C62828"
    if alpha >= 0.5:    return "#F9A825"
    return "#2E7D32"


class CourseBlock(QFrame):
    def __init__(self, slot_data, parent=None):
        super().__init__(parent)
        self.slot_data = slot_data
        bg, fg       = TYPE_COLORS.get(slot_data.get('activity_type', ''), ("#E0E0E0", "#333"))
        border_color = _alpha_to_border(slot_data.get('alpha'))
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid #ccc;
                border-left: 4px solid {border_color};
                border-radius: 4px;
                margin: 1px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 5, 5, 5)
        layout.setSpacing(2)

        # ── Ligne horaire ──────────────────────────────────────
        start  = slot_data.get('start', '08:00')
        end    = slot_data.get('end',   '10:00')
        hour_lbl = QLabel(f"⏰ {start} – {end}")
        hour_lbl.setStyleSheet(
            f"color: {fg}; font-weight: bold; font-size: 11px; "
            f"background: rgba(0,0,0,0.07); border-radius:3px; padding:1px 4px;"
        )
        layout.addWidget(hour_lbl)

        # ── Nom du cours ───────────────────────────────────────
        name_lbl = QLabel(slot_data.get('activity', '—'))
        name_lbl.setStyleSheet(f"color: {fg}; font-weight: bold; font-size: 11px;")
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        # ── Type + Salle ───────────────────────────────────────
        act_type = slot_data.get('activity_type', '')
        room     = slot_data.get('room', '')
        info_lbl = QLabel(f"📍 {act_type}  |  {room}")
        info_lbl.setStyleSheet(f"color: {fg}; font-size: 10px;")
        layout.addWidget(info_lbl)

        # ── Enseignant ────────────────────────────────────────
        teach_lbl = QLabel(f"👤 {slot_data.get('teacher', '')}")
        teach_lbl.setStyleSheet("color: #444; font-size: 10px;")
        layout.addWidget(teach_lbl)

        self.setToolTip(
            f"Activité : {slot_data.get('activity', '')}\n"
            f"Type     : {act_type}\n"
            f"Salle    : {room}\n"
            f"Ens.     : {slot_data.get('teacher', '')}\n"
            f"Cohorte  : {slot_data.get('cohort', '')}\n"
            f"α        : {slot_data.get('alpha', 'N/A')}"
        )


class TimetableGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        time_col = QWidget()
        time_col.setFixedWidth(55)
        tcl = QVBoxLayout(time_col)
        tcl.setContentsMargins(0, 30, 0, 0)
        tcl.setSpacing(0)
        for h in range(HEURE_DEBUT, HEURE_FIN):
            lbl = QLabel(f"{h:02d}:00")
            lbl.setFixedHeight(SLOT_H)
            lbl.setStyleSheet("color: #555; font-size: 10px;")
            lbl.setAlignment(Qt.AlignTop | Qt.AlignRight)
            tcl.addWidget(lbl)
        tcl.addStretch()
        main.addWidget(time_col)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(2)

        for col, jour in enumerate(JOURS):
            h = QLabel(jour)
            h.setFixedHeight(28)
            h.setAlignment(Qt.AlignCenter)
            h.setStyleSheet(
                "font-weight: bold; font-size: 12px; color: #1a73e8; "
                "background: #e8f0fe; border-radius: 4px;"
            )
            self.grid_layout.addWidget(h, 0, col)

        for row in range(1, HEURE_FIN - HEURE_DEBUT + 1):
            for col in range(len(JOURS)):
                cell = QFrame()
                cell.setFixedHeight(SLOT_H)
                cell.setStyleSheet("background: #fafafa; border: 1px solid #eee;")
                self.grid_layout.addWidget(cell, row, col)

        self.grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main.addWidget(self.grid_widget)

    def load_slots(self, slots):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and isinstance(item.widget(), CourseBlock):
                item.widget().deleteLater()
                self.grid_layout.removeItem(item)

        for slot in slots:
            try:
                slot_date = slot.get('date')
                if isinstance(slot_date, str):
                    slot_date = datetime.fromisoformat(slot_date).date()
                weekday = slot_date.weekday()
                if weekday > 5:
                    continue
                start_str = slot.get('start', '08:00')
                end_str   = slot.get('end',   '10:00')
                start_h   = int(start_str.split(':')[0]) if ':' in start_str else int(start_str)
                end_h     = int(end_str.split(':')[0])   if ':' in end_str   else int(end_str)
                if start_h < HEURE_DEBUT or end_h > HEURE_FIN:
                    continue
                row_start = start_h - HEURE_DEBUT + 1
                row_span  = max(1, end_h - start_h)
                block = CourseBlock(slot)
                block.setFixedHeight(SLOT_H * row_span - 4)
                self.grid_layout.addWidget(block, row_start, weekday, row_span, 1)
            except Exception:
                pass


class TimetableTab(QWidget):
    """UC9 — Consultation des emplois du temps — 100% SQLite."""

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._all_slots = []
        self._teachers  = []
        self._cohorts   = []
        # Semaine affichée (lundi de la semaine courante)
        today = date.today()
        self._week_start = today - timedelta(days=today.weekday())
        self._init_ui()
        self._load_db_data()
        self._update_week_label()

    def _load_db_data(self):
        try:
            session = db_manager.get_session()
            self._teachers = TeacherRepository(session).get_all()
            self._cohorts  = CohortRepository(session).get_all()
            self._load_slots_from_db(session)
            self._populate_target_combo()
        except Exception as e:
            print(f"[timetable_tab] Erreur DB: {e}")

    def _load_slots_from_db(self, session):
        self._all_slots = []
        try:
            slots_orm = session.query(ScheduleSlotModel).all()
            for s in slots_orm:
                if not s.date:
                    continue
                act_type = ""
                if s.activity and s.activity.type:
                    act_type = (s.activity.type.value
                                if hasattr(s.activity.type, 'value')
                                else str(s.activity.type))
                alpha = None
                if s.notes and 'alpha=' in s.notes:
                    try:
                        alpha = float(s.notes.split('alpha=')[1].split()[0])
                    except Exception:
                        alpha = s.delay_value
                start_str = (s.start_time.strftime('%H:%M')
                             if isinstance(s.start_time, dtime)
                             else str(s.start_time)[:5])
                end_str   = (s.end_time.strftime('%H:%M')
                             if isinstance(s.end_time, dtime)
                             else str(s.end_time)[:5])
                self._all_slots.append({
                    'date':          s.date,
                    'start':         start_str,
                    'end':           end_str,
                    'activity':      s.activity.name  if s.activity  else "?",
                    'activity_code': s.activity.code  if s.activity  else "",
                    'activity_type': act_type,
                    'teacher':       s.teacher.full_name if s.teacher else "Non assigné",
                    'cohort':        s.cohort.name    if s.cohort    else "?",
                    'room':          s.room or "—",
                    'alpha':         alpha,
                    'delay':         s.delay_value,
                    'cohort_id':     s.cohort_id,
                    'teacher_id':    s.teacher_id,
                    'activity_id':   s.activity_id,
                })
        except Exception as e:
            print(f"[timetable_tab] Erreur lecture schedule_slots: {e}")

    def _populate_target_combo(self):
        # ✅ Mémoriser la sélection avant de reconstruire la liste
        prev_data = self.target_combo.currentData()

        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        view = self.view_combo.currentText()

        if view == "Par cohorte":
            if self._cohorts:
                for c in self._cohorts:
                    self.target_combo.addItem(
                        f"{c.name} ({c.academic_year})",
                        userData=('cohort', c.id, c.name)
                    )
            else:
                self.target_combo.addItem("⚠️ Aucune cohorte", userData=None)
        else:
            if self._teachers:
                for t in self._teachers:
                    self.target_combo.addItem(
                        t.full_name,
                        userData=('teacher', t.id, t.full_name)
                    )
            else:
                self.target_combo.addItem("⚠️ Aucun enseignant", userData=None)

        # ✅ Restaurer la sélection par ID (pas par index)
        if prev_data:
            kind, entity_id, _ = prev_data
            for i in range(self.target_combo.count()):
                data = self.target_combo.itemData(i)
                if data and data[0] == kind and data[1] == entity_id:
                    self.target_combo.setCurrentIndex(i)
                    break

        self.target_combo.blockSignals(False)
        self._refresh_grid()

    def _reload_all(self):
        # ✅ Mémoriser vue et sélection AVANT rechargement
        prev_data = self.target_combo.currentData()
        prev_view = self.view_combo.currentText()

        # Recharger depuis SQLite
        try:
            session = db_manager.get_session()
            self._teachers = TeacherRepository(session).get_all()
            self._cohorts  = CohortRepository(session).get_all()
            self._load_slots_from_db(session)
        except Exception as e:
            print(f"[timetable_tab] Erreur reload: {e}")

        # Restaurer la vue
        self.view_combo.blockSignals(True)
        self.view_combo.setCurrentText(prev_view)
        self.view_combo.blockSignals(False)

        # Reconstruire le combo
        self.target_combo.blockSignals(True)
        self.target_combo.clear()

        if prev_view == "Par cohorte":
            for c in self._cohorts:
                self.target_combo.addItem(
                    f"{c.name} ({c.academic_year})",
                    userData=('cohort', c.id, c.name)
                )
        else:
            for t in self._teachers:
                self.target_combo.addItem(
                    t.full_name,
                    userData=('teacher', t.id, t.full_name)
                )

        # ✅ Restaurer l'enseignant/cohorte sélectionné par son ID
        if prev_data:
            kind, entity_id, _ = prev_data
            for i in range(self.target_combo.count()):
                data = self.target_combo.itemData(i)
                if data and data[0] == kind and data[1] == entity_id:
                    self.target_combo.setCurrentIndex(i)
                    break

        self.target_combo.blockSignals(False)
        self._refresh_grid()

    def _on_view_changed(self):
        self._populate_target_combo()

    def _update_week_label(self):
        end = self._week_start + timedelta(days=5)
        self.week_label.setText(
            f"{self._week_start.strftime('%d/%m')} — {end.strftime('%d/%m/%Y')}"
        )

    def _prev_week(self):
        self._week_start -= timedelta(weeks=1)
        self._update_week_label()
        self._refresh_grid()

    def _next_week(self):
        self._week_start += timedelta(weeks=1)
        self._update_week_label()
        self._refresh_grid()

    def _refresh_grid(self):
        target_data = self.target_combo.currentData()
        if not target_data or not self._all_slots:
            self.grid.load_slots([])
            self.empty_label.setVisible(True)
            self.scroll.setVisible(False)
            return

        self.empty_label.setVisible(False)
        self.scroll.setVisible(True)

        kind, entity_id, entity_name = target_data
        if kind == 'cohort':
            filtered = [s for s in self._all_slots
                        if s.get('cohort') == entity_name
                        or s.get('cohort_id') == entity_id]
        else:
            filtered = [s for s in self._all_slots
                        if s.get('teacher') == entity_name
                        or s.get('teacher_id') == entity_id]

        # ─── Filtrer par semaine affichée ────────────────────────
        week_end = self._week_start + timedelta(days=6)
        week_slots = []
        for s in filtered:
            d = s.get('date')
            if isinstance(d, str):
                d = datetime.fromisoformat(d).date()
            if d is not None and self._week_start <= d <= week_end:
                week_slots.append(s)

        self.grid.load_slots(week_slots)

        # Afficher un message si aucun créneau cette semaine
        total_slots = len(filtered)
        if total_slots > 0 and len(week_slots) == 0:
            self.empty_label.setText(
                f"⚠️ Aucun cours cette semaine.\n"
                f"({total_slots} créneau(x) au total — naviguez avec ◀ ▶)"
            )
            self.empty_label.setVisible(True)
            self.scroll.setVisible(True)
        elif total_slots == 0:
            self.empty_label.setText(
                "⚠️ Aucun emploi du temps disponible.\n"
                "Lancez d'abord l'ordonnancement (UC6)."
            )
            self.empty_label.setVisible(True)
            self.scroll.setVisible(False)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📅 Emplois du Temps")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC9 — Données lues depuis SQLite (schedule_slots)")
        subtitle.setStyleSheet("color: #555; font-size: 12px; font-style: italic;")
        layout.addWidget(subtitle)

        ctrl = QHBoxLayout(); ctrl.setSpacing(10)
        ctrl.addWidget(QLabel("Vue :"))
        self.view_combo = QComboBox()
        self.view_combo.setFixedHeight(36)
        self.view_combo.addItems(["Par cohorte", "Par enseignant"])
        self.view_combo.currentIndexChanged.connect(self._on_view_changed)
        ctrl.addWidget(self.view_combo)

        ctrl.addWidget(QLabel("Afficher :"))
        self.target_combo = QComboBox()
        self.target_combo.setFixedHeight(36)
        self.target_combo.setMinimumWidth(250)
        self.target_combo.currentIndexChanged.connect(self._refresh_grid)
        ctrl.addWidget(self.target_combo)

        btn_reload = QPushButton("🔄 Recharger")
        btn_reload.setFixedHeight(36)
        btn_reload.setStyleSheet(
            "background: #e8f0fe; color: #1a73e8; border-radius: 6px; "
            "font-weight: bold; padding: 0 12px;"
        )
        btn_reload.clicked.connect(self._reload_all)
        ctrl.addWidget(btn_reload)

        # ─── Navigation semaine ───────────────────────────────
        ctrl.addStretch()
        btn_prev = QPushButton("◀ Semaine préc.")
        btn_prev.setFixedHeight(36)
        btn_prev.setStyleSheet("background: #f5f5f5; border-radius:6px; padding:0 10px;")
        btn_prev.clicked.connect(self._prev_week)
        ctrl.addWidget(btn_prev)

        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setMinimumWidth(160)
        self.week_label.setStyleSheet("font-weight:bold; font-size:12px;")
        ctrl.addWidget(self.week_label)

        btn_next = QPushButton("Semaine suiv. ▶")
        btn_next.setFixedHeight(36)
        btn_next.setStyleSheet("background: #f5f5f5; border-radius:6px; padding:0 10px;")
        btn_next.clicked.connect(self._next_week)
        ctrl.addWidget(btn_next)

        for label, (bg, fg) in list(TYPE_COLORS.items())[:4]:
            lbl = QLabel(f" {label} ")
            lbl.setStyleSheet(
                f"background: {bg}; color: {fg}; border-radius: 3px; "
                f"font-size: 10px; padding: 2px 5px;"
            )
            ctrl.addWidget(lbl)
        layout.addLayout(ctrl)

        urg = QHBoxLayout(); urg.setSpacing(5)
        urg.addWidget(QLabel("Bordure :"))
        for color, label in [
            ("#C62828", "🔴 Critique α≥1"),
            ("#F9A825", "🟡 Urgent 0.5≤α<1"),
            ("#2E7D32", "🟢 OK α<0.5"),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"border-left: 4px solid {color}; padding-left: 5px; "
                f"font-size: 11px; color: #555;"
            )
            urg.addWidget(lbl)
        urg.addStretch()
        layout.addLayout(urg)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid = TimetableGrid()
        self.scroll.setWidget(self.grid)
        self.scroll.setStyleSheet("border: 1px solid #ddd; border-radius: 8px;")
        layout.addWidget(self.scroll)

        self.empty_label = QLabel(
            "⚠️ Aucun emploi du temps disponible.\n"
            "Lancez d'abord l'ordonnancement (UC6)."
        )
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #888; font-size: 14px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

        export_layout = QHBoxLayout(); export_layout.setSpacing(8)
        for icon, text, handler, bg in [
            ("🖨️",  "Export PDF",   self._export_pdf,   "#c62828"),
            ("📊",  "Export Excel", self._export_excel, "#2e7d32"),
            ("📅",  "Export iCal",  self._export_ical,  "#1a73e8"),
            ("📄",  "Export CSV",   self._export_csv,   "#5e35b1"),
        ]:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(38)
            btn.setStyleSheet(
                f"QPushButton {{ background: {bg}; color: white; border-radius: 6px; "
                f"font-size: 13px; padding: 0 12px; }}"
                f"QPushButton:hover {{ opacity: 0.9; }}"
            )
            btn.clicked.connect(handler)
            export_layout.addWidget(btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)

    def _get_current_slots(self):
        target_data = self.target_combo.currentData()
        if not target_data:
            return []
        kind, entity_id, entity_name = target_data
        if kind == 'cohort':
            return [s for s in self._all_slots
                    if s.get('cohort') == entity_name
                    or s.get('cohort_id') == entity_id]
        else:
            return [s for s in self._all_slots
                    if s.get('teacher') == entity_name
                    or s.get('teacher_id') == entity_id]

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "emploi_du_temps.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            doc = SimpleDocTemplate(path, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            elements = []
            target_data = self.target_combo.currentData()
            title_txt = target_data[2] if target_data else "Emploi du temps"
            elements.append(Paragraph(f"Emploi du temps — {title_txt}", styles['Title']))
            elements.append(Spacer(1, 10))
            slots = self._get_current_slots()
            if not slots:
                elements.append(Paragraph("Aucun créneau disponible.", styles['Normal']))
            else:
                rows = [["Date", "Début", "Fin", "Activité", "Type", "Salle", "Enseignant"]]
                for s in sorted(slots, key=lambda x: (str(x.get('date', '')), x.get('start', ''))):
                    rows.append([str(s.get('date', '')), s.get('start', ''), s.get('end', ''),
                                 s.get('activity', ''), s.get('activity_type', ''),
                                 s.get('room', ''), s.get('teacher', '')])
                t = Table(rows)
                t.setStyle(TableStyle([
                    ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#1a73e8')),
                    ('TEXTCOLOR',      (0,0), (-1,0), colors.white),
                    ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID',           (0,0), (-1,-1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f5f5')]),
                    ('FONTSIZE',       (0,0), (-1,-1), 9),
                ]))
                elements.append(t)
            doc.build(elements)
            QMessageBox.information(self, "Export réussi", f"PDF sauvegardé :\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Dépendance manquante",
                                "reportlab n'est pas installé.\npip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export PDF", str(e))

    def _export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "emploi_du_temps.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            import openpyxl
            from openpyxl.styles import PatternFill, Font
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Emploi du temps"
            ws.append(["Date", "Début", "Fin", "Activité", "Type", "Salle", "Enseignant", "α"])
            for col in range(1, 9):
                ws.cell(1, col).font = Font(bold=True, color="FFFFFF")
                ws.cell(1, col).fill = PatternFill(fill_type="solid", fgColor="1a73e8")
            for s in sorted(self._get_current_slots(),
                            key=lambda x: (str(x.get('date', '')), x.get('start', ''))):
                ws.append([str(s.get('date', '')), s.get('start', ''), s.get('end', ''),
                           s.get('activity', ''), s.get('activity_type', ''),
                           s.get('room', ''), s.get('teacher', ''), s.get('alpha', '')])
            wb.save(path)
            QMessageBox.information(self, "Export réussi", f"Excel sauvegardé :\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Dépendance manquante", "pip install openpyxl")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export Excel", str(e))

    def _export_ical(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export iCal", "emploi_du_temps.ics", "iCal (*.ics)"
        )
        if not path:
            return
        try:
            lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
                     "PRODID:-//Pfair Scheduler//UC9//FR",
                     "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
            for s in self._get_current_slots():
                try:
                    d = s.get('date')
                    d_str   = d.strftime('%Y%m%d') if hasattr(d, 'strftime') else str(d).replace('-', '')
                    start_t = s.get('start', '08:00').replace(':', '')
                    end_t   = s.get('end',   '10:00').replace(':', '')
                    lines += ["BEGIN:VEVENT",
                              f"DTSTART:{d_str}T{start_t}00",
                              f"DTEND:{d_str}T{end_t}00",
                              f"SUMMARY:{s.get('activity', 'Cours')} [{s.get('activity_type', '')}]",
                              f"LOCATION:{s.get('room', '')}",
                              f"DESCRIPTION:Enseignant: {s.get('teacher', '')}\\n"
                              f"Cohorte: {s.get('cohort', '')}\\nα={s.get('alpha', '')}",
                              "END:VEVENT"]
                except Exception:
                    pass
            lines.append("END:VCALENDAR")
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\r\n'.join(lines))
            QMessageBox.information(self, "Export réussi", f"iCal sauvegardé :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export iCal", str(e))

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "emploi_du_temps.csv", "CSV (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Début", "Fin", "Activité", "Type", "Salle", "Enseignant", "α"])
                for s in sorted(self._get_current_slots(),
                                key=lambda x: (str(x.get('date', '')), x.get('start', ''))):
                    writer.writerow([str(s.get('date', '')), s.get('start', ''), s.get('end', ''),
                                     s.get('activity', ''), s.get('activity_type', ''),
                                     s.get('room', ''), s.get('teacher', ''), s.get('alpha', '')])
            QMessageBox.information(self, "Export réussi", f"CSV sauvegardé :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur export CSV", str(e))

    def refresh_data(self):
        self._reload_all()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_db_data()
=======
Onglet UC6 : Consultation des emplois du temps - VERSION DESIGN MODERNE CORRIGÉE
Acteurs : Enseignant, Étudiant
Fonctionnalités principales :
- Choix du type de vue (personnelle / classe / parcours)
- Choix de la période (semaine / mois / semestre)
- Affichage sous forme de calendrier graphique simplifié (table)
- Export réel (PDF, iCal, CSV, Excel)
"""

from pathlib import Path
import csv
import json
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook


class TimetableTab(QWidget):
    """Onglet de consultation des emplois du temps (UC6) - DESIGN MODERNE."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        # Slots "simples" d'exemple (fallback) + slots réels chargés depuis data/schedules.json
        self.slots = self._build_sample_slots()
        self._load_real_slots()
        self.init_ui()

    # ==============================
    # UI
    # ==============================

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # ==========================================
        # EN-TÊTE
        # ==========================================
        header_layout = QVBoxLayout()
        
        title = QLabel("📅 Consultation des Emplois du Temps")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1a1a1a;")
        header_layout.addWidget(title)

        subtitle = QLabel(
            "UC6 - Enseignants et étudiants consultent leurs emplois du temps personnels ou de classe"
        )
        subtitle.setStyleSheet("font-size: 16px; color: #666;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # ==========================================
        # STATISTIQUES
        # ==========================================
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        self.stat_creneaux = self.create_stat_box("Créneaux affichés", "0", "#3498db")
        self.stat_heures = self.create_stat_box("Heures totales", "0h", "#27ae60")
        self.stat_jours = self.create_stat_box("Jours ouvrés", "0", "#9b59b6")
        self.stat_charge = self.create_stat_box("Charge moyenne", "0%", "#e67e22")
        
        self.stats_layout.addWidget(self.stat_creneaux)
        self.stats_layout.addWidget(self.stat_heures)
        self.stats_layout.addWidget(self.stat_jours)
        self.stats_layout.addWidget(self.stat_charge)
        
        layout.addLayout(self.stats_layout)

        # ==========================================
        # BARRE DE FILTRES
        # ==========================================
        filters_frame = QFrame()
        filters_frame.setStyleSheet(
            """
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                padding: 20px;
            }
        """
        )
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setContentsMargins(20, 20, 20, 20)
        filters_layout.setSpacing(15)

        # Ligne 1 : rôle + type de vue
        row1 = QHBoxLayout()
        row1.setSpacing(15)

        role_label = QLabel("👤 Acteur :")
        role_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        
        self.role_combo = QComboBox()
        self.role_combo.blockSignals(True)  # ← BLOQUER LES SIGNAUX pendant l'init
        self.role_combo.addItems(["Enseignant", "Étudiant"])
        self.role_combo.setFixedHeight(40)
        self.role_combo.setStyleSheet(self.get_combo_style())

        view_label = QLabel("👁️ Type de vue :")
        view_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        
        self.view_type_combo = QComboBox()
        self.view_type_combo.blockSignals(True)  # ← BLOQUER LES SIGNAUX
        self.view_type_combo.addItems(["Personnelle", "Classe", "Parcours"])
        self.view_type_combo.setFixedHeight(40)
        self.view_type_combo.setStyleSheet(self.get_combo_style())

        row1.addWidget(role_label)
        row1.addWidget(self.role_combo, 1)
        row1.addSpacing(20)
        row1.addWidget(view_label)
        row1.addWidget(self.view_type_combo, 1)

        filters_layout.addLayout(row1)

        # Ligne 2 : sélection acteur / classe
        row2 = QHBoxLayout()
        row2.setSpacing(15)

        self.target_label = QLabel("🎯 Enseignant :")
        self.target_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")

        self.target_combo = QComboBox()
        self.target_combo.blockSignals(True)  # ← BLOQUER LES SIGNAUX
        self.target_combo.setFixedHeight(40)
        self.target_combo.setStyleSheet(self.get_combo_style())
        # Valeurs exemples
        self.target_combo.addItems(
            ["KABORE Marie", "TRAORE Moussa", "SAWADOGO Fatimata", "OUATTARA Ibrahim"]
        )

        row2.addWidget(self.target_label)
        row2.addWidget(self.target_combo, 1)

        filters_layout.addLayout(row2)

        # Ligne 3 : période + navigation
        row3 = QHBoxLayout()
        row3.setSpacing(15)

        period_label = QLabel("📆 Période :")
        period_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")

        self.period_combo = QComboBox()
        self.period_combo.blockSignals(True)  # ← BLOQUER LES SIGNAUX
        self.period_combo.addItems(["Semaine", "Mois", "Semestre"])
        self.period_combo.setFixedHeight(40)
        self.period_combo.setStyleSheet(self.get_combo_style())

        self.current_period_label = QLabel(self._format_current_period())
        self.current_period_label.setStyleSheet(
            """
            font-size: 16px;
            color: #1976D2;
            font-weight: bold;
            background: #E3F2FD;
            padding: 8px 16px;
            border-radius: 6px;
            """
        )

        btn_prev = QPushButton("◀ Précédent")
        btn_prev.setFixedHeight(40)
        btn_prev.clicked.connect(self.prev_period)

        btn_next = QPushButton("Suivant ▶")
        btn_next.setFixedHeight(40)
        btn_next.clicked.connect(self.next_period)

        for b in (btn_prev, btn_next):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                """
                QPushButton {
                    background: #F3F4F6;
                    border-radius: 8px;
                    border: 1px solid #E5E7EB;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background: #3498db;
                    color: white;
                    border-color: #3498db;
                }
            """
            )

        row3.addWidget(period_label)
        row3.addWidget(self.period_combo, 1)
        row3.addSpacing(20)
        row3.addWidget(self.current_period_label)
        row3.addStretch()
        row3.addWidget(btn_prev)
        row3.addWidget(btn_next)

        filters_layout.addLayout(row3)

        # Ligne 4 : boutons d'export
        row4 = QHBoxLayout()
        row4.addStretch()

        self.btn_export_pdf = QPushButton("📄 Export PDF")
        self.btn_export_pdf.setFixedHeight(45)
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_pdf.setStyleSheet(self.get_export_button_style("#e74c3c"))

        self.btn_export_excel = QPushButton("📊 Export Excel")
        self.btn_export_excel.setFixedHeight(45)
        self.btn_export_excel.setCursor(Qt.PointingHandCursor)
        self.btn_export_excel.clicked.connect(self.export_excel)
        self.btn_export_excel.setStyleSheet(self.get_export_button_style("#27ae60"))

        self.btn_export_ical = QPushButton("📆 Export iCal")
        self.btn_export_ical.setFixedHeight(45)
        self.btn_export_ical.setCursor(Qt.PointingHandCursor)
        self.btn_export_ical.clicked.connect(self.export_ical)
        self.btn_export_ical.setStyleSheet(self.get_export_button_style("#9b59b6"))

        self.btn_export_csv = QPushButton("📋 Export CSV")
        self.btn_export_csv.setFixedHeight(45)
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_csv.setStyleSheet(self.get_export_button_style("#3498db"))

        row4.addWidget(self.btn_export_pdf)
        row4.addWidget(self.btn_export_excel)
        row4.addWidget(self.btn_export_ical)
        row4.addWidget(self.btn_export_csv)

        filters_layout.addLayout(row4)

        layout.addWidget(filters_frame)

        # ==========================================
        # TABLEAU CALENDRIER
        # ==========================================
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        )
        self.table.setRowCount(12)
        # Heures 8h–19h
        for i in range(12):
            hour = 8 + i
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(f"{hour}h"))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(self.table.NoSelection)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background: white;
                border-radius: 12px;
                border: 2px solid #E5E7EB;
                gridline-color: #E5E7EB;
            }
            QHeaderView::section {
                background: #F5F5F5;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }
            QTableWidget::item {
                padding: 8px;
                border: 1px solid #E5E7EB;
            }
        """
        )

        layout.addWidget(self.table)

        # Message info si vide
        self.empty_label = QLabel("")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(
            """
            font-size: 16px;
            color: #9CA3AF;
            margin-top: 20px;
            padding: 40px;
            background: #F9FAFB;
            border-radius: 8px;
            """
        )
        layout.addWidget(self.empty_label)

        # ==========================================
        # 🔧 DÉBLOQUER LES SIGNAUX APRÈS INITIALISATION
        # ==========================================
        self.role_combo.blockSignals(False)
        self.view_type_combo.blockSignals(False)
        self.target_combo.blockSignals(False)
        self.period_combo.blockSignals(False)
        
        # MAINTENANT connecter les signaux
        self.role_combo.currentTextChanged.connect(self.on_filter_changed)
        self.view_type_combo.currentTextChanged.connect(self.on_filter_changed)
        self.target_combo.currentTextChanged.connect(self.on_filter_changed)
        self.period_combo.currentTextChanged.connect(self.on_filter_changed)

        # Chargement initial
        self.refresh_timetable()

    # ==============================
    # STATISTIQUES
    # ==============================

    def create_stat_box(self, label, value, color):
        """Crée une boîte de statistique."""
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

    def update_statistics(self, displayed_count):
        """Mettre à jour les statistiques."""
        # Créneaux affichés
        self.update_stat_box(self.stat_creneaux, str(displayed_count))
        
        # Heures totales (2h par créneau en moyenne)
        total_heures = displayed_count * 2
        self.update_stat_box(self.stat_heures, f"{total_heures}h")
        
        # Jours ouvrés (nombre de colonnes avec au moins un créneau)
        jours = set()
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    jours.add(col)
        self.update_stat_box(self.stat_jours, str(len(jours)))
        
        # Charge moyenne (créneaux / jours * 100 / 12 heures)
        if len(jours) > 0:
            charge = (displayed_count / len(jours) / 12) * 100
            self.update_stat_box(self.stat_charge, f"{charge:.0f}%")
        else:
            self.update_stat_box(self.stat_charge, "0%")

    # ==============================
    # STYLES
    # ==============================

    def get_combo_style(self):
        """Style des combobox."""
        return """
            QComboBox {
                padding: 10px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
        """

    def get_export_button_style(self, color):
        """Style des boutons d'export."""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """

    # ==============================
    # Période
    # ==============================

    def _format_current_period(self) -> str:
        period = self.period_combo.currentText() if hasattr(self, "period_combo") else "Semaine"
        if period == "Semaine":
            week = self.current_date.weekNumber()[0]
            year = self.current_date.year()
            return f"Semaine {week} - {year}"
        if period == "Mois":
            return self.current_date.toString("MMMM yyyy")
        if period == "Semestre":
            month = self.current_date.month()
            sem = 1 if month <= 6 else 2
            return f"Semestre {sem} - {self.current_date.year()}"
        return ""

    def prev_period(self):
        period = self.period_combo.currentText()
        if period == "Semaine":
            self.current_date = self.current_date.addDays(-7)
        elif period == "Mois":
            self.current_date = self.current_date.addMonths(-1)
        else:  # Semestre
            self.current_date = self.current_date.addMonths(-6)
        self.current_period_label.setText(self._format_current_period())
        self.refresh_timetable()

    def next_period(self):
        period = self.period_combo.currentText()
        if period == "Semaine":
            self.current_date = self.current_date.addDays(7)
        elif period == "Mois":
            self.current_date = self.current_date.addMonths(1)
        else:  # Semestre
            self.current_date = self.current_date.addMonths(6)
        self.current_period_label.setText(self._format_current_period())
        self.refresh_timetable()

    # ==============================
    # Données exemple
    # ==============================

    def _build_sample_slots(self):
        """Construit quelques créneaux d'exemple pour la démo."""
        base_date = QDate.currentDate()
        monday = base_date.addDays(-(base_date.dayOfWeek() - 1))

        def d(offset):
            return monday.addDays(offset)

        return [
            {
                "role": "Enseignant",
                "target": "KABORE Marie",
                "type_vue": "Personnelle",
                "start": d(0),
                "day_index": 0,
                "start_hour": 8,
                "duration_h": 2,
                "label": "Algorithmique avancée (CM)\nSalle A101",
                "color": "#DBEAFE",
            },
            {
                "role": "Enseignant",
                "target": "KABORE Marie",
                "type_vue": "Personnelle",
                "start": d(2),
                "day_index": 2,
                "start_hour": 10,
                "duration_h": 2,
                "label": "Bases de données (TD)\nSalle B201",
                "color": "#DCFCE7",
            },
            {
                "role": "Étudiant",
                "target": "L3 Info 2025-2026",
                "type_vue": "Classe",
                "start": d(1),
                "day_index": 1,
                "start_hour": 9,
                "duration_h": 3,
                "label": "Réseaux informatiques (CM)\nSalle A102",
                "color": "#FEF9C3",
            },
            {
                "role": "Étudiant",
                "target": "L3 Info 2025-2026",
                "type_vue": "Classe",
                "start": d(4),
                "day_index": 4,
                "start_hour": 14,
                "duration_h": 2,
                "label": "TP Bases de données\nSalle Labo 1",
                "color": "#FCE7F3",
            },
        ]

    def _load_real_slots(self):
        """Charge les emplois du temps générés par l'onglet Ordonnancement."""
        data_file = Path("data/schedules.json")
        if not data_file.exists():
            return

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        raw_slots = data.get("slots", [])

        for raw in raw_slots:
            try:
                date_q = QDate.fromString(raw.get("date", ""), "yyyy-MM-dd")
                if not date_q.isValid():
                    continue

                day_index = max(0, min(5, date_q.dayOfWeek() - 1))
                self.slots.append(
                    {
                        "role": raw.get("role", "Étudiant"),
                        "target": raw.get("target", ""),
                        "type_vue": raw.get("type_vue", "Classe"),
                        "start": date_q,
                        "day_index": day_index,
                        "start_hour": int(raw.get("start_hour", 8)),
                        "duration_h": int(raw.get("duration_h", 2)),
                        "label": raw.get("label", ""),
                        "color": raw.get("color", "#E5E7EB"),
                    }
                )
            except Exception:
                continue

    # ==============================
    # Rafraîchissement calendrier
    # ==============================

    def on_filter_changed(self):
        """Réagit au changement de filtres (rôle / type de vue)."""
        try:
            # Bloquer temporairement les signaux pour éviter les boucles
            self.target_combo.blockSignals(True)
            
            # Adapter le label selon le rôle et la vue
            role = self.role_combo.currentText()
            vue = self.view_type_combo.currentText()

            if role == "Enseignant":
                self.target_label.setText("🎯 Enseignant :")
                current_text = self.target_combo.currentText() if self.target_combo.count() > 0 else ""
                if self.target_combo.count() == 0 or "L3 Info" in current_text or "Parcours" in current_text:
                    self.target_combo.clear()
                    self.target_combo.addItems(
                        ["KABORE Marie", "TRAORE Moussa", "SAWADOGO Fatimata", "OUATTARA Ibrahim"]
                    )
            else:
                if vue == "Classe":
                    self.target_label.setText("🎯 Classe :")
                    self.target_combo.clear()
                    self.target_combo.addItems(["L3 Info 2025-2026", "M1 Info 2025-2026"])
                else:
                    self.target_label.setText("🎯 Étudiant / Parcours :")
                    self.target_combo.clear()
                    self.target_combo.addItems(
                        ["Parcours Info L3 - Groupe 1", "Parcours Info L3 - Groupe 2"]
                    )
            
            # Débloquer les signaux
            self.target_combo.blockSignals(False)

            self.refresh_timetable()
            
        except Exception as e:
            # Débloquer en cas d'erreur
            self.target_combo.blockSignals(False)
            # Empêcher la fermeture brutale de l'application et afficher l'erreur
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Erreur dans les filtres",
                f"Une erreur est survenue lors du changement de filtres :\n\n{e}"
            )

    def clear_table(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                self.table.setItem(r, c, QTableWidgetItem(""))

    def refresh_timetable(self):
        """Met à jour l'affichage en fonction des filtres."""
        try:
            self.clear_table()
            role = self.role_combo.currentText()
            vue = self.view_type_combo.currentText()
            target = self.target_combo.currentText()
            period = self.period_combo.currentText()

            # Déterminer la plage de dates
            base = self.current_date
            if period == "Semaine":
                start_period = base.addDays(-(base.dayOfWeek() - 1))
                end_period = start_period.addDays(6)
            elif period == "Mois":
                start_period = QDate(base.year(), base.month(), 1)
                end_period = start_period.addMonths(1).addDays(-1)
            else:  # Semestre
                if base.month() <= 6:
                    start_period = QDate(base.year(), 1, 1)
                    end_period = QDate(base.year(), 6, 30)
                else:
                    start_period = QDate(base.year(), 7, 1)
                    end_period = QDate(base.year(), 12, 31)

            # Filtrer les créneaux
            displayed = 0
            for slot in self.slots:
                if slot["role"] != role:
                    continue
                if slot["type_vue"] != vue:
                    continue
                if slot["target"] != target:
                    continue
                date = slot["start"]
                if not (start_period <= date <= end_period):
                    continue

                col = slot["day_index"]
                row = slot["start_hour"] - 8
                if not (0 <= row < self.table.rowCount()):
                    continue

                item = QTableWidgetItem(slot["label"])
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                item.setBackground(QColor(slot["color"]))
                # Style du texte dans les cellules
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.table.setItem(row, col, item)
                displayed += 1

            # Mettre à jour les statistiques
            self.update_statistics(displayed)

            if displayed == 0:
                msg = (
                    "📭 Aucun emploi du temps disponible pour cette combinaison\n"
                    f"({role} - {vue} - {target})\n\n"
                    "Essayez de changer les filtres ou la période."
                )
                self.empty_label.setText(msg)
                self.empty_label.setVisible(True)
            else:
                self.empty_label.setText("")
                self.empty_label.setVisible(False)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.empty_label.setText(f"⚠️ Erreur lors du chargement:\n{str(e)}")
            self.empty_label.setVisible(True)

    # ==============================
    # Récupération des créneaux affichés
    # ==============================

    def _get_displayed_slots(self):
        """Retourne la liste des créneaux effectivement affichés."""
        slots = []
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    day_label = self.table.horizontalHeaderItem(col).text()
                    hour_label = self.table.verticalHeaderItem(row).text()
                    slots.append(
                        {
                            "day": day_label,
                            "hour": hour_label,
                            "text": item.text(),
                        }
                    )
        return slots

    def _ensure_output_dir(self) -> Path:
        out_dir = Path("outputs/timetables")
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    # ==============================
    # Export CSV
    # ==============================

    def export_csv(self):
        if self.empty_label.isVisible():
            QMessageBox.information(
                self,
                "Export CSV",
                "❌ Aucun créneau à exporter pour la sélection courante.",
            )
            return

        slots = self._get_displayed_slots()
        out_dir = self._ensure_output_dir()

        role = self.role_combo.currentText()
        target = self.target_combo.currentText()
        period_label = self._format_current_period().replace(" ", "_")
        filename = out_dir / f"{role}_{target}_{period_label}.csv".replace(" ", "_")

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Jour", "Heure", "Description"])
                for s in slots:
                    writer.writerow([s["day"], s["hour"], s["text"].replace("\n", " / ")])
        except Exception as e:
            QMessageBox.critical(self, "Export CSV", f"❌ Erreur lors de l'export CSV :\n\n{e}")
            return

        QMessageBox.information(
            self,
            "Export CSV",
            f"✅ L'emploi du temps a été exporté en CSV !\n\nFichier : {filename}",
        )

    # ==============================
    # Export iCal (.ics)
    # ==============================

    def export_ical(self):
        if self.empty_label.isVisible():
            QMessageBox.information(
                self,
                "Export iCal",
                "❌ Aucun créneau à exporter pour la sélection courante.",
            )
            return

        slots = self._get_displayed_slots()
        out_dir = self._ensure_output_dir()

        role = self.role_combo.currentText()
        target = self.target_combo.currentText()
        period_label = self._format_current_period().replace(" ", "_")
        filename = out_dir / f"{role}_{target}_{period_label}.ics".replace(" ", "_")

        base = self.current_date
        monday = base.addDays(-(base.dayOfWeek() - 1))
        day_map = {
            "Lundi": 0,
            "Mardi": 1,
            "Mercredi": 2,
            "Jeudi": 3,
            "Vendredi": 4,
            "Samedi": 5,
        }

        def parse_hour(label: str) -> int:
            try:
                return int(label.replace("h", "").strip())
            except Exception:
                return 8

        now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("BEGIN:VCALENDAR\n")
                f.write("VERSION:2.0\n")
                f.write("PRODID:-//Academic Scheduler//UC6//FR\n")

                for idx, s in enumerate(slots):
                    day_offset = day_map.get(s["day"], 0)
                    date = monday.addDays(day_offset).toPyDate()
                    hour = parse_hour(s["hour"])
                    start_dt = datetime(date.year, date.month, date.day, hour, 0)
                    end_dt = start_dt + timedelta(hours=2)

                    f.write("BEGIN:VEVENT\n")
                    f.write(f"UID:uc6-{idx}-{now_str}\n")
                    f.write(f"DTSTAMP:{now_str}\n")
                    f.write(f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\n")
                    f.write(f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\n")
                    summary = s["text"].split("\n")[0]
                    f.write(f"SUMMARY:{summary}\n")
                    f.write("END:VEVENT\n")

                f.write("END:VCALENDAR\n")
        except Exception as e:
            QMessageBox.critical(self, "Export iCal", f"❌ Erreur lors de l'export iCal :\n\n{e}")
            return

        QMessageBox.information(
            self,
            "Export iCal",
            f"✅ L'emploi du temps a été exporté au format iCal !\n\nFichier : {filename}",
        )

    # ==============================
    # Export Excel (.xlsx)
    # ==============================

    def export_excel(self):
        if self.empty_label.isVisible():
            QMessageBox.information(
                self,
                "Export Excel",
                "❌ Aucun créneau à exporter pour la sélection courante.",
            )
            return

        slots = self._get_displayed_slots()
        out_dir = self._ensure_output_dir()

        role = self.role_combo.currentText()
        target = self.target_combo.currentText()
        period_label = self._format_current_period().replace(" ", "_")
        filename = out_dir / f"{role}_{target}_{period_label}.xlsx".replace(" ", "_")

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Emploi du temps"
            ws.append(["Jour", "Heure", "Description"])
            for s in slots:
                ws.append([s["day"], s["hour"], s["text"].replace("\n", " / ")])
            wb.save(filename)
        except Exception as e:
            QMessageBox.critical(self, "Export Excel", f"❌ Erreur lors de l'export Excel :\n\n{e}")
            return

        QMessageBox.information(
            self,
            "Export Excel",
            f"✅ L'emploi du temps a été exporté en Excel !\n\nFichier : {filename}",
        )

    # ==============================
    # Export PDF
    # ==============================

    def export_pdf(self):
        if self.empty_label.isVisible():
            QMessageBox.information(
                self,
                "Export PDF",
                "❌ Aucun créneau à exporter pour la sélection courante.",
            )
            return

        slots = self._get_displayed_slots()
        out_dir = self._ensure_output_dir()

        role = self.role_combo.currentText()
        target = self.target_combo.currentText()
        period_label = self._format_current_period().replace(" ", "_")
        filename = out_dir / f"{role}_{target}_{period_label}.pdf".replace(" ", "_")

        try:
            doc = SimpleDocTemplate(str(filename), pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            title = Paragraph("📅 Emploi du temps", styles["Title"])
            subtitle = Paragraph(
                f"{role} – {target} – {self._format_current_period()}", styles["Normal"]
            )

            elements.append(title)
            elements.append(Spacer(1, 12))
            elements.append(subtitle)
            elements.append(Spacer(1, 24))

            data = [["Jour", "Heure", "Description"]]
            for s in slots:
                data.append(
                    [
                        s["day"],
                        s["hour"],
                        s["text"].replace("\n", " / "),
                    ]
                )

            table = Table(data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ]
                )
            )

            elements.append(table)
            doc.build(elements)
        except Exception as e:
            QMessageBox.critical(self, "Export PDF", f"❌ Erreur lors de l'export PDF :\n\n{e}")
            return

        QMessageBox.information(
            self,
            "Export PDF",
            f"✅ L'emploi du temps a été exporté en PDF !\n\nFichier : {filename}",
        )
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
