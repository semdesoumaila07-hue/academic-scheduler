"""
Visualiseur d'emploi du temps.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from sqlalchemy.orm import Session

from ...database.repositories import CohortRepository, ScheduleRepository


class ScheduleViewer(QDialog):
    """Dialogue pour visualiser les emplois du temps."""
    
    def __init__(self, parent=None, session: Session = None):
        super().__init__(parent)
        self.session = session
        self.cohort_repo = CohortRepository(session) if session else None
        self.schedule_repo = ScheduleRepository(session) if session else None
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface."""
        self.setWindowTitle("Visualiseur d'Emploi du Temps")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Emploi du Temps")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Filtres
        filters = QHBoxLayout()
        
        filters.addWidget(QLabel("Cohorte:"))
        self.cohort_combo = QComboBox()
        self.cohort_combo.addItem("Toutes les cohortes", None)
        filters.addWidget(self.cohort_combo)
        
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
        self.schedule_table.setRowCount(10)  # 10 créneaux horaires
        self.schedule_table.setVerticalHeaderLabels([
            "8h-9h", "9h-10h", "10h-11h", "11h-12h",
            "12h-13h", "13h-14h", "14h-15h", "15h-16h",
            "16h-17h", "17h-18h",
        ])
        
        layout.addWidget(self.schedule_table)
        
        # Boutons
        buttons = QHBoxLayout()
        
        btn_export = QPushButton("📥 Exporter PDF")
        buttons.addWidget(btn_export)
        
        btn_print = QPushButton("🖨️ Imprimer")
        buttons.addWidget(btn_print)
        
        buttons.addStretch()
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        buttons.addWidget(btn_close)
        
        layout.addLayout(buttons)
        
        # Charger les cohorte et l'EDT initial
        self.load_cohorts()
        self.load_schedule()
    
    def load_cohorts(self):
        """Charge la liste des cohortes dans le combo."""
        if not self.cohort_repo:
            return
        try:
            cohorts = self.cohort_repo.get_all()
            for c in cohorts:
                label = f"{c.name} ({c.academic_year})"
                self.cohort_combo.addItem(label, c.id)
        except Exception:
            pass
    
    def load_schedule(self):
        """Charge l'emploi du temps depuis la base de données."""
        self.schedule_table.clearContents()
        
        if not self.schedule_repo:
            return
        
        # Calculer la semaine (lundi -> samedi) à partir de la date choisie
        qd = self.week_date.date()
        # QDate.dayOfWeek : 1 = lundi, ..., 7 = dimanche
        offset = qd.dayOfWeek() - 1
        monday = qd.addDays(-offset)
        start_date = monday.toPyDate()
        end_date = monday.addDays(5).toPyDate()  # lundi à samedi
        
        cohort_id = self.cohort_combo.currentData()
        
        try:
            if cohort_id:
                slots = self.schedule_repo.get_by_cohort(cohort_id, start_date, end_date)
            else:
                slots = self.schedule_repo.get_by_date_range(start_date, end_date)
        except Exception:
            return
        
        for slot in slots:
            # Jour de la semaine -> colonne (0=lundi,...,5=samedi)
            weekday = slot.date.weekday()  # 0=lundi ... 6=dimanche
            if weekday < 0 or weekday > 5:
                continue
            col = weekday
            
            # Ligne en fonction de l'heure de début (suppose journée 8h-18h)
            start_hour = slot.start_time.hour + slot.start_time.minute / 60.0
            row = int(start_hour - 8)
            if row < 0 or row >= self.schedule_table.rowCount():
                continue
            
            activity_name = getattr(slot.activity, "name", "") if getattr(slot, "activity", None) else ""
            teacher_name = getattr(slot.teacher, "full_name", "") if getattr(slot, "teacher", None) else ""
            room = slot.room or ""
            
            text = (
                f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}\n"
                f"{activity_name}\n"
                f"{teacher_name}\n"
                f"Salle {room}"
            )
            
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(row, col, item)