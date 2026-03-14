import sys; sys.path.insert(0,'.')
from src.database.db_manager import db_manager
db_manager.initialize()
s = db_manager.get_session()
from sqlalchemy import text
rows = s.execute(text("""
    SELECT date, start_time, room, COUNT(*) as nb,
           GROUP_CONCAT(cohort_id) as cohortes
    FROM schedule_slots 
    WHERE room IS NOT NULL AND room != ''
    GROUP BY date, start_time, room 
    HAVING COUNT(*) > 1
    ORDER BY date
    LIMIT 10
""")).fetchall()
if rows:
    print(f"CONFLITS DETECTES: {len(rows)}")
    for r in rows:
        print(f"  Date:{r[0]} Heure:{r[1]} Salle:{r[2]} Nb:{r[3]} Cohortes:{r[4]}")
else:
    print("Aucun conflit de salle detecte")