from PyQt5.QtWidgets import QDialog

class LeaveRequestDialog(QDialog):
    """Dialogue pour soumettre une demande de congé (squelette minimal)."""
    def __init__(self, parent=None, session=None, teacher_id=None):
        super().__init__(parent)
        self.session = session
        self.teacher_id = teacher_id
        self.setWindowTitle("Demande de congé")
        # Ajoutez ici la logique UI et gestion des congés
