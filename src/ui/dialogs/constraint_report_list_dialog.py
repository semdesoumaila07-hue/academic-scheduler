"""
Dialogue listant les signalements de conflits/contraintes (vue admin).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView
)
from sqlalchemy.orm import Session

from ...database.repositories import ConstraintReportRepository


class ConstraintReportListDialog(QDialog):
    """Liste des signalements enseignants pour l'admin."""

    def __init__(self, parent=None, session: Session = None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Signalements des enseignants")
        self.setMinimumSize(750, 450)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Conflits et contraintes signalés par les enseignants :"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Enseignant", "Date", "Type", "Statut", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        if session:
            self._load(session)

    def _load(self, session: Session):
        repo = ConstraintReportRepository(session)
        reports = repo.session.query(repo.model).order_by(
            repo.model.reported_at.desc()
        ).all()
        self.table.setRowCount(0)
        for r in reports:
            row = self.table.rowCount()
            self.table.insertRow(row)
            teacher_name = getattr(r.teacher, "full_name", "") if r.teacher else ""
            date_str = r.reported_at.strftime("%d/%m/%Y %H:%M") if r.reported_at else ""
            type_str = r.report_type.value if hasattr(r.report_type, "value") else str(r.report_type)
            status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
            self.table.setItem(row, 0, QTableWidgetItem(teacher_name))
            self.table.setItem(row, 1, QTableWidgetItem(date_str))
            self.table.setItem(row, 2, QTableWidgetItem(type_str))
            self.table.setItem(row, 3, QTableWidgetItem(status_str))
            self.table.setItem(row, 4, QTableWidgetItem((r.description or "")[:100]))
