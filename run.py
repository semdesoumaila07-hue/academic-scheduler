"""
Point d'entrée principal de l'application.

Mode conception (config) : CustomTkinter + JSON/CSV (conforme au document conception.pdf)
Mode legacy : PyQt5 + SQLite (authentification)
"""
import sys
import json
from pathlib import Path

# Vérifier le mode dans app_config
CONFIG_PATH = Path(__file__).parent / "config" / "app_config.json"
conception_mode = False
if CONFIG_PATH.exists():
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        conception_mode = cfg.get("conception_mode", False)
    except Exception:
        pass

if conception_mode:
    # Lancer la version conforme à la conception (CustomTkinter + JSON/CSV)
    from run_conception import main
else:
    # Lancer la version legacy (PyQt5 + SQLite)
    def main():
        from PyQt5.QtWidgets import QApplication
        from src.database.db_manager import db_manager
        from src.ui.login_window import LoginWindow
        from src.ui.main_window import MainWindow

        app = QApplication(sys.argv)
        db_manager.initialize()
        db_manager.create_tables()
        login_window = LoginWindow()

        def on_login_success(user):
            login_window.close()
            # Garder une référence au MainWindow sur l'objet QApplication
            # pour éviter qu'il soit garbage-collected et fermé immédiatement.
            main_window = MainWindow(current_user=user)
            app.main_window = main_window
            app.main_window.show()

        login_window.user_authenticated.connect(on_login_success)
        login_window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
