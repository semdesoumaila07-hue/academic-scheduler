# 🔐 Rôles et Permissions - Système d'Ordonnancement Académique

Documentation complète des rôles et permissions du système.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Rôles disponibles](#rôles-disponibles)
3. [Permissions disponibles](#permissions-disponibles)
4. [Matrice des permissions par rôle](#matrice-des-permissions-par-rôle)
5. [Fonctionnalités protégées](#fonctionnalités-protégées)
6. [Gestion des permissions](#gestion-des-permissions)

---

## Vue d'ensemble

Le système utilise un modèle **RBAC (Role-Based Access Control)** avec :
- **Rôles** : Groupes d'utilisateurs (Admin, Responsable pédagogique, Enseignant, Étudiant)
- **Permissions** : Actions spécifiques (manage_structure, manage_activities, etc.)
- **Décorateurs** : `@require_permission` et `@require_role` pour protéger les méthodes

---

## Rôles disponibles

### 1. **Admin** (Administrateur)
- **Description** : Accès complet à toutes les fonctionnalités
- **Utilisateurs** : Administrateurs système
- **Permissions** : Toutes les permissions

### 2. **Pedagogical** (Responsable pédagogique)
- **Description** : Gestion complète de la pédagogie et de l'ordonnancement
- **Utilisateurs** : Responsables pédagogiques, Directeurs d'UFR
- **Permissions** : Gestion de la structure, activités, calendrier, ordonnancement, rapports

### 3. **Teacher** (Enseignant)
- **Description** : Accès limité pour consulter et gérer ses activités
- **Utilisateurs** : Enseignants
- **Permissions** : Vue du dashboard, gestion de ses activités, consultation des emplois du temps

### 4. **Student** (Étudiant)
- **Description** : Consultation uniquement
- **Utilisateurs** : Étudiants
- **Permissions** : Vue du dashboard, consultation des emplois du temps

---

## Permissions disponibles

| Permission | Description | Onglet/Fonctionnalité |
|------------|-------------|----------------------|
| `view_dashboard` | Voir le tableau de bord | 📊 Dashboard |
| `manage_structure` | Gérer la structure universitaire | 🏛️ Structure |
| `manage_teachers` | Gérer les enseignants | 👨‍🏫 Enseignants |
| `manage_activities` | Créer et modifier les activités | 📚 Activités |
| `manage_calendar` | Gérer le calendrier académique | 📅 Calendrier |
| `manage_leaves` | Gérer les congés | 🏖️ Congés |
| `launch_scheduling` | Lancer l'ordonnancement automatique | ⏰ Ordonnancement |
| `validate_schedule` | Valider les plannings générés | ⏰ Ordonnancement |
| `analyze_delays` | Analyser les retards et indicateurs | ⏱️ Retards |
| `adjust_schedule` | Ajustements manuels du planning | ⏰ Ordonnancement |
| `generate_reports` | Générer les rapports | 📈 Rapports |
| `view_timetable` | Voir les emplois du temps | 🗓️ Emplois du temps |
| `declare_availability` | Déclarer ses disponibilités | 🕒 Disponibilités |

---

## Matrice des permissions par rôle

| Permission | Admin | Pedagogical | Teacher | Student |
|------------|:-----:|:-----------:|:-------:|:-------:|
| `view_dashboard` | ✅ | ✅ | ✅ | ✅ |
| `manage_structure` | ✅ | ✅ | ❌ | ❌ |
| `manage_teachers` | ✅ | ✅ | ❌ | ❌ |
| `manage_activities` | ✅ | ✅ | ✅ | ❌ |
| `manage_calendar` | ✅ | ✅ | ❌ | ❌ |
| `manage_leaves` | ✅ | ✅ | ❌ | ❌ |
| `launch_scheduling` | ✅ | ✅ | ❌ | ❌ |
| `validate_schedule` | ✅ | ✅ | ❌ | ❌ |
| `analyze_delays` | ✅ | ✅ | ❌ | ❌ |
| `adjust_schedule` | ✅ | ✅ | ❌ | ❌ |
| `generate_reports` | ✅ | ✅ | ❌ | ❌ |
| `view_timetable` | ✅ | ✅ | ✅ | ✅ |
| `declare_availability` | ✅ | ✅ | ✅ | ❌ |

---

## Fonctionnalités protégées

### StructureManager

Les méthodes suivantes nécessitent la permission `manage_structure` :

- ✅ `create_university()` - Créer une université
- ✅ `create_ufr()` - Créer une UFR
- ✅ `create_program()` - Créer un programme
- ✅ `create_cohort()` - Créer une cohorte
- ✅ `create_student()` - Créer un étudiant

**Rôles autorisés** : Admin, Pedagogical

### ActivityManager

Les méthodes suivantes nécessitent la permission `manage_activities` :

- ✅ `create_activity()` - Créer une activité académique
- ✅ `update_activity()` - Modifier une activité

**Rôles autorisés** : Admin, Pedagogical, Teacher

**Note** : Les enseignants peuvent créer/modifier leurs propres activités uniquement (vérification du périmètre).

### ScheduleGenerator

Les méthodes suivantes nécessitent des permissions spécifiques :

- ✅ `generate_schedule()` - Nécessite `launch_scheduling`
- ✅ `adjust_schedule()` - Nécessite `adjust_schedule`

**Rôles autorisés** : Admin, Pedagogical

---

## Détails par onglet

### 📊 Dashboard
- **Permission** : `view_dashboard`
- **Accès** : Tous les rôles
- **Fonctionnalités** :
  - Vue d'ensemble des KPIs
  - Activités récentes
  - Progression globale

### 🏛️ Structure
- **Permission** : `manage_structure`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Créer/modifier/supprimer Universités
  - Créer/modifier/supprimer UFR
  - Créer/modifier/supprimer Programmes
  - Créer/modifier/supprimer Cohortes
  - Créer/modifier/supprimer Étudiants

### 👨‍🏫 Enseignants
- **Permission** : `manage_teachers`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Créer/modifier/supprimer Enseignants
  - Gérer les disponibilités
  - Gérer les contraintes

### 📚 Activités
- **Permission** : `manage_activities`
- **Accès** : Admin, Pedagogical, Teacher
- **Fonctionnalités** :
  - Créer/modifier/supprimer Activités
  - Assigner des enseignants
  - Définir les volumes horaires
  - Gérer les priorités

**Note pour les enseignants** : Peuvent créer/modifier uniquement leurs propres activités.

### 📅 Calendrier
- **Permission** : `manage_calendar`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Gérer les jours fériés
  - Gérer les périodes de vacances
  - Calculer les jours ouvrables

### 🏖️ Congés
- **Permission** : `manage_leaves`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Soumettre des demandes de congés
  - Approuver/rejeter les demandes
  - Consulter les congés

### ⏰ Ordonnancement
- **Permissions** : `launch_scheduling`, `validate_schedule`, `adjust_schedule`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Lancer l'ordonnancement automatique (Pfair)
  - Valider les plannings générés
  - Ajuster manuellement le planning

### ⏱️ Retards
- **Permission** : `analyze_delays`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Analyser les retards par activité
  - Calculer les ratios d'urgence
  - Visualiser les indicateurs

### 📈 Rapports
- **Permission** : `generate_reports`
- **Accès** : Admin, Pedagogical
- **Fonctionnalités** :
  - Générer des rapports PDF
  - Générer des rapports Excel
  - Exporter les données

### 🗓️ Emplois du temps
- **Permission** : `view_timetable`
- **Accès** : Tous les rôles
- **Fonctionnalités** :
  - Consulter les emplois du temps
  - Filtrer par cohorte/enseignant
  - Exporter en PDF/Excel

### 🕒 Disponibilités
- **Permission** : `declare_availability`
- **Accès** : Admin, Pedagogical, Teacher
- **Fonctionnalités** :
  - Déclarer ses disponibilités
  - Gérer les créneaux disponibles

---

## Gestion des permissions

### Vérification des permissions dans le code

#### Décorateur `@require_permission`

```python
from src.services.auth_service import require_permission

@require_permission('manage_activities')
def create_activity(self, ...):
    # Code de création d'activité
    pass
```

#### Vérification manuelle

```python
from src.services.auth_service import _has_permission

if _has_permission(current_user, 'manage_structure'):
    # Code autorisé
    pass
```

### Vérification dans l'interface

L'interface PyQt5 filtre automatiquement les onglets selon les permissions :

```python
from src.services.permissions_config import get_allowed_tab_indices

allowed_tabs = get_allowed_tab_indices(current_user)
# Affiche uniquement les onglets autorisés
```

### Périmètres UFR/Programme

Les utilisateurs non-admin peuvent être limités à leur UFR ou Programme :

- `UserModel.ufr_id` : Limite à une UFR spécifique
- `UserModel.program_id` : Limite à un programme spécifique

**Exemple** : Un responsable pédagogique d'une UFR ne peut gérer que les activités de son UFR.

---

## Utilisateurs par défaut

Après l'exécution de `seed_auth.py`, les utilisateurs suivants sont créés :

| Username | Mot de passe | Rôle |
|----------|--------------|------|
| `admin` | `AdminPass123` | Admin |
| `pedagog` | `PedagogPass123` | Pedagogical |
| `enseignant` | `EnseignantPass123` | Teacher |
| `etudiant` | `EtudiantPass123` | Student |

---

## Exemples d'utilisation

### Créer un utilisateur avec un rôle

```python
from src.services.auth_service import create_user
from src.database.repositories import UserRepository, RoleRepository

session = db_manager.get_session()
user_repo = UserRepository(session)
role_repo = RoleRepository(session)

# Créer l'utilisateur
user = create_user('nouveau_user', 'user@example.com', 'password123', session)

# Assigner un rôle
role = role_repo.get_by_name('Teacher')
user_repo.add_role(user, role)
session.commit()
```

### Vérifier les permissions d'un utilisateur

```python
from src.services.auth_service import AuthService

auth_service = AuthService(session)

# Vérifier une permission
if auth_service.has_permission(user, 'manage_activities'):
    print("L'utilisateur peut gérer les activités")

# Vérifier un rôle
if auth_service.has_role(user, 'Admin'):
    print("L'utilisateur est administrateur")
```

### Obtenir toutes les permissions d'un utilisateur

```python
from src.services.permissions_config import get_user_permission_names

permissions = get_user_permission_names(user)
print(f"Permissions: {permissions}")
```

---

## 🔒 Sécurité

### Bonnes pratiques

1. **Toujours vérifier les permissions** avant d'exécuter une action sensible
2. **Utiliser les décorateurs** `@require_permission` pour protéger les méthodes
3. **Vérifier les périmètres** pour les utilisateurs non-admin
4. **Ne jamais exposer les mots de passe** en clair
5. **Valider les entrées** utilisateur avant traitement

### Limitations

- Les permissions sont vérifiées au niveau applicatif
- Les requêtes SQL directes contournent les vérifications
- Les sessions doivent être correctement gérées

---

## 📝 Notes importantes

1. **Admin a tous les droits** : Le rôle Admin ignore toutes les vérifications de périmètre
2. **Périmètres UFR/Programme** : Les utilisateurs non-admin sont limités à leur périmètre
3. **Permissions multiples** : Un utilisateur peut avoir plusieurs rôles
4. **Héritage** : Les permissions sont héritées via les rôles

---

## 🔄 Mise à jour des permissions

Pour ajouter une nouvelle permission :

1. Ajouter la permission dans `seed_auth.py`
2. L'assigner aux rôles appropriés
3. Protéger les méthodes avec `@require_permission`
4. Ajouter l'onglet dans `permissions_config.py` si nécessaire

---

## ✅ Checklist de vérification

- [ ] Tous les rôles sont correctement définis
- [ ] Les permissions sont assignées aux bons rôles
- [ ] Les méthodes sensibles sont protégées
- [ ] L'interface filtre les onglets selon les permissions
- [ ] Les périmètres UFR/Programme sont vérifiés
- [ ] Les utilisateurs par défaut sont créés

---

**Dernière mise à jour** : 2025
