# ✅ Mise à jour des Permissions - Spécifications Recommandées

## 📋 Nouvelle Configuration des Rôles

Les permissions ont été mises à jour selon les spécifications recommandées.

---

## 🔐 ADMIN (Administrateur)

### Permissions assignées :
1. ✅ **Configurer structure universitaire** (`manage_structure`)
2. ✅ **Configurer calendrier académique** (`manage_calendar`)
3. ✅ **Générer Rapport** (`generate_reports`)
4. ✅ **Consulter Retard Académique** (`analyze_delays`)

### Permissions supplémentaires :
- `view_dashboard` - Vue du tableau de bord
- `view_timetable` - Consultation des emplois du temps

### Onglets accessibles :
- 📊 Dashboard
- 🏛️ Structure
- 📅 Calendrier
- ⏱️ Retards
- 📈 Rapports
- 🗓️ Emplois du temps

---

## 👨‍🏫 RESPONSABLE PÉDAGOGIQUE (Pedagogical)

### Permissions assignées :
1. ✅ **Gérer les activités académiques** (`manage_activities`)
2. ✅ **Lancer l'ordonnancement Pfair** (`launch_scheduling`)
3. ✅ **Consulter les retards académiques** (`analyze_delays`)
4. ✅ **Approuver une demande de congés** (`approve_leave`)
5. ✅ **Consulter l'emploi du temps** (`view_timetable`)

### Permissions supplémentaires :
- `view_dashboard` - Vue du tableau de bord

### Onglets accessibles :
- 📊 Dashboard
- 📚 Activités
- ⏰ Ordonnancement
- ⏱️ Retards
- 🏖️ Congés (pour approuver)
- 🗓️ Emplois du temps

---

## 🎓 ENSEIGNANT (Teacher)

### Permissions assignées :
1. ✅ **Consulter les emplois du temps** (`view_timetable`)
2. ✅ **Déclarer les disponibilités** (`declare_availability`)
3. ✅ **Soumettre une demande de congés** (`submit_leave`)

### Permissions supplémentaires :
- `view_dashboard` - Vue du tableau de bord

### Onglets accessibles :
- 📊 Dashboard
- 🗓️ Emplois du temps
- 🕒 Disponibilités
- 📝 Demander congé (nouvel onglet)

---

## 🎒 ÉTUDIANT (Student)

### Permissions assignées :
1. ✅ **Consulter les emplois du temps** (`view_timetable`)
2. ✅ **Consulter les retards académiques** (`analyze_delays`)

### Permissions supplémentaires :
- `view_dashboard` - Vue du tableau de bord

### Onglets accessibles :
- 📊 Dashboard
- 🗓️ Emplois du temps
- ⏱️ Retards

---

## 🔄 Changements effectués

### 1. Nouvelles permissions créées :
- `submit_leave` - Soumettre une demande de congés
- `approve_leave` - Approuver une demande de congés

### 2. Permissions modifiées :
- `manage_leaves` → divisée en `submit_leave` et `approve_leave` pour plus de granularité

### 3. Méthodes protégées :
- `LeaveService.submit_leave_request()` → `@require_permission('submit_leave')`
- `LeaveService.approve_leave_request()` → `@require_permission('approve_leave')`

### 4. Onglets mis à jour :
- Onglet "Congés" → visible uniquement pour Admin et Responsable pédagogique (approbation)
- Nouvel onglet "Demander congé" → visible pour les enseignants (soumission)

---

## 📊 Matrice des permissions (après mise à jour)

| Permission | Admin | Pedagogical | Teacher | Student |
|------------|:-----:|:-----------:|:-------:|:-------:|
| `view_dashboard` | ✅ | ✅ | ✅ | ✅ |
| `manage_structure` | ✅ | ❌ | ❌ | ❌ |
| `manage_calendar` | ✅ | ❌ | ❌ | ❌ |
| `generate_reports` | ✅ | ❌ | ❌ | ❌ |
| `analyze_delays` | ✅ | ✅ | ❌ | ✅ |
| `manage_activities` | ❌ | ✅ | ❌ | ❌ |
| `launch_scheduling` | ❌ | ✅ | ❌ | ❌ |
| `approve_leave` | ❌ | ✅ | ❌ | ❌ |
| `view_timetable` | ✅ | ✅ | ✅ | ✅ |
| `declare_availability` | ❌ | ❌ | ✅ | ❌ |
| `submit_leave` | ❌ | ❌ | ✅ | ❌ |

---

## 🚀 Application des changements

Pour appliquer les nouvelles permissions :

```bash
# 1. Réinitialiser les permissions
python src/scripts/seed_auth.py

# 2. Vérifier les permissions
python scripts/verify_roles_permissions.py
```

---

## ⚠️ Notes importantes

1. **Permissions existantes** : Les utilisateurs existants doivent être réassignés aux nouveaux rôles
2. **Onglets cachés** : Les onglets non autorisés seront automatiquement cachés dans l'interface
3. **Compatibilité** : Les anciennes permissions (`manage_leaves`) sont conservées pour compatibilité mais ne sont plus assignées par défaut
4. **Méthodes protégées** : Les méthodes de congés nécessitent maintenant les bonnes permissions

---

## ✅ Vérification

Après avoir exécuté `seed_auth.py`, vérifiez que :

- [ ] Admin a uniquement les 4 permissions spécifiées
- [ ] Responsable pédagogique a les 5 permissions spécifiées
- [ ] Enseignant a les 3 permissions spécifiées
- [ ] Étudiant a les 2 permissions spécifiées
- [ ] Les méthodes de congés sont protégées
- [ ] Les onglets sont correctement filtrés dans l'interface

---

**Date de mise à jour** : 2025
