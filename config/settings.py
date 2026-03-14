"""
Configuration de l'application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "ordonnancement.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Backup settings
BACKUP_DIR = BASE_DIR / "backups"
MAX_BACKUPS = 10

# Application settings
APP_NAME = "Système d'Ordonnancement Académique P-équitable"
APP_VERSION = "1.0.0"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Data directories
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"