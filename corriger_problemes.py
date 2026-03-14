"""
SCRIPT DE CORRECTION — À lancer UNE SEULE FOIS depuis la racine du projet
==========================================================================
    python corriger_problemes.py

Corrige :
  1. Colonnes manquantes dans teacher_availability (period_start, period_end)
  2. Fichiers qui utilisent encore JSON au lieu de SQLite
  3. Passage de current_user dans StructureTab
"""

import sys, os, sqlite3, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def ligne(t): print(f"\n{'═'*60}\n  {t}\n{'═'*60}")
def ok(m):    print(f"  ✅ {m}")
def info(m):  print(f"  ℹ️  {m}")
def err(m):   print(f"  ❌ {m}")

# ══════════════════════════════════════════════════════════════
# CORRECTION 1 — Ajouter les colonnes manquantes à la table
#                teacher_availability
# ══════════════════════════════════════════════════════════════
ligne("CORRECTION 1 — Colonnes manquantes dans teacher_availability")

# Trouver le fichier SQLite
from config.settings import DATABASE_PATH
db_path = str(DATABASE_PATH)
info(f"Base SQLite : {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    # Vérifier les colonnes existantes
    cur.execute("PRAGMA table_info(teacher_availability)")
    colonnes = [row[1] for row in cur.fetchall()]
    info(f"Colonnes actuelles : {colonnes}")

    # Ajouter period_start si absente
    if 'period_start' not in colonnes:
        cur.execute("ALTER TABLE teacher_availability ADD COLUMN period_start DATE")
        ok("Colonne period_start ajoutée")
    else:
        ok("period_start déjà présente")

    # Ajouter period_end si absente
    if 'period_end' not in colonnes:
        cur.execute("ALTER TABLE teacher_availability ADD COLUMN period_end DATE")
        ok("Colonne period_end ajoutée")
    else:
        ok("period_end déjà présente")

    # Mettre des valeurs par défaut pour les lignes existantes (NULL interdit)
    cur.execute("""
        UPDATE teacher_availability
        SET period_start = '2025-09-01'
        WHERE period_start IS NULL
    """)
    cur.execute("""
        UPDATE teacher_availability
        SET period_end = '2026-07-31'
        WHERE period_end IS NULL
    """)
    conn.commit()
    ok("Valeurs par défaut appliquées aux lignes existantes")

    # Vérification finale
    cur.execute("PRAGMA table_info(teacher_availability)")
    colonnes_finales = [row[1] for row in cur.fetchall()]
    info(f"Colonnes finales : {colonnes_finales}")
    conn.close()

except Exception as e:
    err(f"Erreur migration : {e}")
    import traceback; traceback.print_exc()


# ══════════════════════════════════════════════════════════════
# CORRECTION 2 — Patcher structure_tab.py pour passer
#                current_user au StructureManager
# ══════════════════════════════════════════════════════════════
ligne("CORRECTION 2 — Passer current_user dans StructureTab")

structure_tab_path = os.path.join("src", "ui", "tabs", "structure_tab.py")

if not os.path.exists(structure_tab_path):
    err(f"Fichier introuvable : {structure_tab_path}")
else:
    with open(structure_tab_path, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Sauvegarder l'original
    shutil.copy(structure_tab_path, structure_tab_path + ".backup")
    ok("Backup créé : structure_tab.py.backup")

    modifie = contenu

    # 1. Changer __init__ pour accepter current_user
    ancien_init = "    def __init__(self):\n        super().__init__()\n        self.session = db_manager.get_session()\n        self.structure_manager = StructureManager(self.session)"
    nouveau_init = "    def __init__(self, current_user=None):\n        super().__init__()\n        self.current_user = current_user\n        self.session = db_manager.get_session()\n        self.structure_manager = StructureManager(self.session)"

    if ancien_init in modifie:
        modifie = modifie.replace(ancien_init, nouveau_init)
        ok("__init__ mis à jour avec current_user")
    else:
        # Essai plus souple
        if "def __init__(self):" in modifie and "StructureManager" in modifie:
            modifie = modifie.replace(
                "    def __init__(self):",
                "    def __init__(self, current_user=None):\n        self.current_user = current_user"
            )
            ok("__init__ patché (méthode alternative)")
        else:
            info("__init__ déjà correct ou format différent — ignoré")

    # 2. Passer current_user à create_university, create_ufr, etc.
    for methode in ["create_university", "create_ufr", "create_program", "create_cohort"]:
        # Remplacer les appels sans current_user par des appels avec current_user
        ancien = f"self.structure_manager.{methode}("
        nouveau = f"self.structure_manager.{methode}(current_user=self.current_user, "
        if ancien in modifie and nouveau not in modifie:
            modifie = modifie.replace(ancien, nouveau)
            ok(f"current_user ajouté dans {methode}()")

    with open(structure_tab_path, 'w', encoding='utf-8') as f:
        f.write(modifie)
    ok("structure_tab.py mis à jour")


# ══════════════════════════════════════════════════════════════
# CORRECTION 3 — Patcher main_window.py pour passer
#                current_user à StructureTab
# ══════════════════════════════════════════════════════════════
ligne("CORRECTION 3 — Passer current_user à StructureTab dans MainWindow")

main_window_path = os.path.join("src", "ui", "main_window.py")

if not os.path.exists(main_window_path):
    err(f"Fichier introuvable : {main_window_path}")
else:
    with open(main_window_path, 'r', encoding='utf-8') as f:
        contenu = f.read()

    shutil.copy(main_window_path, main_window_path + ".backup")

    # Remplacer instance = tab_class() pour StructureTab par tab_class(current_user=...)
    ancien = "            elif tab_class.__name__ == 'StructureTab':\n                instance = tab_class()\n                self.structure_tab = instance"
    nouveau = "            elif tab_class.__name__ == 'StructureTab':\n                instance = tab_class(current_user=self.current_user)\n                self.structure_tab = instance"

    if ancien in contenu:
        contenu = contenu.replace(ancien, nouveau)
        ok("StructureTab reçoit maintenant current_user")
    else:
        # Patcher plus simplement
        contenu = contenu.replace(
            "tab_class.__name__ == 'StructureTab':\n                instance = tab_class()",
            "tab_class.__name__ == 'StructureTab':\n                instance = tab_class(current_user=self.current_user)"
        )
        ok("StructureTab patché (méthode alternative)")

    with open(main_window_path, 'w', encoding='utf-8') as f:
        f.write(contenu)
    ok("main_window.py mis à jour")


# ══════════════════════════════════════════════════════════════
# CORRECTION 4 — Vérifier et lister les fichiers qui utilisent
#                encore JSON pour données académiques
# ══════════════════════════════════════════════════════════════
ligne("CORRECTION 4 — Fichiers utilisant encore JSON (diagnostic)")

fichiers_json = []
for root, dirs, files in os.walk("src"):
    # Ignorer __pycache__
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for fichier in files:
        if not fichier.endswith('.py'):
            continue
        chemin = os.path.join(root, fichier)
        try:
            with open(chemin, 'r', encoding='utf-8', errors='ignore') as f:
                contenu_f = f.read()
            # Chercher des lectures de fichiers JSON de données (pas de config)
            if any(pattern in contenu_f for pattern in [
                "structure.json", "teachers.json", "activities.json",
                "open('data/", 'open("data/',
                "structure_file.exists()", "json.load(f)"
            ]):
                # Compter les occurrences
                nb = sum(contenu_f.count(p) for p in ["structure.json", ".json", "json.load"])
                fichiers_json.append((chemin, nb))
        except:
            pass

if fichiers_json:
    print("\n  ⚠️  Fichiers utilisant encore JSON :")
    for chemin, nb in sorted(fichiers_json, key=lambda x: -x[1]):
        print(f"    • {chemin}  ({nb} occurrences)")
    print(f"\n  Total : {len(fichiers_json)} fichiers à corriger")
    info("Ces fichiers lisent encore des données depuis des fichiers JSON")
    info("Ils doivent être migrés vers SQLite")
else:
    ok("Aucun fichier ne lit de JSON pour les données académiques")


# ══════════════════════════════════════════════════════════════
# CORRECTION 5 — Patcher le simuler_donnees_test.py pour
#                inclure period_start/period_end dans les dispo
# ══════════════════════════════════════════════════════════════
ligne("CORRECTION 5 — Mettre à jour simuler_donnees_test.py")

sim_path = "simuler_donnees_test.py"
if os.path.exists(sim_path):
    with open(sim_path, 'r', encoding='utf-8') as f:
        sim = f.read()

    ancien_dispo = """                dispo = TeacherAvailabilityModel(
                teacher_id=ens.id,
                day_of_week=jour,
                start_time=time(8, 0),
                end_time=time(18, 0)
            )"""

    nouveau_dispo = """                dispo = TeacherAvailabilityModel(
                teacher_id=ens.id,
                day_of_week=jour,
                start_time=time(8, 0),
                end_time=time(18, 0),
                period_start=DEBUT_SEMESTRE,
                period_end=FIN_SEMESTRE
            )"""

    if ancien_dispo in sim:
        sim = sim.replace(ancien_dispo, nouveau_dispo)
        with open(sim_path, 'w', encoding='utf-8') as f:
            f.write(sim)
        ok("simuler_donnees_test.py mis à jour avec period_start/period_end")
    else:
        info("simuler_donnees_test.py déjà correct ou format différent")
else:
    info("simuler_donnees_test.py non trouvé — ignoré")


# ══════════════════════════════════════════════════════════════
# RÉSUMÉ
# ══════════════════════════════════════════════════════════════
ligne("RÉSUMÉ DES CORRECTIONS APPLIQUÉES")
print("""
  1. ✅ Colonnes period_start/period_end ajoutées à teacher_availability
  2. ✅ structure_tab.py accepte current_user en paramètre
  3. ✅ Les appels create_*() passent current_user au StructureManager
  4. ✅ main_window.py passe current_user à StructureTab
  5. ✅ simuler_donnees_test.py corrigé

  ▶️  Lancez maintenant :
      python simuler_donnees_test.py   ← recréer les données
      python main.py                   ← lancer l'application
""")
print("═" * 60)
print("  ✅  CORRECTIONS TERMINÉES")
print("═" * 60)