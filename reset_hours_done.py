"""
Script de correction : remet hours_done = 0 pour toutes les activités
dont hours_done >= volume_hours (marquées à tort comme terminées).

Usage (à la racine du projet) : python reset_hours_done.py
"""
import sys, os

# ── Ajouter la racine du projet au PYTHONPATH ────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

try:
    from src.database.db_manager import db_manager
    from src.database.models import AcademicActivityModel

    # ── Initialiser la DB (obligatoire avant get_session) ────────
    db_manager.initialize()
    db_manager.create_tables()

    session = db_manager.get_session()

    activities = session.query(AcademicActivityModel).all()
    print(f"\n{'='*60}")
    print(f"  Activités trouvées : {len(activities)}")
    print(f"{'='*60}")

    reset_count = 0
    for act in activities:
        h = float(act.hours_done or 0)
        v = float(act.volume_hours or 0)
        flag = "⚠️  BLOQUÉE" if h >= v and v > 0 else "✅ OK"
        print(f"  [{act.id}] {act.name[:30]:<30} {h:5.1f}h / {v:5.1f}h  {flag}")

        if h >= v and v > 0:
            act.hours_done = 0.0
            reset_count += 1

    if reset_count > 0:
        session.commit()
        print(f"\n✅ {reset_count} activité(s) remise(s) à 0h.")
        print("   → Remplacez scheduling_tab.py puis relancez l'application.\n")
    else:
        print(f"\n⚠️  Aucune activité bloquée (hours_done < volume_hours pour toutes).")
        print("   → Le bug vient peut-être de charge_factor = 0 ou teacher_id = NULL.")
        print("   → Vérifiez l'onglet Activités : l'activité a-t-elle un enseignant ?\n")

    print(f"{'='*60}\n")

except Exception as e:
    import traceback
    print(f"\n❌ Erreur : {e}")
    traceback.print_exc()