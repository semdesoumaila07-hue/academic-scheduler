"""
Migration : ajout des colonnes tâches sporadiques sur academic_activities.

À exécuter une seule fois :
    python migrate_sporadic.py

Les colonnes ajoutées :
    - is_sporadic      BOOLEAN DEFAULT 0
    - arrival_date     DATE
    - execution_window INTEGER
"""
import sqlite3
import os
import sys

DB_PATH = os.path.join("data", "ordonnancement.db")

def run():
    if not os.path.exists(DB_PATH):
        print(f"Base de données introuvable : {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Vérifier les colonnes existantes
    cur.execute("PRAGMA table_info(academic_activities)")
    existing = {row[1] for row in cur.fetchall()}

    migrations = [
        ("is_sporadic",      "ALTER TABLE academic_activities ADD COLUMN is_sporadic BOOLEAN DEFAULT 0"),
        ("arrival_date",     "ALTER TABLE academic_activities ADD COLUMN arrival_date DATE"),
        ("execution_window", "ALTER TABLE academic_activities ADD COLUMN execution_window INTEGER"),
    ]

    for col, sql in migrations:
        if col not in existing:
            cur.execute(sql)
            print(f"  + Colonne ajoutée : {col}")
        else:
            print(f"  = Colonne déjà présente : {col}")

    conn.commit()
    conn.close()
    print("\nMigration terminée.")

if __name__ == "__main__":
    run()