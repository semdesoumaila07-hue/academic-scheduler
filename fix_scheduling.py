import sys; sys.path.insert(0,'.')
path = r'src\ui\tabs\scheduling_tab.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Trouver la ligne avec rotation simple
for i,l in enumerate(lines):
    if 'available_rooms[len(scheduled_slots)' in l:
        print(f"Ligne {i+1}: {repr(l)}")
        # Remplacer par verification conflit salle
        lines[i] = '''                    # AMELIORATION 1: Salle compatible + pas de conflit inter-cohortes
                    room = "Salle TBD"
                    act_type_val = str(getattr(getattr(act, 'type', None), 'value', None) or '').lower()
                    type_map = {
                        'magistral': ['AMPHI', 'TD'], 'dirige': ['TD', 'AMPHI'],
                        'pratique': ['TP', 'LABO', 'INFORMATIQUE'],
                        'td': ['TD', 'AMPHI'], 'tp': ['TP', 'LABO', 'INFORMATIQUE'],
                        'cm': ['AMPHI', 'TD'],
                    }
                    preferred = next((v for k,v in type_map.items() if k in act_type_val), None)
                    slot_start_str = f"{start_hour:02d}:00:00.000000"
                    current_date_str = str(current_date)
                    if self.available_rooms:
                        from src.database.db_manager import db_manager as _dm
                        from sqlalchemy import text as _t
                        _s = _dm.get_session()
                        # Salles occupees a ce creneau (toutes cohortes)
                        occupied = set(r[0] for r in _s.execute(_t(
                            "SELECT room FROM schedule_slots WHERE date=:d AND start_time=:st AND room IS NOT NULL"
                        ), {'d': current_date_str, 'st': slot_start_str}).fetchall())
                        free_rooms = [r for r in self.available_rooms if r not in occupied]
                        if free_rooms:
                            # Choisir salle compatible avec type activite
                            if preferred:
                                from src.database.db_manager import db_manager as _dm2
                                from sqlalchemy import text as _t2
                                _s2 = _dm2.get_session()
                                for ptype in preferred:
                                    names = tuple(free_rooms) if len(free_rooms)>1 else (free_rooms[0], free_rooms[0])
                                    rows = _s2.execute(_t2(
                                        "SELECT name FROM rooms WHERE room_type=:rt AND is_active=1 AND name IN :names"
                                    ), {'rt': ptype, 'names': names}).fetchall()
                                    if rows:
                                        room = rows[0][0]; break
                            if room == "Salle TBD" and free_rooms:
                                room = free_rooms[0]
                        else:
                            # Aucune salle libre -> conflit
                            conflicts.append({'date': current_date, 'activity': act.name,
                                'reason': f'Aucune salle libre a {start_hour}h'})
                            continue
'''
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("OK!")

import py_compile
try:
    py_compile.compile(path, doraise=True)
    print("Syntaxe OK!")
except py_compile.PyCompileError as e:
    print(f"Erreur: {e}")