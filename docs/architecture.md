# 🏗️ Architecture du Système

## Vue d'ensemble

Le **Système d'Ordonnancement Académique P-équitable** est une application modulaire construite selon une architecture en couches avec séparation des responsabilités.

---

## 📐 Architecture Globale

```
┌─────────────────────────────────────────────────┐
│          INTERFACE UTILISATEUR (PyQt5)          │
│              7 onglets + Dialogues              │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  MANAGERS                        │
│   StructureManager │ ActivityManager │          │
│              ScheduleGenerator                   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  SERVICES                        │
│  PfairScheduler │ CalendarService │             │
│  LeaveService   │ DelayCalculator               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              REPOSITORIES (13)                   │
│          Accès aux données (CRUD)                │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│            BASE DE DONNÉES SQLite                │
│              12 tables relationnelles            │
└──────────────────────────────────────────────────┘
```

---

## 🎯 Couches de l'Application

### **1. Interface Utilisateur (UI)**
**Technologie** : PyQt5  
**Responsabilité** : Présentation et interaction utilisateur

**Composants** :
- `MainWindow` : Fenêtre principale avec 7 onglets
- **Dialogues** : TeacherDialog, ActivityDialog, LeaveRequestDialog, ScheduleViewer
- **Widgets** : CalendarWidget, ScheduleGrid

**Flux** :
```
Utilisateur → UI → Manager → Service → Repository → BD
```

---

### **2. Managers (Couche Métier Haut Niveau)**
**Responsabilité** : Orchestration des opérations complexes

**Composants** :

#### **StructureManager**
- Gestion de la structure universitaire
- CRUD pour Universités, UFR, Programmes, Cohortes, Étudiants
- Statistiques globales

#### **ActivityManager**
- Gestion des activités académiques
- Calcul de charge de travail
- Suivi de progression
- Activités urgentes

#### **ScheduleGenerator**
- Génération d'emplois du temps
- Création manuelle de créneaux
- Détection de conflits
- Export et statistiques

---

### **3. Services (Logique Métier)**
**Responsabilité** : Algorithmes et logique métier complexe

**Composants** :

#### **PfairScheduler** 🔥
- **Algorithme Pfair** complet
- Calcul de U(τi), lag, α
- Test de faisabilité
- Génération automatique d'emplois du temps

**Formules** :
```
U(τi) = Ci / D_effectif
lag(τi, t) = U(τi) × t - H(t)
α(τi, t) = lag / U(τi)
```

#### **CalendarService**
- Calcul de jours ouvrables
- Gestion jours fériés et vacances
- Validation de dates

#### **LeaveService**
- Workflow de demandes de congés
- Approbation/Rejet
- Blocage automatique de créneaux

#### **DelayCalculator**
- Calcul des retards par activité
- Calcul des retards par cohorte
- Identification activités urgentes
- Prévision de complétion

---

### **4. Validators**
**Responsabilité** : Validation et vérification

**Composants** :

#### **ScheduleValidator**
- Validation créneaux horaires
- Validation dates
- Validation charge enseignants
- Cohérence globale

#### **LeaveValidator**
- Validation demandes de congés
- Vérification chevauchements
- Impact sur emploi du temps

#### **ConflictDetector**
- Détection conflits enseignants
- Détection conflits cohortes
- Détection conflits salles
- Recherche créneaux disponibles

---

### **5. Repositories (Accès aux Données)**
**Responsabilité** : Abstraction de la base de données

**Pattern** : Repository Pattern avec CRUD générique

**13 Repositories** :
1. UniversityRepository
2. UFRRepository
3. ProgramRepository
4. CohortRepository
5. TeacherRepository
6. StudentRepository
7. ActivityRepository
8. ScheduleRepository
9. LeaveRequestRepository
10. CalendarRepository
11. HolidayRepository
12. VacationPeriodRepository
13. BaseRepository (générique)

**Opérations CRUD** :
- `create()` - Créer
- `get_by_id()` - Lire
- `update()` - Mettre à jour
- `delete()` - Supprimer
- `get_all()` - Lister
- Méthodes métier spécifiques

---

### **6. Entités (Modèles Métier)**
**Responsabilité** : Représentation des concepts métier

**12 Entités** :
1. University
2. UFR
3. Program
4. Cohort
5. Teacher
6. Student
7. AcademicActivity (avec paramètres Pfair)
8. ScheduleSlot
9. LeaveRequest
10. AcademicCalendar
11. Holiday
12. VacationPeriod

**Caractéristiques** :
- Validation métier
- Calculs intégrés
- Indépendantes de la BD

---

### **7. Base de Données**
**Technologie** : SQLite + SQLAlchemy ORM

**12 Tables** :
- `universities`
- `ufrs`
- `programs`
- `cohorts`
- `teachers`
- `students`
- `academic_activities`
- `schedule_slots`
- `leave_requests`
- `academic_calendars`
- `holidays`
- `vacation_periods`

**Caractéristiques** :
- Clés étrangères avec CASCADE
- Indexes sur colonnes fréquentes
- Contraintes CHECK
- Optimisations SQLite (WAL mode)

---

## 🔄 Flux de Données

### **Exemple : Génération d'Emploi du Temps**

