"""
main.py — Point d'entree de l'application
Lance directement AppWindow (pas de popup de connexion).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.database.db_manager import db_manager


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    db_manager.initialize()
    db_manager.create_tables()

    from src.ui.app_window import AppWindow
    # Verifier activites urgentes au demarrage
    try:
        from src.services.notification_service import check_urgent_activities
        check_urgent_activities()
    except Exception as _e:
        print(f"[startup] notif check: {_e}")
    window = AppWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()