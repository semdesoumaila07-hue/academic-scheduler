"""
Script de migration : remplace la contrainte UNIQUE(code) sur ufrs
par une contrainte UNIQUE(code, university_id).

Exécuter UNE SEULE FOIS :
    python migrate_ufr_unique.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "ordonnancement.db"


def migrate():
    if not DB_PATH.exists():
        print(f"❌ Base de données introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("BEGIN")

    try:
        # 1. Créer la nouvelle table avec la bonne contrainte
        conn.execute("""
            CREATE TABLE ufrs_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                code VARCHAR(10) NOT NULL,
                director VARCHAR(200),
                university_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
                UNIQUE (code, university_id)
            )
        """)

        # 2. Copier les données existantes
        conn.execute("""
            INSERT INTO ufrs_new (id, name, code, director, university_id, created_at, updated_at)
            SELECT id, name, code, director, university_id, created_at, updated_at
            FROM ufrs
        """)

        # 3. Supprimer l'ancienne table
        conn.execute("DROP TABLE ufrs")

        # 4. Renommer la nouvelle
        conn.execute("ALTER TABLE ufrs_new RENAME TO ufrs")

        # 5. Recréer les index
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ufrs_code ON ufrs(code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ufrs_university ON ufrs(university_id)")

        conn.execute("COMMIT")
        conn.execute("PRAGMA foreign_keys = ON")
        print("✅ Migration réussie : contrainte UNIQUE(code, university_id) appliquée.")

    except Exception as e:
        conn.execute("ROLLBACK")
        print(f"❌ Erreur migration : {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()