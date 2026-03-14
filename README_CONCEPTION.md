# Mode Conception - Conformité au document conception.pdf

Ce projet propose deux modes d'exécution :

## Mode Conception (conforme)

**Technologies :** CustomTkinter (interface) + JSON/CSV (données)

- `config/app_config.json` : mettre `"conception_mode": true`
- Lancer : `python run.py` ou `python run_conception.py`
- Données : `data/structure.json`, `data/activities.csv`, `data/teachers.csv`, `data/leaves.json`

### Initialiser les données de démonstration

```bash
python scripts/init_conception_data.py
```

## Mode Legacy (PyQt5 + SQLite)

**Technologies :** PyQt5 (interface) + SQLAlchemy/SQLite (données)

- `config/app_config.json` : mettre `"conception_mode": false`
- Lancer : `python run.py`
- Données : `data/ordonnancement.db`

## Fichiers conformes à la conception

| Fichier | Description |
|---------|-------------|
| `src/data/data_manager.py` | DataManager - API unifiée JSON/CSV |
| `src/ui_ctk/main_window_ctk.py` | Interface CustomTkinter |
| `run_conception.py` | Point d'entrée mode conception |

## Dépendances

```bash
pip install customtkinter matplotlib pandas
# Optionnel (mode legacy) : pip install PyQt5 SQLAlchemy
```
