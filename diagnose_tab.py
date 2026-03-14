"""
Diagnostic : vérifie que current_user est bien passé à StructureTab
et teste add_programme directement.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db_manager import db_manager
db_manager.initialize()
db_manager.create_tables()
session = db_manager.get_session()

from src.database.models import UserModel
admin = session.query(UserModel).filter(UserModel.username == 'ism').first()
if not admin:
    admin = session.query(UserModel).first()

print(f"Utilisateur : {admin.username}")
print(f"current_user is None : {admin is None}")

# Simuler exactement ce que fait main_window ligne 218
import sys as _sys
from PyQt5.QtWidgets import QApplication
_app = QApplication.instance() or QApplication(_sys.argv)

from src.ui.tabs.structure_tab import StructureTab
tab = StructureTab(current_user=admin)

print(f"\ntab.current_user : {tab.current_user}")
print(f"tab.current_user is None : {tab.current_user is None}")
if tab.current_user:
    for r in tab.current_user.roles:
        print(f"  Rôle : {r.name}")

# Tester directement l'appel comme le fait add_programme
from src.database.models import UFRModel, ProgramLevelEnum
ufr = session.query(UFRModel).first()
print(f"\nUFR : {ufr.name if ufr else 'AUCUNE'}")

if ufr:
    print("\nAppel direct manager.create_program avec tab.current_user :")
    result = tab.structure_manager.create_program(
        name="TEST_TAB",
        code="TST888",
        level=ProgramLevelEnum.LICENCE_1,
        duration_years=3,
        ufr_id=ufr.id,
        current_user=tab.current_user
    )
    print(f"Résultat : {result}")

    # Nettoyer
    from src.database.models import ProgramModel
    p = session.query(ProgramModel).filter_by(code="TST888").first()
    if p:
        session.delete(p)
        session.commit()
        print("(nettoyé)")