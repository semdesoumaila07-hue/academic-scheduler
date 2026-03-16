"""
Tableau de bord enseignant : Mon EDT, Demander congé, Mes demandes, Disponibilités.
"""
from datetime import date, time, timedelta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QDateEdit,
    QTabWidget, QHeaderView, QMessageBox, QTimeEdit, QComboBox
)
from PyQt5.QtCore import Qt, QTime

from ...database.db_manager import db_manager
from ...database.repositories import (
    ScheduleRepository, LeaveRequestRepository,
    TeacherAvailabilityRepository, ConstraintReportRepository,
)
from ..dialogs.leave_request_dialog import LeaveRequestDialog
from ..dialogs.constraint_report_dialog import ConstraintReportDialog

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


class TeacherDashboard(QMainWindow):
    """Tableau de bord pour un enseignant connecté."""

    def __init__(self, teacher_model, parent=None):
        super().__init__(parent)
        self.teacher = teacher_model
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Tableau de bord enseignant - {self.teacher.full_name}")
        self.setGeometry(200, 150, 950, 650)

        central = QWidget()
        layout = QVBoxLayout()

        # En-tête
        header = QLabel(f"👨‍🏫 {self.teacher.full_name} — {self.teacher.speciality}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        tabs = QTabWidget()

        # Onglet Mon emploi du temps
        tab_edt = QWidget()
        layout_edt = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Période:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(date.today())
        row.addWidget(self.start_date)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(date.today() + timedelta(days=14))
        row.addWidget(self.end_date)
        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.load_schedule)
        row.addWidget(btn_refresh)
        row.addStretch()
        layout_edt.addLayout(row)
        self.schedule_table = QTableWidget(0, 6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Date", "Début", "Fin", "Activité", "Cohorte", "Salle"
        ])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_edt.addWidget(self.schedule_table)
        tab_edt.setLayout(layout_edt)
        tabs.addTab(tab_edt, "Mon emploi du temps")

        # Onglet Mes demandes de congé
        tab_leave = QWidget()
        layout_leave = QVBoxLayout()
        btn_new_leave = QPushButton("📨 Nouvelle demande de congé")
        btn_new_leave.clicked.connect(self.on_new_leave_request)
        layout_leave.addWidget(btn_new_leave)
        self.leave_table = QTableWidget(0, 5)
        self.leave_table.setHorizontalHeaderLabels([
            "Début", "Fin", "Type", "Statut", "Raison"
        ])
        self.leave_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_leave.addWidget(self.leave_table)
        tab_leave.setLayout(layout_leave)
        tabs.addTab(tab_leave, "Mes demandes de congé")

        # Onglet Mes disponibilités (plages horaires récurrentes par jour)
        tab_avail = QWidget()
        layout_avail = QVBoxLayout()
        layout_avail.addWidget(QLabel("Créneaux où vous êtes disponible chaque semaine (optionnel) :"))
        row_avail = QHBoxLayout()
        row_avail.addWidget(QLabel("Jour :"))
        self.avail_day_combo = QComboBox()
        for i, name in enumerate(JOURS):
            self.avail_day_combo.addItem(name, i)
        row_avail.addWidget(self.avail_day_combo)
        row_avail.addWidget(QLabel("De :"))
        self.avail_start = QTimeEdit()
        self.avail_start.setTime(QTime(8, 0))
        row_avail.addWidget(self.avail_start)
        row_avail.addWidget(QLabel("à :"))
        self.avail_end = QTimeEdit()
        self.avail_end.setTime(QTime(18, 0))
        row_avail.addWidget(self.avail_end)
