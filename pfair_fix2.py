import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')

path = r'src\services\pfair_scheduler.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Afficher lignes autour de la position 5979
for i, line in enumerate(lines):
    if 'teacher_repo.get_by_id' in line or 'Verifier disponib' in line or 'check_conflict' in line or 'available_rooms' in line and 'available =' in line:
        print(f"{i+1}: {repr(line)}")