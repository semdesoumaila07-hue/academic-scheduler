<<<<<<< HEAD
# 📚 Référence API - Système d'Ordonnancement Académique P-équitable

Documentation complète de l'API du système d'ordonnancement académique.

---

## 📋 Table des matières

1. [Managers](#managers)
   - [StructureManager](#structuremanager)
   - [ActivityManager](#activitymanager)
   - [ScheduleGenerator](#schedulegenerator)
2. [Services](#services)
   - [PfairScheduler](#pfairscheduler)
   - [CalendarService](#calendarservice)
   - [LeaveService](#leaveservice)
   - [DelayCalculator](#delaycalculator)
   - [DashboardService](#dashboardservice)
3. [Repositories](#repositories)
4. [Exemples d'utilisation](#exemples-dutilisation)

---

## Managers

### StructureManager

Gère la structure universitaire (Universités, UFR, Programmes, Cohortes, Étudiants).

#### `create_university(name: str, code: str, address: str, city: str, country: str = "Burkina Faso") -> Dict`

Crée une nouvelle université.

**Paramètres:**
- `name` (str): Nom de l'université
- `code` (str): Code unique
- `address` (str): Adresse
- `city` (str): Ville
- `country` (str): Pays (défaut: "Burkina Faso")

**Retourne:**
```python
{
    'success': True,
    'university_id': int,
    'message': str
}
```

**Exemple:**
```python
from src.managers.structure_manager import StructureManager
from src.database.db_manager import db_manager

session = db_manager.get_session()
manager = StructureManager(session)

result = manager.create_university(
    name="Université Norbert Zongo",
    code="UNZ",
    address="BP 376 Koudougou",
    city="Koudougou",
    country="Burkina Faso"
)
```

#### `create_ufr(name: str, code: str, director: str, university_id: int) -> Dict`

Crée une nouvelle UFR.

**Paramètres:**
- `name` (str): Nom de l'UFR
- `code` (str): Code unique
- `director` (str): Nom du directeur
- `university_id` (int): ID de l'université parente

**Retourne:**
```python
{
    'success': True,
    'ufr_id': int,
    'message': str
}
```

#### `create_program(name: str, code: str, level: ProgramLevelEnum, duration_years: int, ufr_id: int) -> Dict`

Crée un nouveau programme.

**Paramètres:**
- `name` (str): Nom du programme
- `code` (str): Code unique
- `level` (ProgramLevelEnum): Niveau (LICENCE_1, LICENCE_2, etc.)
- `duration_years` (int): Durée en années
- `ufr_id` (int): ID de l'UFR parente

**Retourne:**
```python
{
    'success': True,
    'program_id': int,
    'message': str
}
```

#### `create_cohort(name: str, academic_year: str, semester: int, student_count: int, program_id: int, start_date: date, end_date: date) -> Dict`

Crée une nouvelle cohorte.

**Paramètres:**
- `name` (str): Nom de la cohorte
- `academic_year` (str): Année académique (ex: "2025-2026")
- `semester` (int): Semestre (1 ou 2)
- `student_count` (int): Nombre d'étudiants
- `program_id` (int): ID du programme parent
- `start_date` (date): Date de début
- `end_date` (date): Date de fin

**Retourne:**
```python
{
    'success': True,
    'cohort_id': int,
    'message': str
}
```

#### `get_all_universities() -> List[UniversityModel]`

Récupère toutes les universités.

#### `get_ufrs_by_university(university_id: int) -> List[UFRModel]`

Récupère toutes les UFR d'une université.

#### `get_programs_by_ufr(ufr_id: int) -> List[ProgramModel]`

Récupère tous les programmes d'une UFR.

#### `get_cohorts_by_program(program_id: int) -> List[CohortModel]`

Récupère toutes les cohortes d'un programme.

---

### ActivityManager

Gère les activités académiques.

#### `create_activity(name: str, code: str, activity_type: ActivityTypeEnum, volume_hours: float, cohort_id: int, teacher_id: int = None, activation_date: date = None, deadline: date = None, priority: PriorityEnum = None, current_user: Any = None) -> Dict`

Crée une nouvelle activité académique.

**Paramètres:**
- `name` (str): Nom de l'activité
- `code` (str): Code unique
- `activity_type` (ActivityTypeEnum): Type (COURS_MAGISTRAL, TD, TP, EXAMEN, SOUTENANCE)
- `volume_hours` (float): Volume horaire total (Ci)
- `cohort_id` (int): ID de la cohorte
- `teacher_id` (int, optionnel): ID de l'enseignant
- `activation_date` (date, optionnel): Date d'activation (ri)
- `deadline` (date, optionnel): Date limite (Di)
- `priority` (PriorityEnum, optionnel): Priorité (BASSE, NORMALE, HAUTE, URGENTE)
- `current_user` (Any, optionnel): Utilisateur actuel pour vérification des permissions

**Retourne:**
```python
{
    'success': True,
    'activity_id': int,
    'message': str
}
```

**Exemple:**
```python
from src.managers.activity_manager import ActivityManager
from src.database.models import ActivityTypeEnum, PriorityEnum
from datetime import date

manager = ActivityManager(session)

result = manager.create_activity(
    name="Algorithmique avancée",
    code="ALGO-301",
    activity_type=ActivityTypeEnum.COURS_MAGISTRAL,
    volume_hours=30.0,
    cohort_id=1,
    teacher_id=2,
    activation_date=date(2025, 1, 15),
    deadline=date(2025, 5, 30),
    priority=PriorityEnum.HAUTE
)
```

#### `get_activities_by_cohort(cohort_id: int) -> List[AcademicActivityModel]`

Récupère toutes les activités d'une cohorte.

#### `update_activity_hours(activity_id: int, hours_done: float) -> Dict`

Met à jour les heures réalisées d'une activité.

---

### ScheduleGenerator

Gère la génération d'emplois du temps avec l'algorithme Pfair.

#### `generate_schedule(cohort_id: int, start_date: date, end_date: date, available_rooms: List[str] = None, replace_existing: bool = False, current_user: Any = None) -> Dict`

Génère l'emploi du temps d'une cohorte avec l'algorithme Pfair.

**Paramètres:**
- `cohort_id` (int): ID de la cohorte
- `start_date` (date): Date de début
- `end_date` (date): Date de fin
- `available_rooms` (List[str], optionnel): Liste des salles disponibles
- `replace_existing` (bool): Si True, supprime l'emploi du temps existant
- `current_user` (Any, optionnel): Utilisateur actuel

**Retourne:**
```python
{
    'success': True,
    'schedule_id': int,
    'slots_created': int,
    'message': str
}
```

**Exemple:**
```python
from src.managers.schedule_generator import ScheduleGenerator
from datetime import date

generator = ScheduleGenerator(session)

result = generator.generate_schedule(
    cohort_id=1,
    start_date=date(2025, 1, 15),
    end_date=date(2025, 5, 30),
    available_rooms=["A101", "A102", "B201"],
    replace_existing=True
)
```

---

## Services

### PfairScheduler

Implémente l'algorithme Pfair pour l'ordonnancement équitable.

#### `test_feasibility(activities: List[AcademicActivityModel], effective_days: int) -> Dict`

Teste la faisabilité d'un ensemble d'activités.

**Paramètres:**
- `activities`: Liste des activités
- `effective_days`: Nombre de jours ouvrables effectifs

**Retourne:**
```python
{
    'feasible': bool,
    'total_charge': float,
    'max_charge': float,
    'message': str
}
```

#### `calculate_urgency_ratio(activity: AcademicActivityModel, current_date: date) -> float`

Calcule le ratio d'urgence α(τi, t) d'une activité.

**Formule:** `α(τi, t) = lag(τi, t) / U(τi)`

#### `generate_schedule(activities: List[AcademicActivityModel], start_date: date, end_date: date, available_rooms: List[str]) -> List[ScheduleSlot]`

Génère un emploi du temps avec l'algorithme Pfair.

---

### CalendarService

Gère le calendrier académique.

#### `calculate_effective_days(start_date: date, end_date: date) -> int`

Calcule le nombre de jours ouvrables effectifs (D_effectif).

**Exemple:**
```python
from src.services.calendar_service import CalendarService
from datetime import date

service = CalendarService(session)
effective_days = service.calculate_effective_days(
    start_date=date(2025, 1, 15),
    end_date=date(2025, 5, 30)
)
```

#### `validate_date_range(start_date: date, end_date: date) -> Dict`

Valide une plage de dates.

**Retourne:**
```python
{
    'valid': bool,
    'reason': str
}
```

#### `is_working_day(date: date) -> bool`

Vérifie si une date est un jour ouvrable.

---

### LeaveService

Gère les demandes de congés.

#### `submit_leave_request(teacher_id: int, start_date: date, end_date: date, leave_type: LeaveTypeEnum, reason: str = "") -> Dict`

Soumet une demande de congé.

**Paramètres:**
- `teacher_id` (int): ID de l'enseignant
- `start_date` (date): Date de début
- `end_date` (date): Date de fin
- `leave_type` (LeaveTypeEnum): Type de congé
- `reason` (str): Raison

**Retourne:**
```python
{
    'success': True,
    'leave_request_id': int,
    'message': str
}
```

#### `approve_leave_request(leave_request_id: int, approver_id: int) -> Dict`

Approuve une demande de congé.

#### `reject_leave_request(leave_request_id: int, approver_id: int, reason: str) -> Dict`

Rejette une demande de congé.

---

### DelayCalculator

Calcule les retards académiques.

#### `calculate_delay(activity: AcademicActivityModel, current_date: date) -> Dict`

Calcule le retard d'une activité.

**Retourne:**
```python
{
    'lag': float,
    'urgency_ratio': float,
    'classification': str,  # 'Critique', 'Urgent', 'Normal'
    'predicted_completion': date
}
```

#### `get_urgent_activities(cohort_id: int = None) -> List[Dict]`

Récupère les activités urgentes (α ≥ 1.0).

---

### DashboardService

Fournit les données pour le tableau de bord.

#### `get_dashboard_data() -> Dict`

Récupère toutes les données du tableau de bord.

**Retourne:**
```python
{
    'kpis': [
        {'label': str, 'value': int/float, 'icon': str},
        ...
    ],
    'recent_activities': [
        {
            'name': str,
            'type': str,
            'volume_hours': float,
            'hours_done': float,
            'completion_percentage': float,
            'status': str
        },
        ...
    ],
    'completion_percentage': float
}
```

---

## Repositories

Tous les repositories héritent de `BaseRepository` et implémentent les méthodes CRUD standard :

- `create(**kwargs) -> Model`
- `get_by_id(id: int) -> Optional[Model]`
- `get_all(skip: int = 0, limit: int = 100) -> List[Model]`
- `update(id: int, **kwargs) -> Optional[Model]`
- `delete(id: int) -> bool`

### Repositories disponibles

- `UniversityRepository`
- `UFRRepository`
- `ProgramRepository`
- `CohortRepository`
- `StudentRepository`
- `TeacherRepository`
- `ActivityRepository`
- `ScheduleRepository`
- `LeaveRequestRepository`
- `CalendarRepository`
- `HolidayRepository`
- `VacationPeriodRepository`

---

## Exemples d'utilisation

### Exemple complet : Créer une structure et des activités

```python
from src.database.db_manager import db_manager
from src.managers.structure_manager import StructureManager
from src.managers.activity_manager import ActivityManager
from src.database.models import ActivityTypeEnum, PriorityEnum, ProgramLevelEnum
from datetime import date

# Initialiser la base de données
db_manager.initialize()
db_manager.create_tables()
session = db_manager.get_session()

# Créer les managers
structure_manager = StructureManager(session)
activity_manager = ActivityManager(session)

# 1. Créer une université
univ_result = structure_manager.create_university(
    name="Université Norbert Zongo",
    code="UNZ",
    address="BP 376",
    city="Koudougou"
)
university_id = univ_result['university_id']

# 2. Créer une UFR
ufr_result = structure_manager.create_ufr(
    name="UFR Sciences Exactes et Appliquées",
    code="UFR-SEA",
    director="Dr. Jean Dupont",
    university_id=university_id
)
ufr_id = ufr_result['ufr_id']

# 3. Créer un programme
program_result = structure_manager.create_program(
    name="Licence Informatique",
    code="L3-INFO",
    level=ProgramLevelEnum.LICENCE_3,
    duration_years=1,
    ufr_id=ufr_id
)
program_id = program_result['program_id']

# 4. Créer une cohorte
cohort_result = structure_manager.create_cohort(
    name="L3 Info 2025-2026",
    academic_year="2025-2026",
    semester=1,
    student_count=50,
    program_id=program_id,
    start_date=date(2025, 1, 15),
    end_date=date(2025, 5, 30)
)
cohort_id = cohort_result['cohort_id']

# 5. Créer une activité
activity_result = activity_manager.create_activity(
    name="Algorithmique avancée",
    code="ALGO-301",
    activity_type=ActivityTypeEnum.COURS_MAGISTRAL,
    volume_hours=30.0,
    cohort_id=cohort_id,
    activation_date=date(2025, 1, 15),
    deadline=date(2025, 5, 30),
    priority=PriorityEnum.HAUTE
)

print(f"✅ Activité créée: {activity_result['message']}")
```

### Exemple : Générer un emploi du temps

```python
from src.managers.schedule_generator import ScheduleGenerator
from datetime import date

generator = ScheduleGenerator(session)

result = generator.generate_schedule(
    cohort_id=1,
    start_date=date(2025, 1, 15),
    end_date=date(2025, 5, 30),
    available_rooms=["A101", "A102", "B201", "B202"],
    replace_existing=True
)

if result['success']:
    print(f"✅ Emploi du temps généré: {result['slots_created']} créneaux créés")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Exemple : Calculer les retards

```python
from src.services.delay_calculator import DelayCalculator
from datetime import date

calculator = DelayCalculator(session)
activities = activity_manager.get_activities_by_cohort(cohort_id=1)

for activity in activities:
    delay_info = calculator.calculate_delay(activity, date.today())
    print(f"{activity.name}:")
    print(f"  Retard: {delay_info['lag']:.2f}h")
    print(f"  Ratio d'urgence: {delay_info['urgency_ratio']:.2f}")
    print(f"  Classification: {delay_info['classification']}")
=======
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
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
```

---

<<<<<<< HEAD
## 🔐 Permissions

Certaines méthodes nécessitent des permissions spécifiques :

- `manage_structure`: Gérer la structure universitaire
- `manage_activities`: Gérer les activités académiques
- `launch_scheduling`: Lancer l'ordonnancement
- `manage_leaves`: Gérer les congés

Les permissions sont vérifiées automatiquement via le décorateur `@require_permission`.

---

## 📝 Notes

- Toutes les dates doivent être des objets `date` du module `datetime`
- Les IDs retournés peuvent être utilisés pour les relations
- Les erreurs sont retournées dans le dictionnaire avec `'success': False` et `'error': str`
- Les sessions de base de données doivent être fermées après utilisation
=======
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
>>>>>>> a5a03a993e1b9b43f14c093746cbd6265ba0f65f
