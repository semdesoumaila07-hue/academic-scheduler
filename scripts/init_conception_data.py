"""
Initialise les données de démonstration au format JSON/CSV (conception).
Exécuter une fois pour créer structure.json, teachers.csv, etc.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_manager import data_manager

data_manager.load_all()

# Données de démo conformes à la conception
r = data_manager.add_university("Université Norbert Zongo", "UNZ", "Avenue de l'Indépendance", "Ouagadougou", "Burkina Faso")
univ_id = r.get("id", "univ_1")

r = data_manager.add_ufr(univ_id, "UFR Sciences Exactes et Appliquées", "UFR-SEA", "Pr. Jean-Baptiste OUEDRAOGO")
ufr_id = f"ufr_{r.get('id', 1)}"

r = data_manager.add_program(ufr_id, "Licence Informatique", "L3-INFO", "Licence 3", 1)
prog_id = f"parcours_{r.get('id', 1)}"

r = data_manager.add_cohort(prog_id, "L3 Info 2025-2026", "2025-2026", 1, 45, "2025-10-01", "2026-03-31")
classe_id = f"classe_{r.get('id', 1)}"

# Enseignants
data_manager.add_teacher("Dr. Marie KABORE", "marie.kabore@unz.bf", "+226 70 12 34 56", "Algorithmique")
data_manager.add_teacher("Dr. Moussa TRAORE", "moussa.traore@unz.bf", "+226 70 23 45 67", "Bases de données")

# Activités (classe_id et ens_1, ens_2)
data_manager.add_activity("Algorithmique avancée", "ALG_ADV", "CM", classe_id, "ens_1", 30)
data_manager.add_activity("Algorithmique avancée TD", "ALG_ADV_TD", "TD", classe_id, "ens_1", 20)
data_manager.add_activity("Base de données", "BDD", "CM", classe_id, "ens_2", 25)

print("✓ Données de démonstration initialisées (structure.json, activities.csv, teachers.csv)")
