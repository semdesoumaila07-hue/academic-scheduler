# 🎓 Système d'Ordonnancement Académique P-équitable

Système intelligent de planification des emplois du temps académiques basé sur l'algorithme **Pfair (Proportionate Fair)**.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Fonctionnalités Principales

### ✅ Gestion de la Structure
- **Universités**, **UFR**, **Programmes**, **Cohortes**
- Gestion des **étudiants** et **enseignants**
- Hiérarchie complète de la structure universitaire

### ✅ Activités Académiques
- Création et suivi des **activités** (Cours, TD, TP, Examens)
- Calcul automatique du **retard** (lag) avec l'algorithme Pfair
- Priorisation des activités urgentes (**α ≥ 1**)

### ✅ Algorithme Pfair
- **Génération automatique** d'emplois du temps équitables
- Test de **faisabilité** (U ≤ 1.0)
- Équilibrage des charges de travail
- Minimisation des retards

### ✅ Gestion des Congés
- Demandes de congés des enseignants
- Workflow d'**approbation/rejet**
- Blocage automatique des créneaux

### ✅ Calendrier Académique
- Jours fériés et périodes de vacances
- Calcul du **D_effectif** (jours ouvrables)
- Gestion des weekends

### ✅ Interface Graphique
- **Interface PyQt5** moderne et intuitive
- Visualisation des emplois du temps
- Tableaux de bord et statistiques
- Export PDF

---

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étape 1 : Cloner le projet
```bash
cd academic-scheduler
```

### Étape 2 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 3 : Initialiser la base de données
```bash
python init_db.py --with-test-data
```

### Étape 4 : Lancer l'application
```bash
python main.py
```

---

## 🏗️ Architecture du Projet

```
academic-scheduler/
├── src/
│   ├── config/              # Configuration globale
│   ├── utils/               # Utilitaires et constantes
│   ├── entities/            # 12 entités métier
│   ├── database/            # Base de données
│   │   ├── models.py        # Modèles SQLAlchemy
│   │   ├── repositories/    # 13 repositories
│   │   └── migrations/      # Scripts SQL
│   ├── services/            # Services métier
│   │   ├── pfair_scheduler.py      # 🔥 Algorithme Pfair
│   │   ├── calendar_service.py     # Gestion calendrier
│   │   ├── leave_service.py        # Gestion congés
│   │   └── delay_calculator.py     # Calcul retards
│   ├── managers/            # Managers de haut niveau
│   │   ├── structure_manager.py    # Structure universitaire
│   │   ├── activity_manager.py     # Activités
│   │   └── schedule_generator.py   # Génération EDT
│   └── ui/                  # Interface graphique PyQt5
│       ├── main_window.py   # Fenêtre principale
│       ├── dialogs/         # 4 dialogues
│       └── widgets/         # 2 widgets personnalisés
├── data/                    # Base de données SQLite
├── outputs/                 # Fichiers générés
├── logs/                    # Journaux
├── main.py                  # Point d'entrée
├── init_db.py              # Initialisation BD
└── requirements.txt        # Dépendances

```

---

## 🔬 Algorithme Pfair

### Principe
L'algorithme **Pfair** (Proportionate Fair) garantit un ordonnancement équitable en maintenant la proportionnalité entre le temps écoulé et le travail effectué.

### Formules Clés

**1. Facteur de charge**
```
U(τi) = Ci / D_effectif
```
- `Ci` : Volume horaire total
- `D_effectif` : Nombre de jours ouvrables

**2. Retard (lag)**
```
lag(τi, t) = U(τi) × t - H(t)
```
- `t` : Temps écoulé en jours
- `H(t)` : Heures réalisées

**3. Ratio α**
```
α(τi, t) = lag(τi, t) / U(τi)
```

**4. Condition d'urgence**
```
Si α ≥ 1 → Activité URGENTE
```

### Test de Faisabilité
```
U = Σ U(τi) ≤ 1.0
```

---

## 💻 Utilisation

### 1. Créer une Université et sa Structure
```
📊 Tableau de bord > 🏛️ Structure > Nouvelle Université
```

### 2. Ajouter des Enseignants
```
👨‍🏫 Enseignants > ➕ Nouvel Enseignant
```

### 3. Créer des Activités
```
📚 Activités > ➕ Nouvelle Activité
```

### 4. Générer un Emploi du Temps
```
🗓️ Emplois du temps > 🔄 Générer Emploi du Temps (Pfair)
```

L'algorithme Pfair va :
1. Calculer les facteurs de charge U(τi)
2. Vérifier la faisabilité (U ≤ 1.0)
3. Ordonnancer les activités urgentes (α ≥ 1)
4. Créer les créneaux horaires
5. Minimiser les retards

---

## 📊 Base de Données

### Tables Principales (12)
1. `universities` - Universités
2. `ufrs` - Unités de Formation
3. `programs` - Programmes/Parcours
4. `cohorts` - Cohortes/Classes
5. `teachers` - Enseignants
6. `students` - Étudiants
7. `academic_activities` - Activités (avec paramètres Pfair)
8. `schedule_slots` - Créneaux horaires
9. `leave_requests` - Demandes de congé
10. `academic_calendars` - Calendriers académiques
11. `holidays` - Jours fériés
12. `vacation_periods` - Périodes de vacances

### Sauvegarde
```bash
# Créer une sauvegarde
Fichier > Sauvegarder
```

Les sauvegardes sont stockées dans `backups/`

---

## 🎯 Exemples d'Utilisation

### Exemple 1 : Vérifier la Faisabilité
```python
from src.services import PfairScheduler

scheduler = PfairScheduler(session)
result = scheduler.is_schedulable(
    cohort_id=1,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30)
)

if result['schedulable']:
    print(f"✅ Charge totale: {result['total_charge']:.2f}")
else:
    print(f"❌ {result['reason']}")
```

### Exemple 2 : Calculer le Retard d'une Cohorte
```python
from src.services import DelayCalculator

calculator = DelayCalculator(session)
delay_info = calculator.calculate_cohort_delay(cohort_id=1)

print(f"Retard total: {delay_info['total_delay']:.2f} heures")
print(f"Activités critiques: {delay_info['critical_activities']}")
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_entities/
pytest tests/test_services/
```

---

## 📝 Licence

MIT License - Voir le fichier `LICENSE` pour plus de détails.

---

## 👥 Auteurs

Système développé pour l'**Université Norbert Zongo**  
Burkina Faso 🇧🇫

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**Fait avec ❤️ pour l'éducation au Burkina Faso**