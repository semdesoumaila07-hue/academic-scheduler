from PyQt5.QtWidgets import QDialog

class ConstraintReportDialog(QDialog):
    """Dialogue pour soumettre un rapport de contrainte (squelette minimal)."""
    def __init__(self, parent=None, session=None, teacher_id=None):
        super().__init__(parent)
        self.session = session
        self.teacher_id = teacher_id
        self.setWindowTitle("Rapport de contrainte")
        # Ajoutez ici la logique UI et gestion des rapports
