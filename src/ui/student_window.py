"""
Fenetre Etudiant — UC6 (Emploi du temps) + UC7 (Retards academiques)
Acces lecture seule + Telechargement PDF/CSV
"""
import csv
from datetime import date, datetime, timedelta
from datetime import time as dtime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QStackedWidget,
    QPushButton, QLabel, QComboBox, QFrame, QScrollArea,
    QGridLayout, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.database.db_manager import db_manager
from src.database.models import ScheduleSlotModel, AcademicActivityModel


# ── Constantes ────────────────────────────────────────────────────────────────
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
HEURE_DEBUT = 8
HEURE_FIN   = 19
SLOT_H      = 65

TYPE_COLORS = {
    "CM":              ("#BBDEFB", "#1565C0"),
    "COURS_MAGISTRAL": ("#BBDEFB", "#1565C0"),
    "TD":              ("#C8E6C9", "#2E7D32"),
    "TP":              ("#FFE0B2", "#E65100"),
    "Examen":          ("#FCE4EC", "#880E4F"),
    "EXAMEN":          ("#FCE4EC", "#880E4F"),
    "Soutenance":      ("#E1BEE7", "#6A1B9A"),
}

def _alpha_color(alpha):
    if alpha is None: return "#9E9E9E"
    if alpha >= 1.0:  return "#C62828"
    if alpha >= 0.5:  return "#F9A825"
    return "#2E7D32"

def _type_str(t):
    if t is None: return ""
    if hasattr(t, 'value'): return t.value
    return str(t).split('.')[-1]


# ═════════════════════════════════════════════════════════════════════════════
# BLOC COURS
# ═════════════════════════════════════════════════════════════════════════════

