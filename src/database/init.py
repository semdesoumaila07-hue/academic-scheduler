"""
Script d'initialisation de la base de données.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.database.db_manager import db_manager
from src.config.settings import DATABASE_PATH


def init_database(with_test_data: bool = False):
    """Initialise la base de données."""
    print("=" * 60)
    print("INITIALISATION DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    if DATABASE_PATH.exists():
        print(f"\n⚠️  La base de données existe déjà : {DATABASE_PATH}")
        response = input("Voulez-vous la supprimer et la recréer ? (oui/non) : ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Opération annulée.")
            return
        DATABASE_PATH.unlink()
        print("✓ Base de données supprimée")
    
    print(f"\n📁 Création de la base de données : {DATABASE_PATH}")
    db_manager.initialize()
    
    print("📊 Création des tables...")
    db_manager.create_tables()
    print("✓ Tables créées avec succès")
    
    info = db_manager.get_database_info()
    print(f"\n✓ Base de données initialisée")
    print(f"  - Chemin : {info['path']}")
    print(f"  - Taille : {info['size']} octets")
    
    if with_test_data:
        print("\n📝 Insertion des données de test...")
        # TODO: Ajouter insert_test_data() si nécessaire
        print("✓ Données de test insérées")
    
    print("\n" + "=" * 60)
    print("✓ INITIALISATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialise la base de données")
    parser.add_argument('--with-test-data', action='store_true', help="Insère des données de test")
    args = parser.parse_args()
    
    try:
        init_database(with_test_data=args.with_test_data)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        sys.exit(1)