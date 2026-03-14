# GUIDE D'EXÉCUTION DES TESTS — Pfair Scheduler

## 1. STRUCTURE À CRÉER DANS VOTRE PROJET

Copiez les fichiers de ce guide dans votre projet :

```
votre_projet/
├── src/                      ← votre code existant (ne pas toucher)
├── tests/                    ← NOUVEAU — créer ce dossier
│   ├── __init__.py           ← fichier vide
│   ├── conftest.py           ← fixtures partagées
│   ├── unit/
│   │   ├── __init__.py       ← fichier vide
│   │   ├── test_pfair_algorithm.py
│   │   ├── test_models.py
│   │   ├── test_auth_service.py
│   │   └── test_leave_service.py
│   ├── integration/
│   │   ├── __init__.py       ← fichier vide
│   │   └── test_scheduling_workflow.py
│   └── performance/
│       ├── __init__.py       ← fichier vide
│       └── test_performance.py
```

---

## 2. INSTALLATION DE PYTEST

Dans votre terminal, à la racine du projet :

```bash
pip install pytest pytest-cov
```

---

## 3. ORDRE D'EXÉCUTION RECOMMANDÉ

### ÉTAPE 1 — Tests Pfair (sans BDD, les plus rapides)
Ces tests ne nécessitent aucune base de données.
```bash
pytest tests/unit/test_pfair_algorithm.py -v
```
**Résultat attendu :** 15+ tests PASSED en < 5s

---

### ÉTAPE 2 — Tests des modèles SQLAlchemy
```bash
pytest tests/unit/test_models.py -v
```
**Résultat attendu :** 10+ tests PASSED

---

### ÉTAPE 3 — Tests authentification
```bash
pytest tests/unit/test_auth_service.py -v
```
**Résultat attendu :** 7 tests PASSED

**Note :** Si vos fonctions s'appellent différemment, adaptez les imports.
Cherchez dans votre code :
```python
grep -r "def authenticate\|def hash_password\|def create_user" src/
```

---

### ÉTAPE 4 — Tests des congés
```bash
pytest tests/unit/test_leave_service.py -v
```
**Résultat attendu :** 7 tests PASSED

---

### ÉTAPE 5 — Tests d'intégration
```bash
pytest tests/integration/ -v
```
**Résultat attendu :** 6 tests PASSED

---

### ÉTAPE 6 — Tests de performance
```bash
pytest tests/performance/test_performance.py -v -s
```
**Résultat attendu :** 6 tests PASSED, tableau affiché

---

### ÉTAPE 7 — TOUS LES TESTS + COUVERTURE
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 4. PROBLÈMES COURANTS ET SOLUTIONS

### ❌ "ModuleNotFoundError: No module named 'src'"
→ Exécutez pytest depuis la RACINE de votre projet (là où se trouve le dossier src/)
```bash
cd /chemin/vers/votre/projet
pytest tests/ -v
```

### ❌ "ImportError: cannot import name 'SlotStatusEnum'"
→ Retirez la ligne SlotStatusEnum dans test_scheduling_workflow.py
Remplacez par : `room="AMPHI A"` (sans le champ status)

### ❌ "AttributeError: 'NoneType' object has no attribute 'id'"
→ La fixture conftest.py n'a pas pu créer l'objet.
Vérifiez que vos repositories acceptent bien les mêmes paramètres.

### ❌ Tests d'auth qui échouent
→ Trouvez le bon import :
```python
grep -r "def authenticate\|def hash_password" src/services/
grep -r "def authenticate\|def hash_password" src/
```

### ❌ Tests de modèles qui échouent sur unicité
→ Certaines contraintes nécessitent que PRAGMA foreign_keys = ON soit activé.
Ajoutez dans conftest.py :
```python
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")
```

---

## 5. INTERPRÉTATION DES RÉSULTATS

| Symbole | Signification |
|---------|---------------|
| ✅ PASSED | Test réussi |
| ❌ FAILED | Test échoué — lire le message d'erreur |
| ⚠️ ERROR | Erreur Python (import manquant, etc.) |
| s (skipped) | Test ignoré |

### Résultat cible :
```
========================= 50+ passed in < 30s =========================
```

### Couverture cible :
```
TOTAL    ≥ 80%
```

---

## 6. ADAPTER LES TESTS À VOTRE CODE

Si certains imports ne correspondent pas exactement,
cherchez dans votre code source :

```bash
# Trouver les noms exacts de vos enums
grep -r "class.*Enum" src/utils/
grep -r "class.*Enum" src/database/

# Trouver vos services
ls src/services/

# Vérifier vos modèles
grep -r "class.*Model" src/database/models.py
```

Puis adaptez l'import dans le fichier de test concerné.
