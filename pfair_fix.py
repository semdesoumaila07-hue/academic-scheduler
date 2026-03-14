import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')

path = r'src\services\pfair_scheduler.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. Ajouter import TeacherAvailabilityModel
content = content.replace(
    'from ..database.models import (\n    AcademicActivityModel, ScheduleSlotModel, TeacherModel,\n    CohortModel, ActivityStatusEnum\n)',
    'from ..database.models import (\n    AcademicActivityModel, ScheduleSlotModel, TeacherModel,\n    CohortModel, ActivityStatusEnum, TeacherAvailabilityModel\n)'
)

# 2. Remplacer la section attribution salle + verification disponibilite
old = '''                # V├®rifier disponibilit├® de l'enseignant
                teacher = self.teacher_repo.get_by_id(activity.teacher_id)
                if not teacher:
                    continue

                # Cr├®er un cr├®neau
                slot_start = time(hour=start_hour)
                slot_end = time(hour=start_hour + slot_duration)

                # V├®rifier les conflits
                if self.schedule_repo.check_conflict(
                    current_date, slot_start, slot_end,
                    teacher_id=teacher.id,
                    cohort_id=cohort_id
                ):
                    conflicts.append({
                        'date': current_date,
                        'activity': activity.name,
                        'reason': 'Conflit horaire'
                    })
                    continue

                # Assigner une salle disponible
                room = None
                if available_rooms:
                    available = self.schedule_repo.get_available_rooms(
                        current_date, slot_start, slot_end, available_rooms
                    )
                    if available:
                        room = available[0]'''

new = '''                # Recuperer l'enseignant
                teacher = self.teacher_repo.get_by_id(activity.teacher_id)
                if not teacher:
                    continue

                # Creer un creneau
                slot_start = time(hour=start_hour)
                slot_end = time(hour=start_hour + slot_duration)

                # AMELIORATION 2: Verifier disponibilite enseignant
                day_of_week = current_date.weekday()  # 0=lundi, 6=dimanche
                avail = self.session.query(TeacherAvailabilityModel).filter(
                    TeacherAvailabilityModel.teacher_id == teacher.id,
                    TeacherAvailabilityModel.day_of_week == day_of_week,
                    TeacherAvailabilityModel.start_time <= slot_start,
                    TeacherAvailabilityModel.end_time >= slot_end,
                    TeacherAvailabilityModel.period_start <= current_date,
                    TeacherAvailabilityModel.period_end >= current_date,
                ).first()
                # Si des disponibilites sont declarees et ce creneau n'en fait pas partie -> skip
                has_avail_declared = self.session.query(TeacherAvailabilityModel).filter(
                    TeacherAvailabilityModel.teacher_id == teacher.id
                ).count() > 0
                if has_avail_declared and not avail:
                    conflicts.append({
                        'date': current_date,
                        'activity': activity.name,
                        'reason': f'Enseignant {teacher.full_name} non disponible ce creneau'
                    })
                    continue

                # AMELIORATION 3: Verifier conflits inter-cohortes (meme enseignant)
                inter_conflict = self.session.query(ScheduleSlotModel).filter(
                    ScheduleSlotModel.teacher_id == teacher.id,
                    ScheduleSlotModel.date == current_date,
                    ScheduleSlotModel.start_time == slot_start,
                ).first()
                if inter_conflict:
                    conflicts.append({
                        'date': current_date,
                        'activity': activity.name,
                        'reason': f'Enseignant {teacher.full_name} deja occupe (cohorte {inter_conflict.cohort_id})'
                    })
                    continue

                # Verifier conflits intra-cohorte
                if self.schedule_repo.check_conflict(
                    current_date, slot_start, slot_end,
                    teacher_id=teacher.id,
                    cohort_id=cohort_id
                ):
                    conflicts.append({
                        'date': current_date,
                        'activity': activity.name,
                        'reason': 'Conflit horaire'
                    })
                    continue

                # AMELIORATION 1: Assigner salle compatible avec type activite
                room = None
                act_type = str(getattr(getattr(activity, 'type', None), 'value', None) or '').lower()
                # Mapping type activite -> type salle prefere
                type_map = {
                    'cours magistral': ['AMPHI', 'TD'],
                    'travaux diriges': ['TD', 'AMPHI'],
                    'travaux pratiques': ['TP', 'LABO', 'INFORMATIQUE'],
                    'td': ['TD', 'AMPHI'],
                    'tp': ['TP', 'LABO', 'INFORMATIQUE'],
                    'cm': ['AMPHI', 'TD'],
                }
                preferred_types = None
                for key, types in type_map.items():
                    if key in act_type:
                        preferred_types = types
                        break

                if available_rooms:
                    # Chercher salle compatible
                    from sqlalchemy import text
                    for ptype in (preferred_types or ['TD', 'AMPHI', 'TP', 'LABO', 'INFORMATIQUE', 'AUTRE']):
                        compatible = self.session.execute(text(
                            "SELECT name FROM rooms WHERE room_type=:rt AND is_active=1 AND name IN :names"
                            " AND name NOT IN (SELECT room FROM schedule_slots WHERE date=:d AND start_time=:st AND room IS NOT NULL)"
                        ), {'rt': ptype, 'names': tuple(available_rooms) if len(available_rooms)>1 else (available_rooms[0], available_rooms[0]), 'd': current_date, 'st': slot_start}).fetchall()
                        if compatible:
                            room = compatible[0][0]
                            break
                    # Fallback: salle quelconque disponible
                    if not room:
                        avail_rooms = self.schedule_repo.get_available_rooms(
                            current_date, slot_start, slot_end, available_rooms
                        )
                        if avail_rooms:
                            room = avail_rooms[0]

                # Verifier conflit salle inter-cohortes
                if room:
                    room_conflict = self.session.query(ScheduleSlotModel).filter(
                        ScheduleSlotModel.room == room,
                        ScheduleSlotModel.date == current_date,
                        ScheduleSlotModel.start_time == slot_start,
                    ).first()
                    if room_conflict:
                        room = None  # Liberer la salle conflictuelle'''

if old in content:
    content = content.replace(old, new)
    print("OK ameliorations appliquees!")
else:
    print("Bloc non trouve - recherche alternative...")
    idx = content.find("V├®rifier disponibilit├® de l'enseignant")
    if idx == -1:
        idx = content.find("teacher = self.teacher_repo.get_by_id")
    print(f"Position trouvee: {idx}")
    print(repr(content[idx:idx+200]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

import py_compile
try:
    py_compile.compile(path, doraise=True)
    print("OK syntaxe correcte!")
except py_compile.PyCompileError as e:
    print(f"Erreur: {e}")