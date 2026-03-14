import os, sys
sys.path.insert(0, r'C:\Eclipse\academic-scheduler')
os.chdir(r'C:\Eclipse\academic-scheduler')
BASE = r'C:\Eclipse\academic-scheduler'

# Ajouter dans __init__.py
init_path = os.path.join(BASE, 'src', 'ui', 'tabs', '__init__.py')
with open(init_path, encoding='utf-8') as f:
    init = f.read()
if 'RoomsTab' not in init:
    with open(init_path, 'a', encoding='utf-8') as f:
        f.write('\nfrom .rooms_tab import RoomsTab\n')
    print("OK __init__.py mis a jour")
else:
    print("__init__.py deja ok")

# Ajouter dans main_window.py
main_path = os.path.join(BASE, 'src', 'ui', 'main_window.py')
with open(main_path, encoding='utf-8') as f:
    mw = f.read()
if 'RoomsTab' not in mw:
    mw = mw.replace('from src.ui.tabs.reports_tab import ReportsTab',
                     'from src.ui.tabs.reports_tab import ReportsTab\nfrom src.ui.tabs.rooms_tab import RoomsTab')
    mw = mw.replace("self.tabs.addTab(self.reports_tab",
                     "self.rooms_tab = RoomsTab(current_user=self.current_user)\n        self.tabs.addTab(self.rooms_tab, 'Salles')\n        self.tabs.addTab(self.reports_tab")
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(mw)
    print("OK main_window.py mis a jour")
else:
    print("main_window.py deja ok")

print("Partie 2 OK - lancez rooms_p3.py")