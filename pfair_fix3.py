import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')

path = r'src\services\pfair_scheduler.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Afficher lignes 160-200 pour voir le bloc exact
for i in range(159, 205):
    print(f"{i+1}: {repr(lines[i])}")