class CourseBlock(QFrame):
    def __init__(self, slot, parent=None):
        super().__init__(parent)
        act_type = slot.get('activity_type', '')
        bg, fg   = TYPE_COLORS.get(act_type, ("#E0E0E0", "#333"))
        border   = _alpha_color(slot.get('alpha'))

        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid #ccc;
                border-left: 4px solid {border};
                border-radius: 5px;
                margin: 1px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(7, 5, 5, 5)
        lay.setSpacing(2)

        start = slot.get('start', '')
        end   = slot.get('end',   '')
        h_lbl = QLabel(f"⏰ {start} – {end}")
        h_lbl.setStyleSheet(
            f"color:{fg}; font-weight:bold; font-size:11px;"
            f"background:rgba(0,0,0,0.07); border-radius:3px; padding:1px 4px;"
        )
        lay.addWidget(h_lbl)

        name = QLabel(slot.get('activity', '—'))
        name.setStyleSheet(f"color:{fg}; font-weight:bold; font-size:11px;")
        name.setWordWrap(True)
        lay.addWidget(name)

        room = slot.get('room', '')
        info = QLabel(f"📍 {act_type}  |  {room}")
        info.setStyleSheet(f"color:{fg}; font-size:10px;")
        lay.addWidget(info)

        teacher = QLabel(f"👤 {slot.get('teacher','')}")
        teacher.setStyleSheet("color:#444; font-size:10px;")
        lay.addWidget(teacher)

        self.setToolTip(
            f"Activite  : {slot.get('activity','')}\n"
            f"Horaire   : {start} – {end}\n"
            f"Type      : {act_type}\n"
            f"Salle     : {room}\n"
            f"Enseignant: {slot.get('teacher','')}\n"
            f"α (retard): {slot.get('alpha','N/A')}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# GRILLE HEBDOMADAIRE
# ═════════════════════════════════════════════════════════════════════════════

class TimetableGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(0,0,0,0); main.setSpacing(0)

        tc = QWidget(); tc.setFixedWidth(55)
        tcl = QVBoxLayout(tc); tcl.setContentsMargins(0,30,0,0); tcl.setSpacing(0)
        for h in range(HEURE_DEBUT, HEURE_FIN):
            l = QLabel(f"{h:02d}:00"); l.setFixedHeight(SLOT_H)
            l.setStyleSheet("color:#555; font-size:10px;")
            l.setAlignment(Qt.AlignTop | Qt.AlignRight)
            tcl.addWidget(l)
        tcl.addStretch(); main.addWidget(tc)

        self.gw = QWidget()
        self.gl = QGridLayout(self.gw)
        self.gl.setContentsMargins(0,0,0,0); self.gl.setSpacing(2)

        for col, jour in enumerate(JOURS):
            h = QLabel(jour); h.setFixedHeight(28)
            h.setAlignment(Qt.AlignCenter)
            h.setStyleSheet("font-weight:bold; font-size:12px; color:#1a73e8; "
                            "background:#e8f0fe; border-radius:4px;")
            self.gl.addWidget(h, 0, col)

        for row in range(1, HEURE_FIN - HEURE_DEBUT + 1):
            for col in range(len(JOURS)):
                cell = QFrame(); cell.setFixedHeight(SLOT_H)
                cell.setStyleSheet("background:#fafafa; border:1px solid #eee;")
                self.gl.addWidget(cell, row, col)

        self.gw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main.addWidget(self.gw)

    def load_slots(self, slots):
        for i in reversed(range(self.gl.count())):
            item = self.gl.itemAt(i)
            if item and isinstance(item.widget(), CourseBlock):
                item.widget().deleteLater(); self.gl.removeItem(item)

        for slot in slots:
            try:
                d = slot.get('date')
                if isinstance(d, str): d = datetime.fromisoformat(d).date()
                wd = d.weekday()
                if wd > 5: continue
                sh = int(slot.get('start','08:00').split(':')[0])
                eh = int(slot.get('end',  '10:00').split(':')[0])
                if sh < HEURE_DEBUT or eh > HEURE_FIN: continue
                rs = sh - HEURE_DEBUT + 1
                sp = max(1, eh - sh)
                b  = CourseBlock(slot)
                b.setFixedHeight(SLOT_H * sp - 4)
                self.gl.addWidget(b, rs, wd, sp, 1)
            except Exception:
                pass


# ═════════════════════════════════════════════════════════════════════════════
# ONGLET EMPLOI DU TEMPS (UC6)
# ═════════════════════════════════════════════════════════════════════════════


# ═════════════════════════════════════════════════════════════════════════════
# ONGLET EMPLOI DU TEMPS (UC6) — avec sélection cohorte + vue semaine/mois
# ═════════════════════════════════════════════════════════════════════════════

class StudentTimetableTab(QWidget):
    """
    UC6 — Emploi du temps etudiant.
    - Dropdown cohorte : pré-sélectionné sur la cohorte de l'étudiant
    - Toggle Semaine / Mois
    - Navigation ◀ ▶ selon la vue active
    - Export PDF / CSV
    """

    def __init__(self, student, parent=None):
        super().__init__(parent)
        self._student    = student
        self._slots      = []           # tous les créneaux de la cohorte choisie
        self._view_mode  = 'week'       # 'week' ou 'month'
        today            = date.today()
        self._week_start = today - timedelta(days=today.weekday())
        self._month_start= today.replace(day=1)
        self._selected_cohort_id = getattr(student, 'cohort_id', None)
        self._build_ui()
        self._load_cohorts()            # remplit le dropdown et charge les cours

    # ── Construction UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)

        # ── Titre ────────────────────────────────────────────────
        title = QLabel("📅 Emploi du Temps")
        title.setStyleSheet("font-size:20px; font-weight:bold; color:#1a1a1a;")
        lay.addWidget(title)

        # ── Barre de controles ────────────────────────────────────
        ctrl = QHBoxLayout(); ctrl.setSpacing(10)

        # Sélection cohorte
        ctrl.addWidget(QLabel("Cohorte :"))
        self._cohort_combo = QComboBox()
        self._cohort_combo.setFixedHeight(34)
        self._cohort_combo.setMinimumWidth(200)
        self._cohort_combo.setStyleSheet("""
            QComboBox {
                border:1px solid #ddd; border-radius:6px;
                padding:0 10px; font-size:12px; background:#f9f9f9;
            }
            QComboBox:focus { border:2px solid #1a73e8; }
        """)
        self._cohort_combo.currentIndexChanged.connect(self._on_cohort_changed)
        ctrl.addWidget(self._cohort_combo)

        ctrl.addSpacing(16)

        # Toggle vue Semaine / Mois
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet("QFrame{background:#f0f0f0;border-radius:7px;}")
        toggle_lay = QHBoxLayout(toggle_frame)
        toggle_lay.setContentsMargins(3, 3, 3, 3); toggle_lay.setSpacing(2)

        self._btn_week = QPushButton("📅 Semaine")
        self._btn_week.setFixedHeight(28)
        self._btn_week.setCheckable(True)
        self._btn_week.setChecked(True)
        self._btn_week.clicked.connect(lambda: self._set_view('week'))

        self._btn_month = QPushButton("🗓️ Mois")
        self._btn_month.setFixedHeight(28)
        self._btn_month.setCheckable(True)
        self._btn_month.setChecked(False)
        self._btn_month.clicked.connect(lambda: self._set_view('month'))

        for b in (self._btn_week, self._btn_month):
            b.setStyleSheet("""
                QPushButton {
                    background:transparent; border:none; border-radius:5px;
                    font-size:12px; padding:0 12px; color:#555;
                }
                QPushButton:checked {
                    background:white; color:#1a73e8;
                    font-weight:bold;
                    border:1px solid #ddd;
                }
                QPushButton:hover:!checked { background:#e8e8e8; }
            """)
            toggle_lay.addWidget(b)
        ctrl.addWidget(toggle_frame)

        ctrl.addStretch()

        # Exports
        btn_pdf = QPushButton("🖨️ PDF")
        btn_pdf.setFixedHeight(34)
        btn_pdf.setStyleSheet("background:#c62828;color:white;border-radius:6px;padding:0 14px;font-size:12px;")
        btn_pdf.clicked.connect(self._export_pdf)
        ctrl.addWidget(btn_pdf)

        btn_csv = QPushButton("📄 CSV")
        btn_csv.setFixedHeight(34)
        btn_csv.setStyleSheet("background:#5e35b1;color:white;border-radius:6px;padding:0 14px;font-size:12px;")
        btn_csv.clicked.connect(self._export_csv)
        ctrl.addWidget(btn_csv)

        lay.addLayout(ctrl)

        # ── Barre navigation période ──────────────────────────────
        nav = QHBoxLayout(); nav.setSpacing(8)

        self._btn_prev = QPushButton("◀")
        self._btn_prev.setFixedSize(32, 32)
        self._btn_prev.setStyleSheet("background:#f0f0f0;border-radius:6px;font-size:14px;")
        self._btn_prev.clicked.connect(self._prev_period)
        nav.addWidget(self._btn_prev)

        self._period_lbl = QLabel()
        self._period_lbl.setAlignment(Qt.AlignCenter)
        self._period_lbl.setMinimumWidth(200)
        self._period_lbl.setStyleSheet("font-weight:bold;font-size:13px;color:#333;")
        nav.addWidget(self._period_lbl)

        self._btn_next = QPushButton("▶")
        self._btn_next.setFixedSize(32, 32)
        self._btn_next.setStyleSheet("background:#f0f0f0;border-radius:6px;font-size:14px;")
        self._btn_next.clicked.connect(self._next_period)
        nav.addWidget(self._btn_next)

        btn_today = QPushButton("Aujourd'hui")
        btn_today.setFixedHeight(32)
        btn_today.setStyleSheet("background:#1a73e8;color:white;border-radius:6px;padding:0 12px;font-size:12px;")
        btn_today.clicked.connect(self._go_today)
        nav.addWidget(btn_today)

        nav.addStretch()

        # Légende
        for col, lbl in [("#C62828","🔴 Critique"),("#F9A825","🟡 Urgent"),("#2E7D32","🟢 OK")]:
            l = QLabel(lbl)
            l.setStyleSheet(f"border-left:3px solid {col};padding-left:5px;font-size:10px;color:#555;")
            nav.addWidget(l)

        lay.addLayout(nav)

        # ── Zone d'affichage (stack : grille semaine / grille mois) ──
        self._stack = QStackedWidget()

        # Vue semaine
        self._scroll_week = QScrollArea()
        self._scroll_week.setWidgetResizable(True)
        self._scroll_week.setStyleSheet("border:1px solid #ddd;border-radius:8px;")
        self._grid_week = TimetableGrid()
        self._scroll_week.setWidget(self._grid_week)
        self._stack.addWidget(self._scroll_week)

        # Vue mois
        self._month_widget = MonthView()
        self._stack.addWidget(self._month_widget)

        lay.addWidget(self._stack)

        # Message vide
        self._empty_lbl = QLabel("")
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet("color:#888;font-size:13px;padding:10px;")
        self._empty_lbl.setVisible(False)
        lay.addWidget(self._empty_lbl)

        self._update_period_label()

    # ── Chargement des cohortes ───────────────────────────────────────────────

    def _load_cohorts(self):
        """Remplit le dropdown avec toutes les cohortes disponibles."""
        try:
            from src.database.models import CohortModel
            session = db_manager.get_session()
            cohorts = session.query(CohortModel).order_by(CohortModel.name).all()
            self._cohort_combo.blockSignals(True)
            self._cohort_combo.clear()
            selected_idx = 0
            for i, c in enumerate(cohorts):
                label = f"{c.name}  ({c.academic_year} — S{c.semester})"
                self._cohort_combo.addItem(label, userData=c.id)
                if c.id == self._selected_cohort_id:
                    selected_idx = i
            self._cohort_combo.setCurrentIndex(selected_idx)
            self._cohort_combo.blockSignals(False)
            self._on_cohort_changed(selected_idx)
        except Exception as e:
            print(f"[timetable] Erreur chargement cohortes: {e}")

    def _on_cohort_changed(self, idx):
        """Recharge les créneaux quand la cohorte change."""
        cohort_id = self._cohort_combo.itemData(idx)
        if cohort_id is None:
            return
        self._selected_cohort_id = cohort_id
        self._load_slots(cohort_id)

    def _load_slots(self, cohort_id):
        """Charge tous les créneaux de la cohorte depuis la base."""
        try:
            session = db_manager.get_session()
            orm_slots = session.query(ScheduleSlotModel).filter(
                ScheduleSlotModel.cohort_id == cohort_id
            ).all()
            self._slots = []
            for s in orm_slots:
                if not s.date:
                    continue
                act_type  = _type_str(s.activity.type if s.activity else None)
                alpha     = None
                if s.notes and 'alpha=' in s.notes:
                    try: alpha = float(s.notes.split('alpha=')[1].split()[0])
                    except: alpha = s.delay_value
                start_str = s.start_time.strftime('%H:%M') if isinstance(s.start_time, dtime) else str(s.start_time)[:5]
                end_str   = s.end_time.strftime('%H:%M')   if isinstance(s.end_time,   dtime) else str(s.end_time)[:5]
                self._slots.append({
                    'date':          s.date,
                    'start':         start_str,
                    'end':           end_str,
                    'activity':      s.activity.name if s.activity else '?',
                    'activity_type': act_type,
                    'teacher':       s.teacher.full_name if s.teacher else 'Non assigné',
                    'room':          s.room or '—',
                    'alpha':         alpha,
                })
        except Exception as e:
            print(f"[timetable] Erreur chargement créneaux: {e}")
            self._slots = []
        self._refresh()

    # ── Gestion vue ───────────────────────────────────────────────────────────

    def _set_view(self, mode):
        self._view_mode = mode
        self._btn_week.setChecked(mode == 'week')
        self._btn_month.setChecked(mode == 'month')
        self._stack.setCurrentIndex(0 if mode == 'week' else 1)
        self._update_period_label()
        self._refresh()

    def _update_period_label(self):
        if self._view_mode == 'week':
            end = self._week_start + timedelta(days=5)
            self._period_lbl.setText(
                f"{self._week_start.strftime('%d %b')} — {end.strftime('%d %b %Y')}"
            )
        else:
            MOIS = ["","Janvier","Février","Mars","Avril","Mai","Juin",
                    "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
            self._period_lbl.setText(
                f"{MOIS[self._month_start.month]} {self._month_start.year}"
            )

    def _prev_period(self):
        if self._view_mode == 'week':
            self._week_start -= timedelta(weeks=1)
        else:
            m = self._month_start.month - 1
            y = self._month_start.year
            if m == 0: m, y = 12, y - 1
            self._month_start = date(y, m, 1)
        self._update_period_label(); self._refresh()

    def _next_period(self):
        if self._view_mode == 'week':
            self._week_start += timedelta(weeks=1)
        else:
            m = self._month_start.month + 1
            y = self._month_start.year
            if m == 13: m, y = 1, y + 1
            self._month_start = date(y, m, 1)
        self._update_period_label(); self._refresh()

    def _go_today(self):
        today = date.today()
        self._week_start  = today - timedelta(days=today.weekday())
        self._month_start = today.replace(day=1)
        self._update_period_label(); self._refresh()

    # ── Affichage ─────────────────────────────────────────────────────────────

    def _refresh(self):
        if self._view_mode == 'week':
            week_end   = self._week_start + timedelta(days=6)
            visible    = [s for s in self._slots
                          if self._date(s) and self._week_start <= self._date(s) <= week_end]
            self._grid_week.load_slots(visible)
            self._show_empty_msg(visible)
        else:
            # Vue mois
            import calendar
            last_day   = calendar.monthrange(self._month_start.year, self._month_start.month)[1]
            month_end  = date(self._month_start.year, self._month_start.month, last_day)
            visible    = [s for s in self._slots
                          if self._date(s) and self._month_start <= self._date(s) <= month_end]
            self._month_widget.load(self._month_start, visible)
            self._show_empty_msg(visible)

    def _date(self, slot):
        d = slot.get('date')
        if isinstance(d, str):
            try: return datetime.fromisoformat(d).date()
            except: return None
        return d

    def _show_empty_msg(self, visible):
        total = len(self._slots)
        has   = len(visible) > 0
        if total == 0:
            self._empty_lbl.setText(
                "Aucun cours planifié pour cette cohorte.\n"
                "L'ordonnancement n'a pas encore été lancé."
            )
        elif not has:
            period = "cette semaine" if self._view_mode == 'week' else "ce mois"
            self._empty_lbl.setText(
                f"Aucun cours {period}. ({total} cours au total)\n"
                "Naviguez avec ◀ ▶ ou cliquez sur Aujourd'hui."
            )
        self._empty_lbl.setVisible(not has)

    # ── Exports ───────────────────────────────────────────────────────────────

    def _export_pdf(self):
        sid = getattr(self._student, 'student_id', 'etudiant')
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF",
                    f"emploi_du_temps_{sid}.pdf", "PDF (*.pdf)")
        if not path: return
        try:
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            doc  = SimpleDocTemplate(path, pagesize=landscape(A4))
            styl = getSampleStyleSheet()
            cohort_label = self._cohort_combo.currentText()
            elems = [
                Paragraph(f"Emploi du temps — {self._student.full_name}", styl['Title']),
                Paragraph(f"Cohorte : {cohort_label}", styl['Normal']),
                Spacer(1, 12),
            ]
            rows = [["Date","Début","Fin","Activité","Type","Salle","Enseignant"]]
            for s in sorted(self._slots, key=lambda x: (str(x.get('date','')), x.get('start',''))):
                rows.append([str(s.get('date','')), s.get('start',''), s.get('end',''),
                             s.get('activity',''), s.get('activity_type',''),
                             s.get('room',''), s.get('teacher','')])
            t = Table(rows)
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a73e8')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f5f5')]),
                ('FONTSIZE',(0,0),(-1,-1),8),
            ]))
            elems.append(t)
            doc.build(elems)
            QMessageBox.information(self, "Export OK", f"PDF enregistré :\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Dépendance", "pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _export_csv(self):
        sid = getattr(self._student, 'student_id', 'etudiant')
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV",
                    f"emploi_du_temps_{sid}.csv", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["Date","Début","Fin","Activité","Type","Salle","Enseignant"])
                for s in sorted(self._slots, key=lambda x: (str(x.get('date','')), x.get('start',''))):
                    w.writerow([str(s.get('date','')), s.get('start',''), s.get('end',''),
                                s.get('activity',''), s.get('activity_type',''),
                                s.get('room',''), s.get('teacher','')])
            QMessageBox.information(self, "Export OK", f"CSV enregistré :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


# ═════════════════════════════════════════════════════════════════════════════
# VUE MOIS — Calendrier mensuel avec pastilles de cours
# ═════════════════════════════════════════════════════════════════════════════

class MonthView(QWidget):
    """Grille calendrier mensuelle affichant les cours sous forme de pastilles."""

    JOURS_COURTS = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
    MOIS = ["","Janvier","Février","Mars","Avril","Mai","Juin",
            "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setSpacing(4)
        self._grid.setContentsMargins(4, 4, 4, 4)
        self._cells = {}

    def load(self, month_start: date, slots):
        """Affiche le calendrier du mois avec les cours."""
        import calendar
        # Vider la grille
        for i in reversed(range(self._grid.count())):
            w = self._grid.itemAt(i).widget()
            if w: w.deleteLater()
        self._cells = {}

        # En-têtes jours
        for col, j in enumerate(self.JOURS_COURTS):
            lbl = QLabel(j)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(28)
            lbl.setStyleSheet("font-weight:bold;font-size:11px;color:#1a73e8;"
                              "background:#e8f0fe;border-radius:4px;")
            self._grid.addWidget(lbl, 0, col)

        # Construire les jours du mois
        last_day = calendar.monthrange(month_start.year, month_start.month)[1]
        first_wd = month_start.weekday()  # 0=Lundi

        # Index slots par date
        slots_by_date = {}
        for s in slots:
            d = s.get('date')
            if isinstance(d, str):
                try: d = datetime.fromisoformat(d).date()
                except: continue
            if d:
                slots_by_date.setdefault(d, []).append(s)

        today = date.today()
        cell  = first_wd
        for day in range(1, last_day + 1):
            row = cell // 7 + 1
            col = cell % 7
            cur = date(month_start.year, month_start.month, day)

            frame = QFrame()
            frame.setMinimumHeight(80)
            is_today = (cur == today)
            bg = "#e3f2fd" if is_today else "white"
            border = "#1a73e8" if is_today else "#e0e0e0"
            frame.setStyleSheet(f"QFrame{{background:{bg};border:1px solid {border};border-radius:6px;}}")

            fl = QVBoxLayout(frame)
            fl.setContentsMargins(4, 4, 4, 4)
            fl.setSpacing(2)

            # Numéro du jour
            day_lbl = QLabel(str(day))
            day_lbl.setStyleSheet(
                f"font-weight:bold;font-size:12px;color:{'#1a73e8' if is_today else '#333'};"
            )
            fl.addWidget(day_lbl)

            # Pastilles de cours
            day_slots = slots_by_date.get(cur, [])
            for s in day_slots[:3]:  # max 3 visibles
                act_type = s.get('activity_type','')
                bg_c, fg_c = TYPE_COLORS.get(act_type, ("#e0e0e0","#333"))
                pill = QLabel(f"  {s.get('start','')} {s.get('activity','')[:18]}")
                pill.setStyleSheet(f"""
                    QLabel {{
                        background:{bg_c}; color:{fg_c};
                        border-radius:3px; font-size:9px;
                        padding:1px 3px;
                    }}
                """)
                pill.setToolTip(
                    f"{s.get('activity','')} | {s.get('start','')}–{s.get('end','')}\n"
                    f"{s.get('activity_type','')} | {s.get('room','')}\n"
                    f"👤 {s.get('teacher','')}"
                )
                fl.addWidget(pill)

            if len(day_slots) > 3:
                more = QLabel(f"+{len(day_slots)-3} autres")
                more.setStyleSheet("color:#888;font-size:9px;")
                fl.addWidget(more)

            fl.addStretch()
            self._grid.addWidget(frame, row, col)
            cell += 1

        # Remplir les cases vides avant le 1er
        for c in range(first_wd):
            empty = QFrame()
            empty.setStyleSheet("background:#f9f9f9;border:1px solid #f0f0f0;border-radius:6px;")
            self._grid.addWidget(empty, 1, c)

class StudentDelaysTab(QWidget):
    def __init__(self, student, parent=None):
        super().__init__(parent)
        self._student = student
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16,16,16,16); lay.setSpacing(12)

        title = QLabel("📊 Mes Retards Académiques (α de Pfair)")
        title.setStyleSheet("font-size:20px; font-weight:bold; color:#1a1a1a;")
        lay.addWidget(title)

        info = QLabel(
            "L'indicateur α mesure l'écart entre l'avancement idéal et réel de chaque cours.\n"
            "α < 0.5 = OK ✅  |  0.5 ≤ α < 1 = Urgent 🟡  |  α ≥ 1 = Critique 🔴"
        )
        info.setStyleSheet("color:#555; font-size:12px; background:#f5f5f5; "
                           "padding:8px; border-radius:6px;")
        info.setWordWrap(True)
        lay.addWidget(info)

        # Barre de résumé
        self._summary = QLabel()
        self._summary.setStyleSheet("font-size:13px; padding:6px;")
        lay.addWidget(self._summary)

        # Barre progression globale
        prog_row = QHBoxLayout()
        prog_row.addWidget(QLabel("Progression globale :"))
        self._prog_bar = QProgressBar()
        self._prog_bar.setFixedHeight(18)
        self._prog_bar.setStyleSheet("""
            QProgressBar { border:1px solid #ccc; border-radius:6px; background:#eee; }
            QProgressBar::chunk { background:#4caf50; border-radius:6px; }
        """)
        prog_row.addWidget(self._prog_bar)
        self._prog_lbl = QLabel("0%")
        self._prog_lbl.setFixedWidth(40)
        prog_row.addWidget(self._prog_lbl)
        lay.addLayout(prog_row)

        # Tableau
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels([
            "Activité", "Code", "Type",
            "Volume total (h)", "Réalisé (h)", "Restant (h)", "α (retard)"
        ])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1,7):
            self._table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget { border:1px solid #ddd; border-radius:6px; font-size:12px; }
            QHeaderView::section { background:#f0f0f0; font-weight:bold; padding:6px; border:none; }
        """)
        lay.addWidget(self._table)

    def _load_data(self):
        try:
            session = db_manager.get_session()
            activities = session.query(AcademicActivityModel).filter_by(
                cohort_id=self._student.cohort_id
            ).all()

            total_vol  = sum(float(a.volume_hours or 0) for a in activities)
            total_done = sum(float(a.hours_done or 0) for a in activities)
            progression = int((total_done / total_vol * 100) if total_vol > 0 else 0)

            self._prog_bar.setValue(progression)
            self._prog_lbl.setText(f"{progression}%")

            critiques = sum(1 for a in activities
                            if a.volume_hours and a.hours_done is not None
                            and (a.volume_hours - (a.hours_done or 0)) / max(a.volume_hours,1) >= 1.0)

            self._summary.setText(
                f"📚 {len(activities)} activité(s)  |  "
                f"⏱️ {total_done:.0f}h réalisées / {total_vol:.0f}h au total  |  "
                f"🔴 {critiques} critique(s)"
            )

            self._table.setRowCount(len(activities))
            for row, act in enumerate(activities):
                vol   = float(act.volume_hours or 0)
                done  = float(act.hours_done or 0)
                rest  = max(0.0, vol - done)
                # Calcul alpha simplifié : retard relatif
                alpha = rest / vol if vol > 0 else 0.0

                act_type = _type_str(act.type)

                vals = [
                    act.name, act.code, act_type,
                    f"{vol:.0f}", f"{done:.0f}", f"{rest:.0f}",
                    f"{alpha:.3f}"
                ]
                for col, v in enumerate(vals):
                    item = QTableWidgetItem(str(v))
                    item.setTextAlignment(Qt.AlignCenter if col > 0 else Qt.AlignLeft | Qt.AlignVCenter)
                    # Colorier la cellule α
                    if col == 6:
                        if alpha >= 1.0:
                            item.setBackground(QColor("#FFCDD2"))
                            item.setForeground(QColor("#C62828"))
                        elif alpha >= 0.5:
                            item.setBackground(QColor("#FFF9C4"))
                            item.setForeground(QColor("#F57F17"))
                        else:
                            item.setBackground(QColor("#C8E6C9"))
                            item.setForeground(QColor("#2E7D32"))
                    self._table.setItem(row, col, item)

        except Exception as e:
            print(f"[student_delays] Erreur: {e}")
            self._summary.setText(f"⚠️ Erreur de chargement : {e}")


# ═════════════════════════════════════════════════════════════════════════════
# FENETRE PRINCIPALE ETUDIANT
# ═════════════════════════════════════════════════════════════════════════════

class StudentWindow(QMainWindow):
    """Fenetre principale pour un etudiant connecte."""

    def __init__(self, student, parent=None):
        super().__init__(parent)
        self._student = student
        self._init_ui()

    def _init_ui(self):
        cohort_name = getattr(self._student.cohort, 'name', '') if self._student.cohort else ''
        self.setWindowTitle(f"Espace Etudiant — {self._student.full_name} ({cohort_name})")
        self.setMinimumSize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        # ── En-tete ───────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background:#1a237e;")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16,0,16,0)

        title = QLabel(f"🎓 Espace Etudiant  —  {self._student.full_name}")
        title.setStyleSheet("color:white; font-size:15px; font-weight:bold;")
        h_lay.addWidget(title)
        h_lay.addStretch()

        cohort_lbl = QLabel(f"Cohorte : {cohort_name}  |  Matricule : {self._student.student_id}")
        cohort_lbl.setStyleSheet("color:#90caf9; font-size:11px;")
        h_lay.addWidget(cohort_lbl)

        btn_logout = QPushButton("🚪 Déconnexion")
        btn_logout.setFixedHeight(30)
        btn_logout.setStyleSheet(
            "background:#ef5350; color:white; border-radius:5px; padding:0 10px; font-size:12px;"
        )
        btn_logout.clicked.connect(self.close)
        h_lay.addWidget(btn_logout)

        main_lay.addWidget(header)

        # ── Onglets ───────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab { padding:10px 20px; font-size:13px; }
            QTabBar::tab:selected { font-weight:bold; border-bottom:3px solid #1a73e8; }
        """)

        tabs.addTab(
            StudentTimetableTab(self._student),
            "📅  Mon Emploi du Temps"
        )
        tabs.addTab(
            StudentDelaysTab(self._student),
            "📊  Mes Retards Académiques"
        )

        main_lay.addWidget(tabs)