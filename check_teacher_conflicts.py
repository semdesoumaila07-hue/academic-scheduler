import sys; sys.path.insert(0,'.')
from src.database.db_manager import db_manager
db_manager.initialize()
s = db_manager.get_session()
from sqlalchemy import text
rows = s.execute(text("""
    SELECT ss.date, ss.start_time, t.full_name, 
           COUNT(*) as nb,
           GROUP_CONCAT(c.name) as cohortes,
           GROUP_CONCAT(a.name) as activites
    FROM schedule_slots ss
    LEFT JOIN teachers t ON t.id = ss.teacher_id
    LEFT JOIN cohorts c ON c.id = ss.cohort_id
    LEFT JOIN academic_activities a ON a.id = ss.activity_id
    WHERE ss.teacher_id IS NOT NULL
    GROUP BY ss.date, ss.start_time, ss.teacher_id
    HAVING COUNT(*) > 1
    ORDER BY ss.date
    LIMIT 20
""")).fetchall()
if rows:
    print(f"CONFLITS ENSEIGNANT DETECTES: {len(rows)}")
    for r in rows:
        print(f"  Date:{r[0]} Heure:{r[1]} Enseignant:{r[2]} Nb:{r[3]}")
        print(f"    Cohortes: {r[4]}")
        print(f"    Activites: {r[5]}")
else:
    print("Aucun conflit enseignant detecte!")