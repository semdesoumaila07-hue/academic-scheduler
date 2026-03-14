"""
MIGRATION — Élargir la contrainte semester dans la table cohorts
================================================================
SQLite ne supporte pas ALTER COLUMN, donc on recrée la table.

Lancez CE SCRIPT UNE SEULE FOIS depuis la racine du projet :
    python migrer_semester.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/university.db")

if not DB_PATH.exists():
    # Chercher d'autres noms possibles
    for name in ["database.db", "app.db", "pfair.db", "data/app.db", "data/database.db"]:
        if Path(name).exists():
            DB_PATH = Path(name)
            break

print(f"Base de données : {DB_PATH}")
assert DB_PATH.exists(), f"❌ Base introuvable : {DB_PATH}"

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

print("\n═══════════════════════════════════════")
print("  MIGRATION : contrainte semester")
print("═══════════════════════════════════════")

# ── Vérifier la contrainte actuelle ──────────────────────────────
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cohorts'")
row = cur.fetchone()
if not row:
    print("❌ Table 'cohorts' introuvable !")
    conn.close()
    exit(1)

current_ddl = row[0]
print(f"\nDDL actuel :\n{current_ddl}\n")

if "CHECK (semester IN (1, 2))" not in current_ddl:
    print("✅ Contrainte déjà correcte ou absente — aucune migration nécessaire.")
    conn.close()
    exit(0)

print("⚠️  Contrainte restrictive détectée : CHECK (semester IN (1, 2))")
print("→  Migration vers : semester INTEGER NOT NULL (1-13)\n")

# ── Récupérer les données existantes ─────────────────────────────
cur.execute("SELECT * FROM cohorts")
rows = cur.fetchall()
cur.execute("PRAGMA table_info(cohorts)")
cols_info = cur.fetchall()
col_names = [c[1] for c in cols_info]
print(f"Colonnes : {col_names}")
print(f"Lignes à migrer : {len(rows)}")

# ── Recréer la table sans la contrainte restrictive ──────────────
new_ddl = """CREATE TABLE IF NOT EXISTS cohorts_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    semester INTEGER NOT NULL,
    student_count INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
)"""

cur.execute("DROP TABLE IF EXISTS cohorts_new")
cur.execute(new_ddl)
print("✅ Table cohorts_new créée")

# ── Copier les données ───────────────────────────────────────────
placeholders = ", ".join(["?" for _ in col_names])
cols_str = ", ".join(col_names)
for row in rows:
    cur.execute(
        f"INSERT INTO cohorts_new ({cols_str}) VALUES ({placeholders})",
        row
    )
print(f"✅ {len(rows)} ligne(s) copiée(s)")

# ── Renommer les tables ──────────────────────────────────────────
cur.execute("DROP TABLE cohorts")
cur.execute("ALTER TABLE cohorts_new RENAME TO cohorts")
print("✅ Table renommée")

# ── Recréer les index ────────────────────────────────────────────
for idx_sql in [
    "CREATE INDEX IF NOT EXISTS idx_cohorts_program ON cohorts(program_id)",
    "CREATE INDEX IF NOT EXISTS idx_cohorts_academic_year ON cohorts(academic_year)",
    "CREATE INDEX IF NOT EXISTS idx_cohorts_dates ON cohorts(start_date, end_date)",
]:
    cur.execute(idx_sql)
print("✅ Index recréés")

conn.commit()
conn.close()

print("\n═══════════════════════════════════════")
print("  ✅ MIGRATION TERMINÉE")
print("═══════════════════════════════════════")
print("""
Semestres maintenant acceptés :
  1→Semestre 1   2→Semestre 2
  3→Semestre 3   4→Semestre 4
  5→Semestre 5   6→Semestre 6
  7→M1           8→M2
  9→M3           10→M4
  11→Doctorat 1  12→Doctorat 2  13→Doctorat 3

Lancez maintenant : python main.py
""")