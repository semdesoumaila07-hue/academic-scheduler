import os
BASE = r'C:\Eclipse\academic-scheduler'

# 1. Ajouter RoomsTab dans main_window.py
main_path = os.path.join(BASE, 'src', 'ui', 'main_window.py')
with open(main_path, encoding='utf-8') as f:
    mw = f.read()

if 'RoomsTab' not in mw:
    mw = mw.replace(
        'from .tabs import (\n    DashboardTab, StructureTab, TeachersTab, ActivitiesTab,\n    CalendarTab, SchedulingTab, AnalysisTab, LeavesTab,\n    ReportsTab, TimetableTab, AvailabilityTab, UsersTab,\n)',
        'from .tabs import (\n    DashboardTab, StructureTab, TeachersTab, ActivitiesTab,\n    CalendarTab, SchedulingTab, AnalysisTab, LeavesTab,\n    ReportsTab, TimetableTab, AvailabilityTab, UsersTab, RoomsTab,\n)'
    )
    mw = mw.replace(
        '    AvailabilityTab, UsersTab,\n]',
        '    AvailabilityTab, UsersTab, RoomsTab,\n]'
    )
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(mw)
    print("OK main_window.py mis a jour")
else:
    print("main_window.py deja ok")

# 2. Ajouter dans permissions_config.py
perm_path = os.path.join(BASE, 'src', 'services', 'permissions_config.py')
with open(perm_path, encoding='utf-8') as f:
    pc = f.read()

if 'manage_rooms' not in pc:
    pc = pc.replace(
        "    (11, 'manage_users', '",
        "    (12, 'manage_rooms', '🏢', 'Salles'),\n    (11, 'manage_users', '"
    )
    with open(perm_path, 'w', encoding='utf-8') as f:
        f.write(pc)
    print("OK permissions_config.py mis a jour")
else:
    print("permissions_config.py deja ok")

# 3. Ajouter index 12 dans ROLE_ALLOWED de app_window.py
app_path = os.path.join(BASE, 'src', 'ui', 'app_window.py')
with open(app_path, encoding='utf-8') as f:
    aw = f.read()

if '12' not in aw:
    aw = aw.replace(
        "'admin':       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],   # tout",
        "'admin':       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],   # tout"
    )
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(aw)
    print("OK app_window.py mis a jour")
else:
    print("app_window.py deja ok")

print("\nDone! Lancez: python main.py")