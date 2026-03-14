"""
Configuration de l'application - chemins et paramètres de base de données.
"""
from pathlib import Path

# Répertoire de base (racine du projet)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # config -> src -> project

# Base de données SQLite
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "ordonnancement.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Sauvegardes
BACKUP_DIR = BASE_DIR / "backups"
MAX_BACKUPS = 5
