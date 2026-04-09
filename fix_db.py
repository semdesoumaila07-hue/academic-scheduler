"""
fix_db.py — Corrige la contrainte UNIQUE sur ufrs.code et programs.code
Lancez ce script UNE SEULE FOIS depuis le dossier racine du projet.
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# ── Trouver la base automatiquement ─────────────────────────────────────────
db_path = None
for pattern in ["*.db", "**/*.db"]:
    found = list(Path(".").glob(pattern))
    if found:
        db_path = str(found[0])
        break

if db_path is None:
    print("Base introuvable. Modifiez db_path manuellement.")
    db_path = "pfair_scheduler.db"  # ← changez si nécessaire

print(f"Base trouvée : {db_path}")

# ── Sauvegarde ───────────────────────────────────────────────────────────────
backup = db_path + ".backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(db_path, backup)
print(f"Sauvegarde : {backup}")

# ── Migration ────────────────────────────────────────────────────────────────
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = OFF")

try:
    # Vérifier si la contrainte est déjà correcte
    cur = conn.execute("SELECT sql FROM sqlite_master WHERE name='ufrs'")
    sql = cur.fetchone()[0]
    
    if "university_id" in sql and "UNIQUE" in sql and "code" in sql.split("university_id")[1]:
        print("✅ La contrainte ufrs est déjà correcte, rien à faire.")
    else:
        print("🔧 Correction de ufrs...")
        conn.executescript("""
            CREATE TABLE ufrs_new (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          VARCHAR(200) NOT NULL,
                code          VARCHAR(20)  NOT NULL,
                director      VARCHAR(200),
                university_id INTEGER NOT NULL REFERENCES universities(id),
                created_at    DATETIME,
                updated_at    DATETIME,
                UNIQUE(code, university_id)
            );
            INSERT INTO ufrs_new SELECT id,name,code,director,university_id,created_at,updated_at FROM ufrs;
            DROP TABLE ufrs;
            ALTER TABLE ufrs_new RENAME TO ufrs;
        """)
        print("✅ ufrs corrigé : UNIQUE(code, university_id)")

    # Même chose pour programs
    cur = conn.execute("SELECT sql FROM sqlite_master WHERE name='programs'")
    row = cur.fetchone()
    if row:
        sql2 = row[0]
        if "ufr_id" in sql2 and "UNIQUE" in sql2 and "code" in sql2.split("ufr_id")[1]:
            print("✅ La contrainte programs est déjà correcte.")
        else:
            print("🔧 Correction de programs...")
            conn.executescript("""
                CREATE TABLE programs_new (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    name           VARCHAR(200) NOT NULL,
                    code           VARCHAR(20)  NOT NULL,
                    level          VARCHAR(50),
                    duration_years INTEGER DEFAULT 1,
                    ufr_id         INTEGER NOT NULL REFERENCES ufrs(id),
                    created_at     DATETIME,
                    updated_at     DATETIME,
                    UNIQUE(code, ufr_id)
                );
                INSERT INTO programs_new SELECT id,name,code,level,duration_years,ufr_id,created_at,updated_at FROM programs;
                DROP TABLE programs;
                ALTER TABLE programs_new RENAME TO programs;
            """)
            print("✅ programs corrigé : UNIQUE(code, ufr_id)")

    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()
    print("\n🎉 Migration réussie ! Vous pouvez relancer l'application.")

except Exception as e:
    conn.rollback()
    conn.close()
    shutil.copy2(backup, db_path)
    print(f"\n❌ Erreur : {e}")
    print(f"Base restaurée depuis {backup}")