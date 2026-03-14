import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')

path = r'src\services\pfair_scheduler.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Remplacer lignes 163-192 (index 162-191) par le nouveau code ameliore
new_lines = [
    "                # Recuperer l'enseignant\n",
    "                teacher = self.teacher_repo.get_by_id(activity.teacher_id)\n",
    "                if not teacher:\n",
    "                    continue\n",
    "\n",
    "                # Creer le creneau\n",
    "                slot_start = time(hour=start_hour)\n",
    "                slot_end = time(hour=start_hour + slot_duration)\n",
    "\n",
    "                # AMELIORATION 2: Verifier disponibilite enseignant\n",
    "                day_of_week = current_date.weekday()\n",
    "                has_avail = self.session.query(TeacherAvailabilityModel).filter(\n",
    "                    TeacherAvailabilityModel.teacher_id == teacher.id\n",
    "                ).count() > 0\n",
    "                if has_avail:\n",
    "                    avail_ok = self.session.query(TeacherAvailabilityModel).filter(\n",
    "                        TeacherAvailabilityModel.teacher_id == teacher.id,\n",
    "                        TeacherAvailabilityModel.day_of_week == day_of_week,\n",
    "                        TeacherAvailabilityModel.start_time <= slot_start,\n",
    "                        TeacherAvailabilityModel.end_time >= slot_end,\n",
    "                        TeacherAvailabilityModel.period_start <= current_date,\n",
    "                        TeacherAvailabilityModel.period_end >= current_date,\n",
    "                    ).first()\n",
    "                    if not avail_ok:\n",
    "                        conflicts.append({'date': current_date, 'activity': activity.name,\n",
    "                            'reason': f'Enseignant {teacher.full_name} non disponible'})\n",
    "                        continue\n",
    "\n",
    "                # AMELIORATION 3: Conflits inter-cohortes (meme enseignant)\n",
    "                inter_conflict = self.session.query(ScheduleSlotModel).filter(\n",
    "                    ScheduleSlotModel.teacher_id == teacher.id,\n",
    "                    ScheduleSlotModel.date == current_date,\n",
    "                    ScheduleSlotModel.start_time == slot_start,\n",
    "                ).first()\n",
    "                if inter_conflict and inter_conflict.cohort_id != cohort_id:\n",
    "                    conflicts.append({'date': current_date, 'activity': activity.name,\n",
    "                        'reason': f'Enseignant occupe par cohorte {inter_conflict.cohort_id}'})\n",
    "                    continue\n",
    "\n",
    "                # Verifier conflits intra-cohorte\n",
    "                if self.schedule_repo.check_conflict(\n",
    "                    current_date, slot_start, slot_end,\n",
    "                    teacher_id=teacher.id, cohort_id=cohort_id\n",
    "                ):\n",
    "                    conflicts.append({'date': current_date, 'activity': activity.name,\n",
    "                        'reason': 'Conflit horaire'})\n",
    "                    continue\n",
    "\n",
    "                # AMELIORATION 1: Salle compatible avec type activite\n",
    "                room = None\n",
    "                act_type = str(getattr(getattr(activity, 'type', None), 'value', None) or '').lower()\n",
    "                type_map = {\n",
    "                    'magistral': ['AMPHI', 'TD'],\n",
    "                    'dirige': ['TD', 'AMPHI'],\n",
    "                    'pratique': ['TP', 'LABO', 'INFORMATIQUE'],\n",
    "                    'td': ['TD', 'AMPHI'],\n",
    "                    'tp': ['TP', 'LABO', 'INFORMATIQUE'],\n",
    "                    'cm': ['AMPHI', 'TD'],\n",
    "                }\n",
    "                preferred = None\n",
    "                for key, types in type_map.items():\n",
    "                    if key in act_type:\n",
    "                        preferred = types\n",
    "                        break\n",
    "                if available_rooms:\n",
    "                    from sqlalchemy import text as sqlt\n",
    "                    for ptype in (preferred or ['AMPHI','TD','TP','LABO','INFORMATIQUE','AUTRE']):\n",
    "                        names = tuple(available_rooms) if len(available_rooms)>1 else (available_rooms[0], available_rooms[0])\n",
    "                        rows = self.session.execute(sqlt(\n",
    "                            'SELECT name FROM rooms WHERE room_type=:rt AND is_active=1'\n",
    "                            ' AND name IN :names'\n",
    "                            ' AND name NOT IN (SELECT room FROM schedule_slots WHERE date=:d AND start_time=:st AND room IS NOT NULL)'\n",
    "                        ), {'rt': ptype, 'names': names, 'd': str(current_date), 'st': str(slot_start)}).fetchall()\n",
    "                        if rows:\n",
    "                            room = rows[0][0]; break\n",
    "                    if not room:\n",
    "                        avail_r = self.schedule_repo.get_available_rooms(current_date, slot_start, slot_end, available_rooms)\n",
    "                        if avail_r: room = avail_r[0]\n",
    "                # Verifier conflit salle inter-cohortes\n",
    "                if room:\n",
    "                    rc = self.session.query(ScheduleSlotModel).filter(\n",
    "                        ScheduleSlotModel.room == room,\n",
    "                        ScheduleSlotModel.date == current_date,\n",
    "                        ScheduleSlotModel.start_time == slot_start,\n",
    "                    ).first()\n",
    "                    if rc: room = None\n",
    "\n",
]

# Remplacer lignes 162 a 192 (index)
lines = lines[:162] + new_lines + lines[192:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("OK remplace!")

# Ajouter import TeacherAvailabilityModel
with open(path, encoding='utf-8') as f:
    content = f.read()
if 'TeacherAvailabilityModel' not in content:
    content = content.replace(
        'from ..database.models import (\n    AcademicActivityModel, ScheduleSlotModel, TeacherModel,\n    CohortModel, ActivityStatusEnum\n)',
        'from ..database.models import (\n    AcademicActivityModel, ScheduleSlotModel, TeacherModel,\n    CohortModel, ActivityStatusEnum, TeacherAvailabilityModel\n)'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK import ajoute!")

import py_compile
try:
    py_compile.compile(path, doraise=True)
    print("OK syntaxe correcte!")
except py_compile.PyCompileError as e:
    print(f"Erreur syntaxe: {e}")
    import re
    m = re.search(r'line (\d+)', str(e))
    if m:
        ln = int(m.group(1))
        with open(path, encoding='utf-8') as f:
            ls = f.readlines()
        for j in range(max(0,ln-3), min(len(ls),ln+3)):
            print(f"  {j+1}: {repr(ls[j])}")