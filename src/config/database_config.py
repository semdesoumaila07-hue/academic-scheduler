"""
Configuration spécifique à la base de données.
"""
from pathlib import Path
from typing import Dict, Any


class DatabaseConfig:
    """Configuration de la base de données."""
    
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    BACKUP_DIR = BASE_DIR / "backups"
    
    DATABASE_FILE = "ordonnancement.db"
    DATABASE_PATH = DATA_DIR / DATABASE_FILE
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    
    CONNECTION_CONFIG = {
        'check_same_thread': False,
        'timeout': 30,
    }
    
    SQLITE_PRAGMAS = {
        'foreign_keys': 'ON',
        'journal_mode': 'WAL',
        'synchronous': 'NORMAL',
        'cache_size': -64000,
    }
    
    MAX_BACKUPS = 10
    AUTO_BACKUP_ENABLED = True
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Crée les répertoires nécessaires."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)


db_config = DatabaseConfig()