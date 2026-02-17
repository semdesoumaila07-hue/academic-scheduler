# 📚 Référence API

Documentation complète de l'API du système d'ordonnancement.

---

## 🔥 PfairScheduler

### `schedule_cohort(cohort_id, start_date, end_date, available_rooms=None)`

Génère l'emploi du temps d'une cohorte avec l'algorithme Pfair.

**Paramètres** :
- `cohort_id` (int) : ID de la cohorte
- `start_date` (date) : Date de début
- `end_date` (date) : Date de fin
- `available_rooms` (List[str], optionnel) : Liste des salles disponibles

**Retour** : `Dict`
```python
{
    'success': True,
    'scheduled_slots': 45,
    'total_hours': 90,
    'conflicts': 0,
    'total_charge': 0.66,
    'effective_days': 120,
    'schedulable': True
}
```

**Exemple** :
```python
from src.services import PfairScheduler

scheduler = PfairScheduler(session)
result = scheduler.schedule_cohort(
    cohort_id=1,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30),
    available_rooms=['A101', 'A102', 'B201']
)

if result['success']:
    print(f"✅ {result['scheduled_slots']} créneaux créés")
```

---

### `is_schedulable(cohort_id, start_date, end_date)`

Vérifie si une cohorte peut être ordonnancée (test de faisabilité).

**Paramètres** :
- `cohort_id` (int) : ID de la cohorte
- `start_date` (date) : Date de début
- `end_date` (date) : Date de fin

**Retour** : `Dict`
```python
{
    'schedulable': True,
    'total_charge': 0.66,
    'effective_days': 120,
    'reason': 'OK' ou message d'erreur
}
```

**Condition de faisabilité** :
```
U = Σ U(τi) ≤ 1.0

où U(τi) = Ci / D_effectif
```

**Exemple** :
```python
result = scheduler.is_schedulable(
    cohort_id=1,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30)
)

if result['schedulable']:
    print(f"✅ Faisable (U={result['total_charge']:.2f})")
else:
    print(f"❌ {result['reason']}")
```

---

### `calculate_activity_priority(activity, t)`

Calcule la priorité d'une activité (α et retard).

**Paramètres** :
- `activity` (AcademicActivityModel) : Activité
- `t` (int) : Temps écoulé en jours

**Retour** : `Tuple[float, float]`
```python
(alpha, delay)  # (α, lag)
```

**Formules** :
```
lag(τi, t) = U(τi) × t - H(t)
α(τi, t) = lag / U(τi)
```

---

## 📅 CalendarService

### `is_workday(check_date, calendar_id=None)`

Vérifie si une date est un jour ouvrable.

**Paramètres** :
- `check_date` (date) : Date à vérifier
- `calendar_id` (int, optionnel) : ID du calendrier

**Retour** : `bool`

**Exemple** :
```python
from src.services import CalendarService

calendar_service = CalendarService(session)

if calendar_service.is_workday(date(2026, 1, 15)):
    print("✅ Jour ouvrable")
else:
    print("❌ Weekend, férié ou vacances")
```

---

### `calculate_effective_days(start_date, end_date, calendar_id=None)`

Calcule le nombre de jours ouvrables (D_effectif).

**Paramètres** :
- `start_date` (date) : Date de début
- `end_date` (date) : Date de fin
- `calendar_id` (int, optionnel) : ID du calendrier

**Retour** : `int`

**Calcul** :
```
D_effectif = Jours ouvrables - Jours fériés - Jours de vacances
```

**Exemple** :
```python
d_effective = calendar_service.calculate_effective_days(
    date(2026, 1, 1),
    date(2026, 6, 30)
)
print(f"D_effectif = {d_effective} jours")
```

---

## ⏱️ DelayCalculator

### `calculate_activity_delay(activity, reference_date=None)`

Calcule le retard d'une activité.

