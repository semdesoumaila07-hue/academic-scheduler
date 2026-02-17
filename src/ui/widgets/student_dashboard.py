"""
Tableau de bord minimal pour un étudiant : consultation d'EDT.
"""
from datetime import date, timedelta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QDateEdit
)
from PyQt5.QtCore import Qt

from ...database.db_manager import db_manager
from ...database.repositories import StudentRepository


class StudentDashboard(QMainWindow):
    def __init__(self, student_model, parent=None):
        super().__init__(parent)
        self.student = student_model
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Tableau de bord étudiant - {self.student.full_name}")
        self.setGeometry(200, 150, 900, 600)

        central = QWidget()
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        header_layout.addWidget(QLabel('Période:'))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(date.today())
        header_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(date.today() + timedelta(days=7))
        header_layout.addWidget(self.end_date)

        refresh_btn = QPushButton('Voir EDT')
        refresh_btn.clicked.connect(self.load_schedule)
        header_layout.addWidget(refresh_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Table for schedule slots
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Date', 'Début', 'Fin', 'Activité', 'Enseignant', 'Salle'])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # Load initial schedule
        self.load_schedule()

    def load_schedule(self):
        # Convert QDateEdit to date
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        session = db_manager.get_session()
        try:
            repo = StudentRepository(session)
            slots = repo.get_student_schedule(self.student.id, start, end)

            self.table.setRowCount(0)
            for slot in slots:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(slot.date)))
                self.table.setItem(row, 1, QTableWidgetItem(slot.start_time.strftime('%H:%M')))
                self.table.setItem(row, 2, QTableWidgetItem(slot.end_time.strftime('%H:%M')))
                activity_name = getattr(slot.activity, 'name', '') if slot.activity else ''
                teacher_name = getattr(slot.teacher, 'full_name', '') if slot.teacher else ''
                self.table.setItem(row, 3, QTableWidgetItem(activity_name))
                self.table.setItem(row, 4, QTableWidgetItem(teacher_name))
                self.table.setItem(row, 5, QTableWidgetItem(slot.room or ''))

        finally:
            session.close()
