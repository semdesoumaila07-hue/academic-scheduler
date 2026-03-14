"""
Script pour convertir les dates DD/MM/YYYY en YYYY-MM-DD dans la base
"""
import sqlite3
from datetime import datetime
import sys
import os

# Trouver la base de données
possible_paths = [
    'data/ordonnancement.db',
    'ordonnancement.db',
    'academic_scheduler.db',
    'data/academic_scheduler.db',
    'instance/academic_scheduler.db'
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ Base de données non trouvée !")
    sys.exit(1)

print(f"✅ Base trouvée : {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Récupérer toutes les cohortes
cursor.execute("SELECT id, start_date, end_date FROM cohorts")
cohorts = cursor.fetchall()

print(f"\n🔄 Conversion de {len(cohorts)} cohorte(s)...")

for cohort_id, start_date, end_date in cohorts:
    try:
        # Essayer de parser les dates
        if start_date and '/' in start_date:
            # Format français DD/MM/YYYY
            start_obj = datetime.strptime(start_date, "%d/%m/%Y")
            start_iso = start_obj.strftime("%Y-%m-%d")
        else:
            start_iso = start_date
        
        if end_date and '/' in end_date:
            end_obj = datetime.strptime(end_date, "%d/%m/%Y")
            end_iso = end_obj.strftime("%Y-%m-%d")
        else:
            end_iso = end_date
        
        # Mettre à jour
        cursor.execute(
            "UPDATE cohorts SET start_date = ?, end_date = ? WHERE id = ?",
            (start_iso, end_iso, cohort_id)
        )
        
        print(f"  ✅ Cohorte {cohort_id}: {start_date} → {start_iso}")
    
    except Exception as e:
        print(f"  ⚠️ Erreur cohorte {cohort_id}: {e}")

conn.commit()
conn.close()

print("\n✅ Conversion terminée ! Relancez l'application.")
