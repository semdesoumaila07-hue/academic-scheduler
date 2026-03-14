# 📋 Résumé des Rôles et Permissions

## 🎯 Vue d'ensemble rapide

| Rôle | Accès | Description |
|------|-------|-------------|
| **Admin** | 🔓 Complet | Toutes les fonctionnalités |
| **Pedagogical** | 📚 Pédagogie | Gestion complète sauf administration système |
| **Teacher** | 👨‍🏫 Limité | Ses activités + consultation |
| **Student** | 👁️ Lecture seule | Consultation uniquement |

---

## 📊 Permissions par onglet

| Onglet | Permission | Admin | Pedagogical | Teacher | Student |
|--------|------------|:-----:|:-----------:|:-------:|:-------:|
| 📊 Dashboard | `view_dashboard` | ✅ | ✅ | ✅ | ✅ |
| 🏛️ Structure | `manage_structure` | ✅ | ✅ | ❌ | ❌ |
| 👨‍🏫 Enseignants | `manage_teachers` | ✅ | ✅ | ❌ | ❌ |
| 📚 Activités | `manage_activities` | ✅ | ✅ | ✅* | ❌ |
| 📅 Calendrier | `manage_calendar` | ✅ | ✅ | ❌ | ❌ |
| 🏖️ Congés | `manage_leaves` | ✅ | ✅ | ❌ | ❌ |
| ⏰ Ordonnancement | `launch_scheduling` | ✅ | ✅ | ❌ | ❌ |
| ⏱️ Retards | `analyze_delays` | ✅ | ✅ | ❌ | ❌ |
| 📈 Rapports | `generate_reports` | ✅ | ✅ | ❌ | ❌ |
| 🗓️ Emplois du temps | `view_timetable` | ✅ | ✅ | ✅ | ✅ |

*Les enseignants peuvent créer/modifier uniquement leurs propres activités.

---

## 🔐 Méthodes protégées

### StructureManager
- `create_university()` → `manage_structure`
- `create_ufr()` → `manage_structure`
- `create_program()` → `manage_structure`
- `create_cohort()` → `manage_structure`
- `create_student()` → `manage_structure`

### ActivityManager
- `create_activity()` → `manage_activities`
- `update_activity()` → `manage_activities`

### ScheduleGenerator
- `generate_schedule()` → `launch_scheduling`
- `adjust_schedule()` → `adjust_schedule`

---

## ✅ Vérification

Pour vérifier les rôles et permissions :

```bash
python scripts/verify_roles_permissions.py
```

Pour créer les rôles et permissions par défaut :

```bash
python src/scripts/seed_auth.py
```

---

## 📝 Utilisateurs par défaut

| Username | Mot de passe | Rôle |
|----------|--------------|------|
| `admin` | `AdminPass123` | Admin |
| `pedagog` | `PedagogPass123` | Pedagogical |
| `enseignant` | `EnseignantPass123` | Teacher |
| `etudiant` | `EtudiantPass123` | Student |

---

Voir la documentation complète : `docs/ROLES_ET_PERMISSIONS.md`