**Paramètres** :
- `activity` (AcademicActivityModel) : Activité
- `reference_date` (date, optionnel) : Date de référence (aujourd'hui par défaut)

**Retour** : `Dict`
```python
{
    'activity_id': 1,
    'activity_name': 'Algorithmique',
    'delay': 5.0,  # heures de retard
    'alpha': 0.5,
    'expected_hours': 15.0,
    'hours_done': 10.0,
    'remaining_hours': 20.0,
    'completion': 33.3,
    'urgency': 'Normal',  # Normal, Urgent, Critique
    'status': 'IN_PROGRESS'
}
```

**Exemple** :
```python
from src.services import DelayCalculator

calculator = DelayCalculator(session)
delay_info = calculator.calculate_activity_delay(activity)

print(f"Retard: {delay_info['delay']:.1f}h")
print(f"α: {delay_info['alpha']:.2f}")
print(f"Urgence: {delay_info['urgency']}")
```

---

### `get_urgent_activities(cohort_id=None, reference_date=None)`

Récupère les activités urgentes (α ≥ 0.5).

**Paramètres** :
- `cohort_id` (int, optionnel) : ID de la cohorte
- `reference_date` (date, optionnel) : Date de référence

**Retour** : `List[Dict]`

**Exemple** :
```python
urgent = calculator.get_urgent_activities(cohort_id=1)

print(f"{len(urgent)} activités urgentes")
for activity in urgent:
    print(f"- {activity['activity_name']}: α={activity['alpha']:.2f}")
```

---

## 🏗️ StructureManager

### `create_university(name, code, address, city, country='Burkina Faso')`

Crée une nouvelle université.

**Retour** : `Dict`
```python
{
    'success': True,
    'university_id': 1,
    'message': 'Université créée avec succès'
}
```

---

### `create_cohort(name, academic_year, semester, student_count, program_id, start_date, end_date)`

Crée une nouvelle cohorte.

**Exemple** :
```python
from src.managers import StructureManager

structure_mgr = StructureManager(session)

result = structure_mgr.create_cohort(
    name="L3 Info 2025-2026",
    academic_year="2025-2026",
    semester=1,
    student_count=45,
    program_id=1,
    start_date=date(2025, 10, 1),
    end_date=date(2026, 3, 31)
)

if result['success']:
    cohort_id = result['cohort_id']
```

---

## 📚 ActivityManager

### `create_activity(name, code, activity_type, volume_hours, cohort_id, teacher_id=None, activation_date=None, deadline=None, priority=1)`

Crée une nouvelle activité académique.

**Paramètres** :
- `name` (str) : Nom de l'activité
- `code` (str) : Code unique
- `activity_type` (ActivityTypeEnum) : COURS, TD, TP, EXAMEN
- `volume_hours` (float) : Volume horaire total (Ci)
- `cohort_id` (int) : ID de la cohorte
- `teacher_id` (int, optionnel) : ID de l'enseignant
- `activation_date` (date, optionnel) : Date d'activation (ri)
- `deadline` (date, optionnel) : Date limite (Di)
- `priority` (int) : Priorité (1-10)

**Exemple** :
```python
from src.managers import ActivityManager
from src.utils.constants import ActivityTypeEnum

activity_mgr = ActivityManager(session)

result = activity_mgr.create_activity(
    name="Algorithmique avancée",
    code="ALGO-301",
    activity_type=ActivityTypeEnum.COURS,
    volume_hours=30,
    cohort_id=1,
    teacher_id=1,
    priority=8
)
```

---

### `get_urgent_activities(cohort_id=None)`

Récupère les activités urgentes avec leurs métriques.

**Retour** : `List[Dict]`

---

## 🗓️ ScheduleGenerator

### `generate_schedule(cohort_id, start_date, end_date, available_rooms=None, replace_existing=False)`

Génère un emploi du temps complet.

**Paramètres** :
- `cohort_id` (int) : ID de la cohorte
- `start_date` (date) : Date de début
- `end_date` (date) : Date de fin
- `available_rooms` (List[str], optionnel) : Salles disponibles
- `replace_existing` (bool) : Remplacer l'emploi du temps existant

**Exemple** :
```python
from src.managers import ScheduleGenerator

schedule_gen = ScheduleGenerator(session)

result = schedule_gen.generate_schedule(
    cohort_id=1,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30),
    available_rooms=['A101', 'B202', 'C303'],
    replace_existing=True
)

print(f"Créneaux générés: {result['scheduled_slots']}")
```

---

### `create_manual_slot(cohort_id, activity_id, teacher_id, target_date, start_time, end_time, room=None)`

Crée manuellement un créneau horaire.

**Exemple** :
```python
result = schedule_gen.create_manual_slot(
    cohort_id=1,
    activity_id=1,
    teacher_id=1,
    target_date=date(2026, 1, 15),
    start_time=time(8, 0),
    end_time=time(10, 0),
    room='A101'
)
```

---

## ✅ ScheduleValidator

### `validate_time_slot(start_time, end_time)`

Valide un créneau horaire.

**Retour** : `Tuple[bool, Optional[str]]`

**Contraintes** :
- Durée ≥ 30 minutes
- Durée ≤ 4 heures
- Heures entre 7h et 20h

**Exemple** :
```python
from src.validators import ScheduleValidator

valid, error = ScheduleValidator.validate_time_slot(
    time(8, 0),
    time(10, 0)
)

if not valid:
    print(f"❌ Erreur: {error}")
```

---

## 🔍 ConflictDetector

### `detect_all_conflicts(slots)`

Détecte tous les types de conflits.

**Retour** : `Dict`
```python
{
    'teacher_conflicts': [],
    'cohort_conflicts': [],
    'room_conflicts': [],
    'total_conflicts': 0,
    'has_conflicts': False
}
```

**Exemple** :
```python
from src.validators import ConflictDetector

conflicts = ConflictDetector.detect_all_conflicts(schedule_slots)

if conflicts['has_conflicts']:
    print(f"❌ {conflicts['total_conflicts']} conflits détectés")
```

---

## 📄 PDFExporter

### `export_cohort_schedule(cohort, slots, start_date, end_date)`

Exporte un emploi du temps en PDF.

**Retour** : `Path` (chemin du fichier)

**Exemple** :
```python
from src.exporters import PDFExporter

pdf_exporter = PDFExporter()

filepath = pdf_exporter.export_cohort_schedule(
    cohort=cohort,
    slots=schedule_slots,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30)
)

print(f"✅ PDF généré: {filepath}")
```

---

## 📊 ExcelExporter

### `export_activities(activities)`

Exporte des activités en Excel.

**Exemple** :
```python
from src.exporters import ExcelExporter

excel_exporter = ExcelExporter()

filepath = excel_exporter.export_activities(activities)
print(f"✅ Excel: {filepath}")
```

---

## 🏖️ LeaveService

### `submit_leave_request(teacher_id, start_date, end_date, leave_type, reason)`

Soumet une demande de congé.

**Exemple** :
```python
from src.services import LeaveService
from src.utils.constants import LeaveTypeEnum

leave_service = LeaveService(session)

result = leave_service.submit_leave_request(
    teacher_id=1,
    start_date=date(2026, 2, 1),
    end_date=date(2026, 2, 7),
    leave_type=LeaveTypeEnum.CONGE_ANNUEL,
    reason="Vacances familiales"
)
```

---

## 🔧 ConfigLoader

### `get(key, default=None, config_type='app')`

Récupère une valeur de configuration.

**Exemple** :
```python
from src.config import config_loader

db_path = config_loader.get('database.path')
# → "data/ordonnancement.db"

urgent_alpha = config_loader.get(
    'pfair.thresholds.urgent_alpha',
    config_type='algorithm'
)
# → 1.0
```

---

## 📊 Codes de Retour

### Succès
```python
{
    'success': True,
    'message': 'Opération réussie',
    # ... autres données
}
```

### Erreur
```python
{
    'success': False,
    'error': 'Message d'erreur détaillé'
}
```

---

## 🎯 Enums

### ActivityTypeEnum
```python
COURS = "Cours Magistral"
TD = "Travaux Dirigés"
TP = "Travaux Pratiques"
EXAMEN = "Examen"
```

### ActivityStatusEnum
```python
PENDING = "En attente"
SCHEDULED = "Planifié"
IN_PROGRESS = "En cours"
COMPLETED = "Terminé"
CANCELLED = "Annulé"
```

### LeaveTypeEnum
```python
MALADIE = "Congé maladie"
CONGE_ANNUEL = "Congé annuel"
FORMATION = "Formation"
MATERNITE = "Congé maternité/paternité"
SANS_SOLDE = "Congé sans solde"
AUTRE = "Autre"
```

---

Cette API fournit tous les outils nécessaires pour :
- ✅ Générer des emplois du temps
- ✅ Calculer les retards
- ✅ Gérer la structure
- ✅ Valider les données
- ✅ Détecter les conflits
- ✅ Exporter les résultats