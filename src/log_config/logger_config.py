"""
Configuration du système de journalisation.

Gère la création et la configuration des loggers de l'application.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


# Répertoire des logs
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Niveaux de log
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Format des messages
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Fichiers de log
APP_LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
DATABASE_LOG_FILE = LOGS_DIR / "database.log"
PFAIR_LOG_FILE = LOGS_DIR / "pfair.log"


def setup_logger(name: str = 'academic_scheduler', 
                level: str = 'INFO',
                log_to_file: bool = True,
                log_to_console: bool = True) -> logging.Logger:
    """
    Configure et retourne un logger.
    
    Args:
        name: Nom du logger
        level: Niveau de log ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_to_file: Si True, écrit dans un fichier
        log_to_console: Si True, écrit dans la console
        
    Returns:
        Logger configuré
    """
    # Créer le logger
    logger = logging.getLogger(name)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVELS.get(level, logging.INFO))
    
    # Format
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Handler fichier
    if log_to_file:
        # Fichier principal avec rotation par taille
        file_handler = RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Fichier erreurs uniquement
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    # Handler console
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger existant ou en crée un nouveau.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger
    """
    logger = logging.getLogger(name)
    
    # Si pas encore configuré, le configurer
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


def setup_database_logger() -> logging.Logger:
    """
    Configure un logger spécifique pour la base de données.
    
    Returns:
        Logger pour la base de données
    """
    logger = logging.getLogger('database')
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Fichier dédié aux opérations de base de données
    db_handler = RotatingFileHandler(
        DATABASE_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    db_handler.setLevel(logging.DEBUG)
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    
    return logger


def setup_pfair_logger() -> logging.Logger:
    """
    Configure un logger spécifique pour l'algorithme Pfair.
    
    Returns:
        Logger pour Pfair
    """
    logger = logging.getLogger('pfair')
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Fichier dédié à l'algorithme Pfair
    pfair_handler = RotatingFileHandler(
        PFAIR_LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    pfair_handler.setLevel(logging.DEBUG)
    pfair_handler.setFormatter(formatter)
    logger.addHandler(pfair_handler)
    
    return logger


def log_function_call(logger: logging.Logger):
    """
    Décorateur pour logger les appels de fonction.
    
    Args:
        logger: Logger à utiliser
        
    Returns:
        Décorateur
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Appel de {func.__name__} avec args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} terminé avec succès")
                return result
            except Exception as e:
                logger.error(f"Erreur dans {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


def clean_old_logs(days: int = 30) -> int:
    """
    Supprime les fichiers de log plus anciens que X jours.
    
    Args:
        days: Nombre de jours
        
    Returns:
        Nombre de fichiers supprimés
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for log_file in LOGS_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            log_file.unlink()
            deleted_count += 1
    
    return deleted_count


# Logger principal de l'application
app_logger = setup_logger('academic_scheduler')
