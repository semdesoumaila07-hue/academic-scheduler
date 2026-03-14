"""
Point d'entrée conforme au document de conception.

Utilise CustomTkinter (interface) et JSON/CSV (données) comme spécifié.
Lance l'application en mode conception.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import customtkinter as ctk
except ImportError:
    print("Erreur: customtkinter non installé. Exécutez: pip install customtkinter")
    sys.exit(1)

from src.data.data_manager import data_manager
from src.ui_ctk.main_window_ctk import MainWindowCTK


def main():
    """Lance l'application conforme à la conception."""
    # Charger les données (JSON/CSV)
    data_manager.load_all()

    # Configuration CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Pfair Scheduler - Ordonnancement Académique P-équitable")
    app.geometry("1280x800")
    app.minsize(1024, 600)

    main_window = MainWindowCTK(app)
    main_window.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
