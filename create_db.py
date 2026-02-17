"""
Script pour créer une base de données vide.
"""
import sys
from pathlib import Path

# Ajouter src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.db_manager import db_manager

def main():
    """Crée la base de données vide."""
    print("🔄 Création de la base de données...")
    
    try:
        # Initialiser la base de données
        db_manager.initialize()
        
        print("✅ Base de données créée avec succès !")
        print(f"📁 Fichier : {db_manager.database_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()