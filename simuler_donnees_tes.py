"""
SCRIPT DE SIMULATION COMPLÈTE — VERSION CORRIGÉE
=================================================
Lance depuis la racine du projet :
    python simuler_donnees_test.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, time, timedelta

from src.database.db_manager import db_manager
from src.database.models import (
    UniversityModel, UFRModel, ProgramModel, CohortModel,
    TeacherModel, AcademicActivityModel, TeacherAvailabilityModel,
    RoleModel, UserModel, PermissionModel,
    ProgramLevelEnum, TeacherStatusEnum,
    ActivityTypeEnum, ActivityStatusEnum, PriorityEnum
)

def ligne(t): print(f"\n{'═'*60}\n  {t}\n{'═'*60}")
def ok(m):    print(f"  ✅ {m}")
def info(m):  print(f"  ℹ️  {m}")
def err(m):   print(f"  ❌ {m}")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 — Connexion
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 1 — Connexion SQLite")
try:
    db_manager.initialize()
    db_manager.create_tables()
    session = db_manager.get_session()
    ok("Base de données prête")
except Exception as e:
    err(f"Connexion impossible : {e}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 — Créer un utilisateur Admin avec toutes les permissions
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 2 — Utilisateur Admin avec toutes les permissions")

TOUTES_PERMISSIONS = [
    'view_dashboard', 'manage_structure', 'manage_teachers',
    'manage_activities', 'manage_calendar', 'approve_leave',
    'launch_scheduling', 'analyze_delays', 'generate_reports',
    'view_timetable', 'declare_availability', 'submit_leave',
]

try:
    # Créer les permissions si absentes
    perms = {}
    for nom in TOUTES_PERMISSIONS:
        p = session.query(PermissionModel).filter_by(name=nom).first()
        if not p:
            p = PermissionModel(name=nom, description=f"Permission {nom}")
            session.add(p)
        perms[nom] = p
    session.commit()
    ok(f"{len(perms)} permissions vérifiées")

    # Rôle Admin
    role_admin = session.query(RoleModel).filter_by(name='Admin').first()
    if not role_admin:
        role_admin = RoleModel(name='Admin', description='Administrateur système')
        session.add(role_admin)
        session.commit()
    for p in perms.values():
        if p not in role_admin.permissions:
            role_admin.permissions.append(p)
    session.commit()
    ok(f"Rôle Admin → {len(role_admin.permissions)} permissions")

    # Utilisateur admin
    from src.utils.passwords import hash_password
    admin_user = session.query(UserModel).filter_by(username='admin').first()
    if not admin_user:
        admin_user = UserModel(
            username='admin',
            email='admin@ujkz.bf',
            password_hash=hash_password('admin123'),
            is_active=True
        )
        session.add(admin_user)
        session.commit()
        ok("Utilisateur admin créé  (login: admin / admin123)")
    else:
        ok("Utilisateur admin existant")

    if role_admin not in admin_user.roles:
        admin_user.roles.append(role_admin)
        session.commit()

    session.refresh(admin_user)
    CURRENT_USER = admin_user
    ok(f"Permissions actives : {[p.name for r in CURRENT_USER.roles for p in r.permissions]}")

except Exception as e:
    session.rollback()
    err(f"Erreur admin : {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 — Université
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 3 — Université")
try:
    univ = session.query(UniversityModel).filter_by(code="UJKZ").first()
    if not univ:
        univ = UniversityModel(
            name="Université Joseph KI-ZERBO", code="UJKZ",
            address="03 BP 7021", city="Ouagadougou", country="Burkina Faso"
        )
        session.add(univ); session.commit()
        ok(f"Créée → ID={univ.id}")
    else:
        ok(f"Existante → ID={univ.id}")
    info(f"{univ.name}")
except Exception as e:
    session.rollback(); err(str(e)); sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4 — UFR
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 4 — UFR")
try:
    ufr = session.query(UFRModel).filter_by(code="UFR-ST").first()
    if not ufr:
        ufr = UFRModel(
            name="UFR Sciences et Technologies", code="UFR-ST",
            director="Prof. Moussa OUEDRAOGO", university_id=univ.id
        )
        session.add(ufr); session.commit()
        ok(f"Créée → ID={ufr.id}")
    else:
        ok(f"Existante → ID={ufr.id}")
    info(f"{ufr.name}")
except Exception as e:
    session.rollback(); err(str(e)); sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 — Programme
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 5 — Programme")
try:
    prog = session.query(ProgramModel).filter_by(code="L3-INFO").first()
    if not prog:
        prog = ProgramModel(
            name="Licence 3 Informatique", code="L3-INFO",
            level=ProgramLevelEnum.LICENCE_3, duration_years=3, ufr_id=ufr.id
        )
        session.add(prog); session.commit()
        ok(f"Créé → ID={prog.id}")
    else:
        ok(f"Existant → ID={prog.id}")
    info(f"{prog.name}")
except Exception as e:
    session.rollback(); err(str(e)); sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 6 — Cohorte
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 6 — Cohorte")
DEBUT = date(2025, 9, 15)
FIN   = date(2026, 1, 31)
try:
    cohorte = session.query(CohortModel).filter_by(
        name="L3-INFO-A 2025-2026", program_id=prog.id
    ).first()
    if not cohorte:
        cohorte = CohortModel(
            name="L3-INFO-A 2025-2026", academic_year="2025-2026",
            semester=1, student_count=35, program_id=prog.id,
            start_date=DEBUT, end_date=FIN
        )
        session.add(cohorte); session.commit()
        ok(f"Créée → ID={cohorte.id}")
    else:
        ok(f"Existante → ID={cohorte.id}")
    info(f"{cohorte.name} — {DEBUT} → {FIN}")
except Exception as e:
    session.rollback(); err(str(e)); sys.exit(1)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 7 — Enseignants
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 7 — Enseignants")
ens_data = [
    dict(full_name="KABORE Marie",     email="marie.kabore@ujkz.bf",
         phone="+226 70 11 22 33", speciality="Algorithmique",
         status=TeacherStatusEnum.PERMANENT,  max_hours_per_week=20, ufr_id=ufr.id),
    dict(full_name="TRAORE Moussa",    email="moussa.traore@ujkz.bf",
         phone="+226 70 44 55 66", speciality="Bases de données",
         status=TeacherStatusEnum.PERMANENT,  max_hours_per_week=20, ufr_id=ufr.id),
    dict(full_name="SAWADOGO Aminata", email="aminata.sawadogo@ujkz.bf",
         phone="+226 70 77 88 99", speciality="Réseaux",
         status=TeacherStatusEnum.VACATAIRE,  max_hours_per_week=12, ufr_id=ufr.id),
]
enseignants = {}
for d in ens_data:
    try:
        t = session.query(TeacherModel).filter_by(email=d["email"]).first()
        if not t:
            t = TeacherModel(**d); session.add(t); session.commit()
            ok(f"Créé    → {t.full_name} (ID={t.id})")
        else:
            ok(f"Existant → {t.full_name} (ID={t.id})")
        enseignants[t.full_name] = t
    except Exception as e:
        session.rollback(); err(f"{d['full_name']} : {e}")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 8 — Disponibilités
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 8 — Disponibilités (Lun–Ven 08h–18h)")
for ens in enseignants.values():
    ex = session.query(TeacherAvailabilityModel).filter_by(teacher_id=ens.id).first()
    if not ex:
        for jour in range(5):
            session.add(TeacherAvailabilityModel(
                teacher_id=ens.id, day_of_week=jour,
                start_time=time(8, 0), end_time=time(18, 0),
                period_start=DEBUT, period_end=FIN
            ))
        session.commit()
        ok(f"Créées → {ens.full_name}")
    else:
        ok(f"Existantes → {ens.full_name}")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 9 — Activités
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 9 — Activités académiques")
jours_ouvres = sum(1 for i in range((FIN-DEBUT).days+1)
                   if (DEBUT+timedelta(i)).weekday() < 5)

t_k = enseignants.get("KABORE Marie")
t_t = enseignants.get("TRAORE Moussa")
t_s = enseignants.get("SAWADOGO Aminata")

act_data = [
    dict(name="Algorithmique Avancée",  code="ALGO-L3-CM", type=ActivityTypeEnum.COURS_MAGISTRAL, volume_hours=30.0, priority=PriorityEnum.HAUTE,   teacher_id=t_k.id if t_k else None),
    dict(name="TD Algorithmique",       code="ALGO-L3-TD", type=ActivityTypeEnum.TD,              volume_hours=15.0, priority=PriorityEnum.NORMALE, teacher_id=t_k.id if t_k else None),
    dict(name="Bases de Données",       code="BDD-L3-CM",  type=ActivityTypeEnum.COURS_MAGISTRAL, volume_hours=30.0, priority=PriorityEnum.HAUTE,   teacher_id=t_t.id if t_t else None),
    dict(name="TP Bases de Données",    code="BDD-L3-TP",  type=ActivityTypeEnum.TP,              volume_hours=20.0, priority=PriorityEnum.NORMALE, teacher_id=t_t.id if t_t else None),
    dict(name="Réseaux Informatiques",  code="RES-L3-CM",  type=ActivityTypeEnum.COURS_MAGISTRAL, volume_hours=25.0, priority=PriorityEnum.NORMALE, teacher_id=t_s.id if t_s else None),
    dict(name="TP Réseaux",             code="RES-L3-TP",  type=ActivityTypeEnum.TP,              volume_hours=15.0, priority=PriorityEnum.BASSE,   teacher_id=t_s.id if t_s else None),
]

activites = []
total_h = 0
for d in act_data:
    try:
        a = session.query(AcademicActivityModel).filter_by(code=d["code"]).first()
        if not a:
            charge = round(d["volume_hours"] / jours_ouvres, 6) if jours_ouvres else 0
            a = AcademicActivityModel(
                **d, cohort_id=cohorte.id,
                hours_done=0.0, charge_factor=charge,
                activation_date=DEBUT, deadline=FIN,
                status=ActivityStatusEnum.PENDING,
            )
            session.add(a); session.commit()
            ok(f"Créée → {a.name} ({a.volume_hours}h)")
        else:
            ok(f"Existante → {a.name} ({a.volume_hours}h)")
        activites.append(a); total_h += a.volume_hours
    except Exception as e:
        session.rollback(); err(f"{d['code']} : {e}")

info(f"Total : {total_h}h sur {jours_ouvres} jours ouvrés "
     f"= {total_h/jours_ouvres:.2f}h/jour")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 10 — Génération emploi du temps
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 10 — Génération emploi du temps (Pfair)")

EDT_DEBUT = DEBUT
EDT_FIN   = DEBUT + timedelta(weeks=4)
SALLES    = ["Amphi A", "Salle 101", "Salle 102", "Labo Info"]

info(f"Cohorte      : {cohorte.name} (ID={cohorte.id})")
info(f"Période EDT  : {EDT_DEBUT} → {EDT_FIN}")
info(f"Salles       : {', '.join(SALLES)}")
info(f"current_user : {CURRENT_USER.username} / rôle Admin")

try:
    from src.managers.schedule_generator import ScheduleGenerator
    generator = ScheduleGenerator(session)
    resultat  = generator.generate_schedule(
        cohort_id=cohorte.id,
        start_date=EDT_DEBUT,
        end_date=EDT_FIN,
        available_rooms=SALLES,
        replace_existing=True,
        current_user=CURRENT_USER    # ← admin avec launch_scheduling
    )

    if resultat.get("success"):
        slots = resultat.get("slots", resultat.get("schedule", []))
        ok(f"Emploi du temps généré ! ({len(slots)} créneaux)")

        print("\n  📅 APERÇU DES 10 PREMIERS CRÉNEAUX :")
        print("  " + "─"*60)
        print(f"  {'Date':<12} {'Heure':<15} {'Activité':<22} {'Salle'}")
        print("  " + "─"*60)
        for slot in slots[:10]:
            if hasattr(slot, 'date'):
                d   = str(slot.date)
                h   = f"{slot.start_time}–{slot.end_time}"
                act = (slot.activity.name[:20] if slot.activity else "?")
                sal = slot.room or "?"
            else:
                d   = str(slot.get("date", "?"))
                h   = f"{slot.get('start_time','?')}–{slot.get('end_time','?')}"
                act = slot.get("activity_name", slot.get("name", "?"))[:20]
                sal = slot.get("room", "?")
            print(f"  {d:<12} {h:<15} {act:<22} {sal}")
        if len(slots) > 10:
            print(f"  ... et {len(slots)-10} créneaux de plus")
        print("  " + "─"*60)
    else:
        err(f"Échec : {resultat.get('error', '?')}")
        for k, v in resultat.items():
            print(f"    {k}: {v}")

except Exception as e:
    err(f"Exception : {e}")
    import traceback; traceback.print_exc()


# ══════════════════════════════════════════════════════════════
# ÉTAPE 11 — Dashboard
# ══════════════════════════════════════════════════════════════
ligne("ÉTAPE 11 — Vérification Dashboard")
try:
    from src.services.dashboard_service import DashboardService
    data = DashboardService(session).get_dashboard_data()
    print("\n  📊 KPIs :")
    for kpi in data.get("kpis", []):
        print(f"    {kpi['icon']}  {kpi['label']:<25} → {kpi['value']}")
    print(f"\n  ⏳ Progression : {data.get('completion_percentage', 0):.1f}%")
    ok("Dashboard alimenté depuis SQLite")
except Exception as e:
    err(f"Dashboard : {e}")


# ══════════════════════════════════════════════════════════════
# RÉSUMÉ
# ══════════════════════════════════════════════════════════════
ligne("RÉSUMÉ FINAL")
print(f"""
  🏛️  Université : {univ.name}
  🎓  UFR        : {ufr.name}
  📚  Programme  : {prog.name}
  👥  Cohorte    : {cohorte.name} ({cohorte.student_count} étudiants)
  👨‍🏫  Enseignants : {len(enseignants)}
  📋  Activités  : {len(activites)} ({total_h}h)
  🔑  Connexion  : admin / admin123

  ▶️  Lancez maintenant :  python main.py
      → Connectez-vous avec  admin / admin123
      → Tous les onglets seront accessibles
      → L'emploi du temps sera visible dans "Emplois du temps"
""")
session.close()
print("═"*60)
print("  ✅  SIMULATION TERMINÉE AVEC SUCCÈS")
print("═"*60)