<<<<<<< HEAD
        # Ajout des champs période
        row_avail.addWidget(QLabel("Période :"))
        self.avail_period_start = QDateEdit()
        self.avail_period_start.setCalendarPopup(True)
        self.avail_period_start.setDate(date.today())
        row_avail.addWidget(self.avail_period_start)
        self.avail_period_end = QDateEdit()
        self.avail_period_end.setCalendarPopup(True)
        self.avail_period_end.setDate(date.today() + timedelta(days=14))
        row_avail.addWidget(self.avail_period_end)
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        btn_add_avail = QPushButton("Ajouter créneau")
        btn_add_avail.clicked.connect(self.on_add_availability)
        row_avail.addWidget(btn_add_avail)
        row_avail.addStretch()
        layout_avail.addLayout(row_avail)
        self.avail_table = QTableWidget(0, 4)
        self.avail_table.setHorizontalHeaderLabels(["Jour", "Début", "Fin", "Action"])
        self.avail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_avail.addWidget(self.avail_table)
        tab_avail.setLayout(layout_avail)
        tabs.addTab(tab_avail, "Mes disponibilités")

        # Onglet Mes signalements (conflits / contraintes)
        tab_reports = QWidget()
        layout_reports = QVBoxLayout()
        btn_new_report = QPushButton("📢 Signaler un conflit ou une contrainte")
        btn_new_report.clicked.connect(self.on_new_constraint_report)
        layout_reports.addWidget(btn_new_report)
        self.reports_table = QTableWidget(0, 4)
        self.reports_table.setHorizontalHeaderLabels(["Date", "Type", "Statut", "Description"])
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_reports.addWidget(self.reports_table)
        tab_reports.setLayout(layout_reports)
        tabs.addTab(tab_reports, "Mes signalements")

        layout.addWidget(tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.load_schedule()
        self.load_leave_requests()
        self.load_availability()
        self.load_constraint_reports()

    def load_schedule(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        session = db_manager.get_session()
        try:
            repo = ScheduleRepository(session)
            slots = repo.get_by_teacher(self.teacher.id, start, end)
            self.schedule_table.setRowCount(0)
            for slot in slots:
                row = self.schedule_table.rowCount()
                self.schedule_table.insertRow(row)
                self.schedule_table.setItem(row, 0, QTableWidgetItem(str(slot.date)))
                self.schedule_table.setItem(row, 1, QTableWidgetItem(
                    slot.start_time.strftime("%H:%M") if slot.start_time else ""
                ))
                self.schedule_table.setItem(row, 2, QTableWidgetItem(
                    slot.end_time.strftime("%H:%M") if slot.end_time else ""
                ))
                activity_name = getattr(slot.activity, "name", "") if slot.activity else ""
                cohort_name = getattr(slot.cohort, "name", "") if slot.cohort else ""
                self.schedule_table.setItem(row, 3, QTableWidgetItem(activity_name))
                self.schedule_table.setItem(row, 4, QTableWidgetItem(cohort_name))
                self.schedule_table.setItem(row, 5, QTableWidgetItem(slot.room or ""))
        finally:
            session.close()

    def load_leave_requests(self):
        session = db_manager.get_session()
        try:
            repo = LeaveRequestRepository(session)
            requests = repo.get_by_teacher(self.teacher.id)
            self.leave_table.setRowCount(0)
            for req in requests:
                row = self.leave_table.rowCount()
                self.leave_table.insertRow(row)
                status_str = req.status.value if hasattr(req.status, "value") else str(req.status)
                self.leave_table.setItem(row, 0, QTableWidgetItem(str(req.start_date)))
                self.leave_table.setItem(row, 1, QTableWidgetItem(str(req.end_date)))
                type_str = req.leave_type.value if hasattr(req.leave_type, "value") else str(req.leave_type)
                self.leave_table.setItem(row, 2, QTableWidgetItem(type_str))
                self.leave_table.setItem(row, 3, QTableWidgetItem(status_str))
                self.leave_table.setItem(row, 4, QTableWidgetItem((req.reason or "")[:60]))
        finally:
            session.close()

    def on_new_leave_request(self):
        session = db_manager.get_session()
        try:
            dialog = LeaveRequestDialog(self, session, teacher_id=self.teacher.id)
            if dialog.exec_():
                self.load_leave_requests()
        finally:
            session.close()

    def load_availability(self):
        session = db_manager.get_session()
        try:
            repo = TeacherAvailabilityRepository(session)
            slots = repo.get_by_teacher(self.teacher.id)
            self.avail_table.setRowCount(0)
            for s in slots:
                row = self.avail_table.rowCount()
                self.avail_table.insertRow(row)
                self.avail_table.setItem(row, 0, QTableWidgetItem(JOURS[s.day_of_week]))
                self.avail_table.setItem(row, 1, QTableWidgetItem(
                    s.start_time.strftime("%H:%M") if s.start_time else ""
                ))
                self.avail_table.setItem(row, 2, QTableWidgetItem(
                    s.end_time.strftime("%H:%M") if s.end_time else ""
                ))
                btn_del = QPushButton("Supprimer")
                btn_del.setProperty("slot_id", s.id)
                btn_del.clicked.connect(lambda checked=False, sid=s.id: self.on_delete_availability(sid))
                self.avail_table.setCellWidget(row, 3, btn_del)
        finally:
            session.close()

    def on_add_availability(self):
        day = self.avail_day_combo.currentData()
        qstart = self.avail_start.time()
        qend = self.avail_end.time()
        start_t = time(qstart.hour(), qstart.minute())
        end_t = time(qend.hour(), qend.minute())
<<<<<<< HEAD
        # Ajout des dates de début et fin (correction)
        period_start = self.avail_period_start.date().toPyDate()
        period_end = self.avail_period_end.date().toPyDate()
        if end_t <= start_t:
            QMessageBox.warning(self, "Validation", "L'heure de fin doit être après l'heure de début.")
            return
        if period_end < period_start:
            QMessageBox.warning(self, "Validation", "La date de fin doit être après la date de début.")
            return
=======
        if end_t <= start_t:
            QMessageBox.warning(self, "Validation", "L'heure de fin doit être après l'heure de début.")
            return
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
        session = db_manager.get_session()
        try:
            repo = TeacherAvailabilityRepository(session)
            repo.create(
                teacher_id=self.teacher.id,
                day_of_week=day,
                start_time=start_t,
                end_time=end_t,
<<<<<<< HEAD
                period_start=period_start,
                period_end=period_end
=======
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
            )
            self.load_availability()
        finally:
            session.close()

    def on_delete_availability(self, slot_id: int):
        session = db_manager.get_session()
        try:
            repo = TeacherAvailabilityRepository(session)
            slot = repo.get_by_id(slot_id)
            if slot:
                repo.delete(slot_id)
            self.load_availability()
        finally:
            session.close()

    def load_constraint_reports(self):
        session = db_manager.get_session()
        try:
            repo = ConstraintReportRepository(session)
            reports = repo.get_by_teacher(self.teacher.id)
            self.reports_table.setRowCount(0)
            for r in reports:
                row = self.reports_table.rowCount()
                self.reports_table.insertRow(row)
                date_str = r.reported_at.strftime("%d/%m/%Y %H:%M") if r.reported_at else ""
                type_str = r.report_type.value if hasattr(r.report_type, "value") else str(r.report_type)
                status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
                self.reports_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.reports_table.setItem(row, 1, QTableWidgetItem(type_str))
                self.reports_table.setItem(row, 2, QTableWidgetItem(status_str))
                self.reports_table.setItem(row, 3, QTableWidgetItem((r.description or "")[:80]))
        finally:
            session.close()

    def on_new_constraint_report(self):
        session = db_manager.get_session()
        try:
            dialog = ConstraintReportDialog(self, session, teacher_id=self.teacher.id)
            if dialog.exec_():
                self.load_constraint_reports()
        finally:
            session.close()
