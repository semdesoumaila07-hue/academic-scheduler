"""
Gestionnaire de connexion à la base de données.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config.settings import DATABASE_URL, DATABASE_PATH, BACKUP_DIR, MAX_BACKUPS
from .models import Base


class DatabaseManager:
    """
    Gestionnaire de connexion et d'opérations sur la base de données.
    
    Attributes:
        engine: Moteur SQLAlchemy
        SessionLocal: Fabrique de sessions
    """
    
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialise le gestionnaire de base de données."""
        if self._initialized:
            return
        
        self.engine = None
        self.SessionLocal = None
        self._initialized = True
    
    def initialize(self, database_url: str = None) -> None:
        """
        Initialise la connexion à la base de données.
        
        Args:
            database_url: URL de connexion (utilise DATABASE_URL par défaut)
        """
        if database_url is None:
            database_url = DATABASE_URL
        
        # Créer le répertoire data s'il n'existe pas
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer le moteur SQLAlchemy
        # Pour SQLite, nous utilisons check_same_thread=False pour permettre
        # l'utilisation multi-thread (nécessaire pour PyQt)
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Mettre à True pour voir les requêtes SQL
        )
        
        # Activer les clés étrangères pour SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # Créer la fabrique de sessions
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self) -> None:
        """Crée toutes les tables dans la base de données."""
        if self.engine is None:
            raise RuntimeError("La base de données n'est pas initialisée")
        
        Base.metadata.create_all(bind=self.engine)
        self._migrate_users_teacher_id()

    def _migrate_users_teacher_id(self) -> None:
        """Ajoute la colonne teacher_id à la table users si elle n'existe pas (migration)."""
        try:
            with self.engine.connect() as conn:
                r = conn.execute(text(
                    "SELECT COUNT(*) FROM pragma_table_info('users') WHERE name='teacher_id'"
                ))
                if r.scalar() == 0:
                    conn.execute(text(
                        "ALTER TABLE users ADD COLUMN teacher_id INTEGER REFERENCES teachers(id)"
                    ))
                    conn.commit()
        except Exception:
            pass
    
    def drop_tables(self) -> None:
        """Supprime toutes les tables de la base de données."""
        if self.engine is None:
            raise RuntimeError("La base de données n'est pas initialisée")
        
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """
        Crée et retourne une nouvelle session.
        
        Returns:
            Session SQLAlchemy
        """
        if self.SessionLocal is None:
            raise RuntimeError("La base de données n'est pas initialisée")
        
        return self.SessionLocal()
    
    def backup(self, backup_name: str = None) -> Path:
        """
        Crée une sauvegarde de la base de données.
        
        Args:
            backup_name: Nom du fichier de sauvegarde (auto-généré si None)
            
        Returns:
            Chemin du fichier de sauvegarde
        """
        if not DATABASE_PATH.exists():
            raise FileNotFoundError("La base de données n'existe pas")
        
        # Créer le répertoire de sauvegarde s'il n'existe pas
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Générer le nom du fichier de sauvegarde
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ordonnancement_backup_{timestamp}.db"
        
        backup_path = BACKUP_DIR / backup_name
        
        # Copier le fichier de base de données
        shutil.copy2(DATABASE_PATH, backup_path)
        
        # Nettoyer les anciennes sauvegardes
        self._cleanup_old_backups()
        
        return backup_path
    
    def restore(self, backup_path: Path) -> None:
        """
        Restaure la base de données depuis une sauvegarde.
        
        Args:
            backup_path: Chemin du fichier de sauvegarde
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Le fichier de sauvegarde n'existe pas: {backup_path}")
        
        # Fermer toutes les connexions
        if self.engine:
            self.engine.dispose()
        
        # Restaurer le fichier
        shutil.copy2(backup_path, DATABASE_PATH)
        
        # Réinitialiser la connexion
        self.initialize()
    
    def _cleanup_old_backups(self) -> None:
        """Supprime les anciennes sauvegardes au-delà de MAX_BACKUPS."""
        if not BACKUP_DIR.exists():
            return
        
        # Lister tous les fichiers de sauvegarde
        backups = sorted(
            BACKUP_DIR.glob("ordonnancement_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Supprimer les sauvegardes excédentaires
        for backup in backups[MAX_BACKUPS:]:
            backup.unlink()
    
    def get_database_size(self) -> int:
        """
        Retourne la taille de la base de données en octets.
        
        Returns:
            Taille en octets
        """
        if not DATABASE_PATH.exists():
            return 0
        
        return DATABASE_PATH.stat().st_size
    
    def get_database_info(self) -> dict:
        """
        Retourne les informations sur la base de données.
        
        Returns:
            Dictionnaire d'informations
        """
        if not DATABASE_PATH.exists():
            return {
                'exists': False,
                'path': str(DATABASE_PATH),
                'size': 0,
            }
        
        stat = DATABASE_PATH.stat()
        
        return {
            'exists': True,
            'path': str(DATABASE_PATH),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
        }
    
    def vacuum(self) -> None:
        """Optimise la base de données SQLite (VACUUM)."""
        if self.engine is None:
            raise RuntimeError("La base de données n'est pas initialisée")
        
        with self.engine.connect() as conn:
            conn.execute(text("VACUUM"))
    
    def close(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None


# Instance globale du gestionnaire
db_manager = DatabaseManager()