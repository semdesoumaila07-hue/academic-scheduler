"""
Visualiseur d'emploi du temps pour un enseignant.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import TeacherRepository, ScheduleRepository


class TeacherScheduleViewer(QDialog):
    """Dialogue pour visualiser l'emploi du temps d'un enseignant."""

    def __init__(self, parent=None, session: Session = None):
        super().__init__(parent)
        self.session = session
        self.teacher_repo = TeacherRepository(session) if session else None
        self.schedule_repo = ScheduleRepository(session) if session else None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface."""
        self.setWindowTitle("Emploi du Temps Enseignant")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Emploi du Temps de l'Enseignant")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Filtres
        filters = QHBoxLayout()

        filters.addWidget(QLabel("Enseignant:"))
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("-- Sélectionner un enseignant --", None)
        filters.addWidget(self.teacher_combo)

        filters.addWidget(QLabel("Semaine du:"))
        self.week_date = QDateEdit()
        self.week_date.setDate(QDate.currentDate())
        self.week_date.setCalendarPopup(True)
        filters.addWidget(self.week_date)

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_schedule)
        filters.addWidget(btn_refresh)

        filters.addStretch()
        layout.addLayout(filters)

        # Grille d'emploi du temps
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"
        ])
        self.schedule_table.setRowCount(10)
        self.schedule_table.setVerticalHeaderLabels([
            "8h-9h", "9h-10h", "10h-11h", "11h-12h",
            "12h-13h", "13h-14h", "14h-15h", "15h-16h",
            "16h-17h", "17h-18h",
        ])

        layout.addWidget(self.schedule_table)

        # Boutons
        buttons = QHBoxLayout()

        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        buttons.addStretch()
        buttons.addWidget(btn_close)

        layout.addLayout(buttons)

        # Charger les enseignants et l'emploi du temps initial
        self.load_teachers()
        self.load_schedule()

    def load_teachers(self):
        """Charge la liste des enseignants."""
        if not self.teacher_repo:
            return
        try:
            teachers = self.teacher_repo.get_all()
            for t in teachers:
                self.teacher_combo.addItem(t.full_name, t.id)
        except Exception:
            pass

    def load_schedule(self):
        """Charge l'emploi du temps de l'enseignant sélectionné."""
        self.schedule_table.clearContents()

        if not self.schedule_repo:
            return

        teacher_id = self.teacher_combo.currentData()
        if not teacher_id:
            return

        # Calculer la semaine (lundi -> samedi)
        qd = self.week_date.date()
        offset = qd.dayOfWeek() - 1  # 1=lundi
        monday = qd.addDays(-offset)
        start_date = monday.toPyDate()
        end_date = monday.addDays(5).toPyDate()

        try:
            slots = self.schedule_repo.get_by_teacher(teacher_id, start_date, end_date)
        except Exception:
            return

        for slot in slots:
            weekday = slot.date.weekday()  # 0=lundi...6=dimanche
            if weekday < 0 or weekday > 5:
                continue
            col = weekday

            start_hour = slot.start_time.hour + slot.start_time.minute / 60.0
            row = int(start_hour - 8)
            if row < 0 or row >= self.schedule_table.rowCount():
                continue

            activity_name = getattr(slot.activity, "name", "") if getattr(slot, "activity", None) else ""
            cohort_name = getattr(slot.cohort, "name", "") if getattr(slot, "cohort", None) else ""
            room = slot.room or ""

            text = (
                f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}\n"
                f"{activity_name}\n"
                f"{cohort_name}\n"
                f"Salle {room}"
            )

            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(row, col, item)

