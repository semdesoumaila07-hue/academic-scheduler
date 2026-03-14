"""
Diagnostic complet : trouve TOUTES les définitions de require_permission
et teste la création d'un parcours directement.
"""
import sys, os, inspect
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 70)
print("1. RECHERCHE DE TOUS LES require_permission CHARGÉS")
print("=" * 70)

# Forcer le rechargement
import importlib
import src.services.auth_service as auth_mod
importlib.reload(auth_mod)

func = auth_mod.require_permission
source = inspect.getsource(func)
print(f"Fichier : {inspect.getfile(auth_mod)}")
print(f"kwargs.pop : {'OUI ✅' if 'kwargs.pop' in source else 'NON ❌'}")
print(f"kwargs.get : {'OUI ❌' if 'kwargs.get' in source else 'NON ✅'}")

print("\n" + "=" * 70)
print("2. VÉRIFICATION DU MANAGER")
print("=" * 70)

import src.managers.structure_manager as sm_mod
importlib.reload(sm_mod)

# Vérifier quel require_permission le manager utilise
sm_source = inspect.getsource(sm_mod)
if 'from ..services.auth_service import require_permission' in sm_source:
    print("Manager importe depuis : ..services.auth_service ✅")
elif 'from .auth_service import require_permission' in sm_source:
    print("Manager importe depuis : .auth_service")
else:
    print("Import inconnu !")

# Vérifier la fonction décorée réelle
manager_class = sm_mod.StructureManager
create_program = manager_class.create_program
print(f"\ncreate_program est un wrapper : {hasattr(create_program, '__wrapped__')}")

# Extraire le décorateur réellement utilisé
try:
    wrapper_source = inspect.getsource(create_program)
    print(f"Source contient pop : {'OUI ✅' if 'pop' in wrapper_source else 'NON ❌'}")
except:
    pass

print("\n" + "=" * 70)
print("3. TEST DIRECT SANS INTERFACE")
print("=" * 70)

from src.database.db_manager import db_manager
db_manager.initialize()
db_manager.create_tables()
session = db_manager.get_session()

from src.database.models import UserModel
admin = session.query(UserModel).filter(UserModel.username == 'admin').first()
if not admin:
    admin = session.query(UserModel).first()

print(f"Utilisateur test : {admin.username if admin else 'AUCUN'}")
if admin:
    for r in admin.roles:
        print(f"  Rôle : {r.name}")
        for p in r.permissions:
            print(f"    Permission : {p.name}")

# Test direct
from src.managers.structure_manager import StructureManager
manager = StructureManager(session)

# Chercher une UFR existante
from src.database.models import UFRModel
ufr = session.query(UFRModel).first()
print(f"\nUFR disponible : {ufr.name if ufr else 'AUCUNE'}")

if ufr and admin:
    from src.database.models import ProgramLevelEnum
    print("\nTest create_program avec current_user=admin :")
    result = manager.create_program(
        name="TEST_DIAG",
        code="TST999",
        level=ProgramLevelEnum.LICENCE_1,
        duration_years=3,
        ufr_id=ufr.id,
        current_user=admin
    )
    print(f"Résultat : {result}")

    # Nettoyer
    from src.database.models import ProgramModel
    p = session.query(ProgramModel).filter_by(code="TST999").first()
    if p:
        session.delete(p)
        session.commit()
        print("(test nettoyé)")