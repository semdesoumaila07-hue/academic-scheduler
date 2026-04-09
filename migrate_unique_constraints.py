"""
migrate_unique_constraints.py
------------------------------
Script de migration à exécuter UNE SEULE FOIS pour corriger les contraintes
UNIQUE trop larges dans la base de données.

Problèmes corrigés :
  - ufrs.code       : UNIQUE global → UNIQUE(code, university_id)
  - programs.code   : UNIQUE global → UNIQUE(code, ufr_id)

SQLite ne permet pas de modifier une contrainte existante directement.
La technique standard est : créer nouvelle table → copier données → supprimer
l'ancienne → renommer.

Usage :
    python migrate_unique_constraints.py
    # ou depuis le code :
    from migrate_unique_constraints import run_migration
    run_migration("chemin/vers/votre_base.db")
"""

import sqlite3
import shutil
import os
from datetime import datetime
from pathlib import Path


def run_migration(db_path: str = None):
    """
    Corrige les contraintes UNIQUE sur ufrs et programs.

    Args:
        db_path: Chemin vers le fichier .db. Si None, cherche automatiquement.
    """
    # ── Trouver la base de données ──────────────────────────────────────────
    if db_path is None:
        candidates = [
            "pfair_scheduler.db",
            "academic_scheduler.db",
            "database.db",
            "src/database/pfair_scheduler.db",
            "src/pfair_scheduler.db",
            "data/pfair_scheduler.db",
        ]
        for c in candidates:
            if Path(c).exists():
                db_path = c
                break
        if db_path is None:
            # Chercher récursivement
            for p in Path(".").rglob("*.db"):
                db_path = str(p)
                break
        if db_path is None:
            print("❌ Base de données introuvable. Passez le chemin en argument.")
            return False

    print(f"📂 Base de données : {db_path}")

    # ── Sauvegarde ──────────────────────────────────────────────────────────
    backup = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup)
    print(f"✅ Sauvegarde créée : {backup}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # désactiver le temps de la migration
    cursor = conn.cursor()

    try:
        # ── Vérifier la contrainte actuelle sur ufrs ─────────────────────────
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='ufrs'")
        row = cursor.fetchone()
        if not row:
            print("⚠️  Table 'ufrs' introuvable — migration non nécessaire ou base différente.")
            return False

        current_sql = row[0]
        print(f"\nSchéma actuel ufrs :\n{current_sql}\n")

        # ── Migrer la table ufrs ─────────────────────────────────────────────
        print("🔧 Migration de la table 'ufrs'...")
        cursor.executescript("""
            -- 1. Créer la nouvelle table avec la contrainte composite
            CREATE TABLE IF NOT EXISTS ufrs_new (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        VARCHAR(200) NOT NULL,
                code        VARCHAR(20)  NOT NULL,
                director    VARCHAR(200),
                university_id INTEGER NOT NULL,
                created_at  DATETIME,
                updated_at  DATETIME,
                FOREIGN KEY (university_id) REFERENCES universities(id),
                UNIQUE (code, university_id)
            );

            -- 2. Copier toutes les données existantes
            INSERT INTO ufrs_new
                SELECT id, name, code, director, university_id, created_at, updated_at
                FROM ufrs;

            -- 3. Supprimer l'ancienne table
            DROP TABLE ufrs;

            -- 4. Renommer la nouvelle
            ALTER TABLE ufrs_new RENAME TO ufrs;
        """)
        print("✅ Table 'ufrs' migrée — contrainte UNIQUE(code, university_id) appliquée.")

        # ── Migrer la table programs ─────────────────────────────────────────
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='programs'")
        row = cursor.fetchone()
        if row:
            print("\n🔧 Migration de la table 'programs'...")
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS programs_new (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    name           VARCHAR(200) NOT NULL,
                    code           VARCHAR(20)  NOT NULL,
                    level          VARCHAR(50),
                    duration_years INTEGER DEFAULT 1,
                    ufr_id         INTEGER NOT NULL,
                    created_at     DATETIME,
                    updated_at     DATETIME,
                    FOREIGN KEY (ufr_id) REFERENCES ufrs(id),
                    UNIQUE (code, ufr_id)
                );

                INSERT INTO programs_new
                    SELECT id, name, code, level, duration_years, ufr_id, created_at, updated_at
                    FROM programs;

                DROP TABLE programs;
                ALTER TABLE programs_new RENAME TO programs;
            """)
            print("✅ Table 'programs' migrée — contrainte UNIQUE(code, ufr_id) appliquée.")

        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

        print("\n🎉 Migration terminée avec succès !")
        print(f"   Vous pouvez supprimer la sauvegarde {backup} une fois l'application testée.")
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        # Restaurer la sauvegarde
        shutil.copy2(backup, db_path)
        print(f"\n❌ Erreur pendant la migration : {e}")
        print(f"   La base a été restaurée depuis {backup}.")
        return False


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    run_migration(path)