```
1. Utilisateur clique "Générer Emploi du Temps"
   ↓
2. MainWindow.on_generate_schedule()
   ↓
3. ScheduleGenerator.generate_schedule()
   ↓
4. PfairScheduler.schedule_cohort()
   ├── CalendarService.calculate_effective_days()
   ├── ActivityRepository.get_by_cohort()
   ├── Pour chaque jour :
   │   ├── Calcul α pour toutes activités
   │   ├── Tri par α décroissant
   │   ├── ConflictDetector.check_conflicts()
   │   └── ScheduleRepository.create()
   └── Retour résultat
   ↓
5. Affichage résultat dans UI
```

---

## 🎨 Patterns de Conception

### **Repository Pattern**
```python
class BaseRepository:
    def create(self, **kwargs): ...
    def get_by_id(self, id): ...
    def update(self, id, **kwargs): ...
    def delete(self, id): ...
```

### **Service Pattern**
```python
class PfairScheduler:
    def __init__(self, session):
        self.activity_repo = ActivityRepository(session)
        self.schedule_repo = ScheduleRepository(session)
```

### **Manager Pattern**
```python
class ScheduleGenerator:
    def __init__(self, session):
        self.pfair_scheduler = PfairScheduler(session)
        self.calendar_service = CalendarService(session)
```

### **Validator Pattern**
```python
class ScheduleValidator:
    @staticmethod
    def validate_time_slot(start, end):
        # Validation stateless
```

---

## 📦 Modules Transversaux

### **Configuration**
- `config/app_config.json` - Configuration globale
- `config/algorithm_params.json` - Paramètres Pfair
- `ConfigLoader` - Chargement dynamique

### **Logging**
- Logs structurés par niveau
- 4 fichiers de log (app, errors, database, pfair)
- Rotation automatique

### **Exporters**
- `PDFExporter` - Export PDF
- `ExcelExporter` - Export Excel
- `ReportGenerator` - Rapports analytiques

### **Utilitaires**
- `constants.py` - Enums et constantes
- `helpers.py` - Fonctions utilitaires

---

## 🔐 Sécurité et Fiabilité

### **Validation**
- Validation à tous les niveaux (UI, Entités, Services)
- Détection de conflits automatique
- Contraintes de base de données

### **Transactions**
- Utilisation de transactions SQLAlchemy
- Rollback automatique en cas d'erreur
- Cohérence des données garantie

### **Logs**
- Traçabilité complète des opérations
- Logs d'erreurs détaillés
- Facilite le debugging

### **Sauvegardes**
- Sauvegardes automatiques
- Rotation des backups (max 10)
- Restauration simple

---

## 🚀 Performance

### **Optimisations Base de Données**
- Mode WAL (Write-Ahead Logging)
- Cache de 64MB
- Indexes sur colonnes clés

### **Lazy Loading**
- Chargement à la demande
- Pagination des résultats

### **Caching**
- Configuration en cache
- Facteurs de charge mis en cache

---

## 🧪 Testabilité

### **Architecture Testable**
- Injection de dépendances
- Mocking des repositories
- Tests unitaires par couche

### **Tests**
- Tests unitaires (entités, services, validators)
- Tests d'intégration
- Fixtures pytest

---

## 📊 Diagramme de Classes (Simplifié)

```
┌────────────────┐
│   MainWindow   │
└───────┬────────┘
        │
┌───────▼────────┐     ┌──────────────┐
│ScheduleGenerator├────►│PfairScheduler│
└───────┬────────┘     └──────┬───────┘
        │                     │
┌───────▼────────┐     ┌──────▼───────┐
│ActivityManager │     │CalendarService│
└───────┬────────┘     └──────────────┘
        │
┌───────▼────────────┐
│ ActivityRepository │
└───────┬────────────┘
        │
┌───────▼────────┐
│    Database    │
└────────────────┘
```

---

## 🎯 Principes de Design

### **SOLID**
- **S**ingle Responsibility : Chaque classe a une responsabilité unique
- **O**pen/Closed : Ouvert à l'extension, fermé à la modification
- **L**iskov Substitution : Repositories interchangeables
- **I**nterface Segregation : Interfaces spécifiques
- **D**ependency Inversion : Dépendances via abstractions

### **DRY** (Don't Repeat Yourself)
- BaseRepository pour CRUD générique
- ConfigLoader centralisé
- Utilitaires réutilisables

### **Separation of Concerns**
- UI séparée de la logique métier
- Services séparés des données
- Validation isolée

---

## 📈 Évolutivité

### **Ajout de Fonctionnalités**
- Nouveau service → Créer dans `services/`
- Nouveau repository → Hériter de `BaseRepository`
- Nouvelle entité → Ajouter modèle + repository

### **Extensions Possibles**
- Support multi-utilisateurs
- API REST
- Application mobile
- Notifications par email
- Export vers Google Calendar
- Intégration avec systèmes existants

---

## 🔧 Technologies Utilisées

| Couche | Technologie |
|--------|-------------|
| Interface | PyQt5 |
| Base de données | SQLite + SQLAlchemy |
| Export PDF | ReportLab |
| Export Excel | openpyxl + pandas |
| Tests | pytest |
| Logging | Python logging |
| Configuration | JSON |

---

Cette architecture garantit :
- ✅ **Maintenabilité** : Code organisé et modulaire
- ✅ **Testabilité** : Tests à tous les niveaux
- ✅ **Évolutivité** : Facile d'ajouter des fonctionnalités
- ✅ **Performance** : Optimisations ciblées
- ✅ **Fiabilité** : Validation et logs complets