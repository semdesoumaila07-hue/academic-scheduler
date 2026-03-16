"""
<<<<<<< HEAD
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
=======
Point d'entrée de l'application avec authentification
Système d'Ordonnancement Académique P-équitable
"""
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow
from src.ui.login_dialog import LoginDialog


def install_global_exception_handler():
    """Installe un gestionnaire global pour afficher les erreurs Python."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        # Ne pas interférer avec Ctrl+C
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Afficher la trace complète dans la console
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        # Essayer aussi de montrer une boîte de dialogue (si une QApplication existe)
        try:
            app = QApplication.instance()
            if app is not None:
                msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                QMessageBox.critical(
                    None,
                    "Erreur inattendue",
                    f"Une erreur inattendue est survenue :\n\n{msg}",
                )
        except Exception:
            # En dernier recours, on s'appuie uniquement sur la console
            pass

    sys.excepthook = handle_exception


def main():
    """Point d'entrée principal avec authentification."""
    install_global_exception_handler()

    app = QApplication(sys.argv)
    
    # Appliquer un style global
    app.setStyle('Fusion')
    
    # ==========================================
    # ÉCRAN DE CONNEXION
    # ==========================================
    login_dialog = LoginDialog()
    
    # Afficher les identifiants de test (à retirer en production)
    login_dialog.show_credentials_info()
    
    # Variable pour stocker les infos utilisateur
    user_data = None
    
    def on_login_success(user):
        nonlocal user_data
        user_data = user
    
    # Connecter le signal
    login_dialog.login_successful.connect(on_login_success)
    
    # Attendre la connexion
    result = login_dialog.exec_()
    
    if result != LoginDialog.Accepted:
        # Utilisateur a annulé
        return 0
    
    # ==========================================
    # FENÊTRE PRINCIPALE AVEC RESTRICTIONS
    # ==========================================
    window = MainWindow(user_data)
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
