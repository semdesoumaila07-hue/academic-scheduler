"""
Onglet Calendrier Académique — UC5 — 100% SQLite

CORRECTION : calcul_d_effectif() ne gérait pas les jours fériés récurrents.
Un férié marqué is_recurring=True doit être exclu chaque année au même jour/mois,
pas seulement à sa date exacte. Sans ce fix, le dashboard affichait un D_effectif
supérieur à celui calculé par le Pfair Scheduler (ex: 225 vs 236).
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QFrame, QTabWidget,
    QDialog, QFormLayout, QLineEdit, QDateEdit, QSpinBox,
    QComboBox, QMessageBox, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from datetime import datetime, date

from src.database.db_manager import db_manager
from src.database.models import (
    AcademicCalendarModel, HolidayModel, VacationPeriodModel,
    UniversityModel, VacationTypeEnum
)


class CalendarTab(QWidget):
    """Onglet calendrier académique — UC5 — 100% SQLite."""

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.session = db_manager.get_session()
        self.calendars   = []
        self.holidays    = []
        self.vacations   = []
        self.universites = []
        self.load_data()
        self.init_ui()

    # ══════════════════════════════════════════════════════════
    # CHARGEMENT SQLITE
    # ══════════════════════════════════════════════════════════

    def load_data(self):
        try:
            self.universites = self.session.query(UniversityModel).all()
            self.calendars   = self.session.query(AcademicCalendarModel).all()
            self.holidays    = self.session.query(HolidayModel).all()
            self.vacations   = self.session.query(VacationPeriodModel).all()
        except Exception as e:
            print(f"Erreur chargement calendrier: {e}")

    # ══════════════════════════════════════════════════════════
    # ACTIONS — Calendriers
    # ══════════════════════════════════════════════════════════

    def add_calendar(self):
        univ_names = [u.name for u in self.universites]
        dialog = CalendarDialog(self, universites=univ_names)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            try:
                cal = AcademicCalendarModel(
                    name=d['name'],
                    academic_year=d['academic_year'],
                    start_date=d['start_date'],
                    end_date=d['end_date'],
                    hours_per_day=d.get('hours_per_day', 8),
                    semester_count=d.get('semester_count', 2),
                )
                self.session.add(cal)
                self.session.commit()
                self.load_data()
                self.refresh_calendars_table()
                self.update_stats()
                QMessageBox.information(self, "Succès", f"✅ Calendrier '{cal.name}' créé !")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    def delete_calendar(self, row):
        if row < 0 or row >= len(self.calendars):
            return
        cal = self.calendars[row]
        if QMessageBox.question(self, "Confirmation",
                f"Supprimer le calendrier '{cal.name}' ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.session.delete(cal)
                self.session.commit()
                self.load_data()
                self.refresh_calendars_table()
                self.update_stats()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    # ══════════════════════════════════════════════════════════
    # ACTIONS — Jours fériés
    # ══════════════════════════════════════════════════════════

    def add_holiday(self):
        if not self.calendars:
            QMessageBox.warning(self, "Attention", "Créez d'abord un calendrier académique.")
            return
        dialog = HolidayDialog(self, calendars=self.calendars)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            try:
                holiday = HolidayModel(
                    name=d['name'],
                    date=d['date'],
                    is_recurring=d.get('is_recurring', False),
                    calendar_id=d['calendar_id'],
                    description=d.get('description', ''),
                )
                self.session.add(holiday)
                self.session.commit()
                self.load_data()
                self.refresh_holidays_table()
                self.update_stats()
                QMessageBox.information(self, "Succès", f"✅ Jour férié '{holiday.name}' ajouté !")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    def delete_holiday(self, row):
        if row < 0 or row >= len(self.holidays):
            return
        h = self.holidays[row]
        if QMessageBox.question(self, "Confirmation",
                f"Supprimer '{h.name}' ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.session.delete(h)
                self.session.commit()
                self.load_data()
                self.refresh_holidays_table()
                self.update_stats()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    # ══════════════════════════════════════════════════════════
    # ACTIONS — Vacances
    # ══════════════════════════════════════════════════════════

    def add_vacation(self):
        if not self.calendars:
            QMessageBox.warning(self, "Attention", "Créez d'abord un calendrier académique.")
            return
        dialog = VacationDialog(self, calendars=self.calendars)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            try:
                vac = VacationPeriodModel(
                    name=d['name'],
                    start_date=d['start_date'],
                    end_date=d['end_date'],
                    type=d['type'],
                    calendar_id=d['calendar_id'],
                    description=d.get('description', ''),
                )
                self.session.add(vac)
                self.session.commit()
                self.load_data()
                self.refresh_vacations_table()
                self.update_stats()
                QMessageBox.information(self, "Succès", f"✅ Vacances '{vac.name}' ajoutées !")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    def delete_vacation(self, row):
        if row < 0 or row >= len(self.vacations):
            return
        v = self.vacations[row]
        if QMessageBox.question(self, "Confirmation",
                f"Supprimer '{v.name}' ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.session.delete(v)
                self.session.commit()
                self.load_data()
                self.refresh_vacations_table()
                self.update_stats()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Erreur", str(e))

    # ══════════════════════════════════════════════════════════
    # CALCUL D_EFFECTIF
    # ══════════════════════════════════════════════════════════

    def calcul_d_effectif(self, calendar: AcademicCalendarModel):
        """
        Calcule le nombre de jours ouvrables effectifs.

        CORRECTION : l'ancienne version ne vérifiait que la date exacte des
        fériés, ignorant les fériés récurrents (is_recurring=True).
        Un férié récurrent s'applique chaque année au même jour/mois.
        Ex : Indépendance le 11/12/2026 (récurrent) → aussi exclu le 11/12/2025
        si cette date est dans la période du calendrier.

        Cette logique est désormais identique à celle de HolidayRepository.is_holiday()
        utilisée par le Pfair Scheduler, garantissant la cohérence des deux valeurs
        affichées dans l'application.
        """
        from datetime import timedelta
        if not calendar.start_date or not calendar.end_date:
            return 0

        vacation_ranges = [
            (v.start_date, v.end_date)
            for v in calendar.vacation_periods
        ]

        jours = 0
        current = calendar.start_date

        while current <= calendar.end_date:
            if current.weekday() < 5:  # Lundi-Vendredi uniquement

                # ── Vérification fériés : exacts ET récurrents ───────────────
                est_ferie = False
                for h in calendar.holidays:
                    # 1. Date exacte (récurrent ou non)
                    if h.date == current:
                        est_ferie = True
                        break
                    # 2. Férié récurrent : même jour/mois, année différente
                    #    ✅ CORRECTION : cette branche était absente avant
                    if (
                        h.is_recurring
                        and h.date.day   == current.day
                        and h.date.month == current.month
                    ):
                        est_ferie = True
                        break
                # ─────────────────────────────────────────────────────────────

                if not est_ferie:
                    en_vacances = any(s <= current <= e for s, e in vacation_ranges)
                    if not en_vacances:
                        jours += 1

            current += timedelta(days=1)

        return jours

    # ══════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Calendrier Académique")
        title.setStyleSheet("font-size:28px; font-weight:bold; color:#1a1a1a;")
        layout.addWidget(title)

        subtitle = QLabel("UC5 — Configuration de l'année académique, jours fériés et vacances")
        subtitle.setStyleSheet("font-size:14px; color:#666;")
        layout.addWidget(subtitle)

        stats_layout = QHBoxLayout()
        self.stat_cal  = self._stat_card("Calendriers",       "0", "#3B82F6")
        self.stat_hol  = self._stat_card("Jours fériés",      "0", "#F59E0B")
        self.stat_vac  = self._stat_card("Périodes vacances",  "0", "#8B5CF6")
        self.stat_deff = self._stat_card("D_effectif (jours)", "—", "#10B981")
        for c in [self.stat_cal, self.stat_hol, self.stat_vac, self.stat_deff]:
            stats_layout.addWidget(c)
        layout.addLayout(stats_layout)
        self.update_stats()

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border:1px solid #E5E7EB; border-radius:8px; background:white; }
            QTabBar::tab { padding:10px 20px; background:#F3F4F6; border-radius:6px 6px 0 0; margin-right:4px; }
            QTabBar::tab:selected { background:white; font-weight:bold; border-bottom:2px solid #3B82F6; }
        """)

        # Tab 1 : Calendriers
        cal_widget = QWidget()
        cal_layout = QVBoxLayout(cal_widget)
        cal_layout.setContentsMargins(16, 16, 16, 16)
        btn_add_cal = QPushButton("➕ Nouveau Calendrier")
        btn_add_cal.setFixedHeight(38)
        btn_add_cal.setStyleSheet("background:#3B82F6; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_add_cal.clicked.connect(self.add_calendar)
        cal_layout.addWidget(btn_add_cal, alignment=Qt.AlignLeft)
        self.table_calendars = self._make_table(["Nom", "Année", "Début", "Fin", "H/jour", "Semestres", "D_effectif", "Actions"])
        cal_layout.addWidget(self.table_calendars)
        tabs.addTab(cal_widget, "📅 Calendriers")

        # Tab 2 : Jours fériés
        hol_widget = QWidget()
        hol_layout = QVBoxLayout(hol_widget)
        hol_layout.setContentsMargins(16, 16, 16, 16)
        btn_add_hol = QPushButton("➕ Ajouter Jour Férié")
        btn_add_hol.setFixedHeight(38)
        btn_add_hol.setStyleSheet("background:#F59E0B; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_add_hol.clicked.connect(self.add_holiday)
        hol_layout.addWidget(btn_add_hol, alignment=Qt.AlignLeft)
        self.table_holidays = self._make_table(["Nom", "Date", "Récurrent", "Calendrier", "Actions"])
        hol_layout.addWidget(self.table_holidays)
        tabs.addTab(hol_widget, "🎉 Jours fériés")

        # Tab 3 : Vacances
        vac_widget = QWidget()
        vac_layout = QVBoxLayout(vac_widget)
        vac_layout.setContentsMargins(16, 16, 16, 16)
        btn_add_vac = QPushButton("➕ Ajouter Période de Vacances")
        btn_add_vac.setFixedHeight(38)
        btn_add_vac.setStyleSheet("background:#8B5CF6; color:white; border-radius:6px; padding:0 16px; font-weight:bold;")
        btn_add_vac.clicked.connect(self.add_vacation)
        vac_layout.addWidget(btn_add_vac, alignment=Qt.AlignLeft)
        self.table_vacations = self._make_table(["Nom", "Type", "Début", "Fin", "Calendrier", "Actions"])
        vac_layout.addWidget(self.table_vacations)
        tabs.addTab(vac_widget, "🏖️ Périodes de vacances")

        layout.addWidget(tabs)

        self.refresh_calendars_table()
        self.refresh_holidays_table()
        self.refresh_vacations_table()

    def _make_table(self, headers):
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
        """)
        return t

    def _stat_card(self, label, value, color):
        f = QFrame()
        f.setStyleSheet(f"QFrame {{ background:{color}; border-radius:10px; padding:12px; }}")
        v = QVBoxLayout(f)
        lbl_v = QLabel(value)
        lbl_v.setObjectName("val")
        lbl_v.setStyleSheet("font-size:28px; font-weight:bold; color:white;")
        lbl_v.setAlignment(Qt.AlignCenter)
        lbl_l = QLabel(label)
        lbl_l.setStyleSheet("font-size:12px; color:white;")
        lbl_l.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl_v)
        v.addWidget(lbl_l)
        return f

    def _set_stat(self, card, val):
        for c in card.findChildren(QLabel):
            if c.objectName() == "val":
                c.setText(str(val))

    def update_stats(self):
        self._set_stat(self.stat_cal,  len(self.calendars))
        self._set_stat(self.stat_hol,  len(self.holidays))
        self._set_stat(self.stat_vac,  len(self.vacations))
        if self.calendars:
            d = self.calcul_d_effectif(self.calendars[0])
            self._set_stat(self.stat_deff, d)

    def refresh_calendars_table(self):
        self.table_calendars.setRowCount(0)
        for row, cal in enumerate(self.calendars):
            self.table_calendars.insertRow(row)
            d_eff = self.calcul_d_effectif(cal)
            vals = [
                cal.name, cal.academic_year,
                str(cal.start_date), str(cal.end_date),
                str(cal.hours_per_day), str(cal.semester_count),
                str(d_eff)
            ]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_calendars.setItem(row, col, item)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 32)
            btn_del.setStyleSheet("background:#EF4444; color:white; border-radius:4px; border:none;")
            r = row
            btn_del.clicked.connect(lambda _, r=r: self.delete_calendar(r))
            self.table_calendars.setCellWidget(row, 7, btn_del)

    def refresh_holidays_table(self):
        self.table_holidays.setRowCount(0)
        for row, h in enumerate(self.holidays):
            self.table_holidays.insertRow(row)
            cal_name = h.calendar.name if h.calendar else "?"
            vals = [h.name, str(h.date), "✅" if h.is_recurring else "—", cal_name]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_holidays.setItem(row, col, item)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 32)
            btn_del.setStyleSheet("background:#EF4444; color:white; border-radius:4px; border:none;")
            r = row
            btn_del.clicked.connect(lambda _, r=r: self.delete_holiday(r))
            self.table_holidays.setCellWidget(row, 4, btn_del)

    def refresh_vacations_table(self):
        self.table_vacations.setRowCount(0)
        for row, v in enumerate(self.vacations):
            self.table_vacations.insertRow(row)
            cal_name = v.calendar.name if v.calendar else "?"
            type_val = v.type.value if v.type and hasattr(v.type, 'value') else str(v.type)
            vals = [v.name, type_val, str(v.start_date), str(v.end_date), cal_name]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_vacations.setItem(row, col, item)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 32)
            btn_del.setStyleSheet("background:#EF4444; color:white; border-radius:4px; border:none;")
            r = row
            btn_del.clicked.connect(lambda _, r=r: self.delete_vacation(r))
            self.table_vacations.setCellWidget(row, 5, btn_del)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()
        self.refresh_calendars_table()
        self.refresh_holidays_table()
        self.refresh_vacations_table()
        self.update_stats()


# ══════════════════════════════════════════════════════════════
# DIALOGUES
# ══════════════════════════════════════════════════════════════

class CalendarDialog(QDialog):
    def __init__(self, parent=None, universites=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Calendrier Académique")
        self.setMinimumWidth(480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = QLabel("📅 Nouveau Calendrier Académique")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)
        form = QFormLayout()
        form.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Calendrier 2025-2026")
        self.name_input.setFixedHeight(36)
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Ex: 2025-2026")
        self.year_input.setFixedHeight(36)
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedHeight(36)
        self.end_date = QDateEdit(QDate.currentDate().addMonths(6))
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedHeight(36)
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(1, 12)
        self.hours_spin.setValue(8)
        self.hours_spin.setFixedHeight(36)
        self.sem_spin = QSpinBox()
        self.sem_spin.setRange(1, 4)
        self.sem_spin.setValue(2)
        self.sem_spin.setFixedHeight(36)
        form.addRow("Nom *:", self.name_input)
        form.addRow("Année académique *:", self.year_input)
        form.addRow("Date début *:", self.start_date)
        form.addRow("Date fin *:", self.end_date)
        form.addRow("Heures/jour:", self.hours_spin)
        form.addRow("Nombre semestres:", self.sem_spin)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_c = QPushButton("Annuler")
        btn_c.setFixedSize(110, 36)
        btn_c.setStyleSheet("background:#e0e0e0; border:none; border-radius:6px;")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("✅ Enregistrer")
        btn_ok.setFixedSize(140, 36)
        btn_ok.setStyleSheet("background:#3B82F6; color:white; border:none; border-radius:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.validate)
        btns.addWidget(btn_c)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def validate(self):
        if not self.name_input.text().strip() or not self.year_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Nom et année académique obligatoires.")
            return
        self.accept()

    def get_data(self):
        sd = self.start_date.date()
        ed = self.end_date.date()
        return {
            'name'          : self.name_input.text().strip(),
            'academic_year' : self.year_input.text().strip(),
            'start_date'    : date(sd.year(), sd.month(), sd.day()),
            'end_date'      : date(ed.year(), ed.month(), ed.day()),
            'hours_per_day' : self.hours_spin.value(),
            'semester_count': self.sem_spin.value(),
        }


class HolidayDialog(QDialog):
    def __init__(self, parent=None, calendars=None):
        super().__init__(parent)
        self.calendars = calendars or []
        self.setWindowTitle("Ajouter un Jour Férié")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = QLabel("🎉 Nouveau Jour Férié")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)
        form = QFormLayout()
        form.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Fête Nationale")
        self.name_input.setFixedHeight(36)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedHeight(36)
        self.recurring = QCheckBox("Récurrent chaque année")
        self.cal_combo = QComboBox()
        self.cal_combo.setFixedHeight(36)
        for c in self.calendars:
            self.cal_combo.addItem(c.name, c.id)
        form.addRow("Nom *:", self.name_input)
        form.addRow("Date *:", self.date_edit)
        form.addRow("", self.recurring)
        form.addRow("Calendrier *:", self.cal_combo)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_c = QPushButton("Annuler")
        btn_c.setFixedSize(110, 36)
        btn_c.setStyleSheet("background:#e0e0e0; border:none; border-radius:6px;")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("✅ Enregistrer")
        btn_ok.setFixedSize(140, 36)
        btn_ok.setStyleSheet("background:#F59E0B; color:white; border:none; border-radius:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.validate)
        btns.addWidget(btn_c)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return
        self.accept()

    def get_data(self):
        d = self.date_edit.date()
        return {
            'name'        : self.name_input.text().strip(),
            'date'        : date(d.year(), d.month(), d.day()),
            'is_recurring': self.recurring.isChecked(),
            'calendar_id' : self.cal_combo.currentData(),
        }


class VacationDialog(QDialog):
    TYPES = {
        "Vacances de Noël"     : VacationTypeEnum.NOEL,
        "Vacances de Pâques"   : VacationTypeEnum.PAQUES,
        "Vacances d'été"       : VacationTypeEnum.ETE,
        "Vacances de Toussaint": VacationTypeEnum.TOUSSAINT,
    }

    def __init__(self, parent=None, calendars=None):
        super().__init__(parent)
        self.calendars = calendars or []
        self.setWindowTitle("Ajouter une Période de Vacances")
        self.setMinimumWidth(420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = QLabel("🏖️ Nouvelle Période de Vacances")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)
        form = QFormLayout()
        form.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Vacances de Noël 2025")
        self.name_input.setFixedHeight(36)
        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(36)
        self.type_combo.addItems(list(self.TYPES.keys()))
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedHeight(36)
        self.end_date = QDateEdit(QDate.currentDate().addDays(7))
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedHeight(36)
        self.cal_combo = QComboBox()
        self.cal_combo.setFixedHeight(36)
        for c in self.calendars:
            self.cal_combo.addItem(c.name, c.id)
        form.addRow("Nom *:", self.name_input)
        form.addRow("Type *:", self.type_combo)
        form.addRow("Début *:", self.start_date)
        form.addRow("Fin *:", self.end_date)
        form.addRow("Calendrier *:", self.cal_combo)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_c = QPushButton("Annuler")
        btn_c.setFixedSize(110, 36)
        btn_c.setStyleSheet("background:#e0e0e0; border:none; border-radius:6px;")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("✅ Enregistrer")
        btn_ok.setFixedSize(140, 36)
        btn_ok.setStyleSheet("background:#8B5CF6; color:white; border:none; border-radius:6px; font-weight:bold;")
        btn_ok.clicked.connect(self.validate)
        btns.addWidget(btn_c)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def validate(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return
        self.accept()

    def get_data(self):
        sd = self.start_date.date()
        ed = self.end_date.date()
        return {
            'name'       : self.name_input.text().strip(),
            'type'       : self.TYPES[self.type_combo.currentText()],
            'start_date' : date(sd.year(), sd.month(), sd.day()),
            'end_date'   : date(ed.year(), ed.month(), ed.day()),
            'calendar_id': self.cal_combo.currentData(),
        }