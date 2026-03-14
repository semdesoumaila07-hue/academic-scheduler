# 📝 Changelog - Mise à jour des Permissions

## Date : 2025

### ✅ Modifications effectuées

#### 1. Nouvelles permissions créées
- ✅ `submit_leave` - Soumettre une demande de congés
- ✅ `approve_leave` - Approuver une demande de congés

#### 2. Rôles mis à jour

**ADMIN :**
- ✅ `manage_structure` - Configurer structure universitaire
- ✅ `manage_calendar` - Configurer calendrier académique
- ✅ `generate_reports` - Générer Rapport
- ✅ `analyze_delays` - Consulter Retard Académique
- ✅ `view_dashboard` - Vue du tableau de bord
- ✅ `view_timetable` - Consultation des emplois du temps

**RESPONSABLE PÉDAGOGIQUE :**
- ✅ `manage_activities` - Gérer les activités académiques
- ✅ `launch_scheduling` - Lancer l'ordonnancement Pfair
- ✅ `analyze_delays` - Consulter les retards académiques
- ✅ `approve_leave` - Approuver une demande de congés
- ✅ `view_timetable` - Consulter l'emploi du temps
- ✅ `view_dashboard` - Vue du tableau de bord

**ENSEIGNANT :**
- ✅ `view_timetable` - Consulter les emplois du temps
- ✅ `declare_availability` - Déclarer les disponibilités
- ✅ `submit_leave` - Soumettre une demande de congés
- ✅ `view_dashboard` - Vue du tableau de bord

**ÉTUDIANT :**
- ✅ `view_timetable` - Consulter les emplois du temps
- ✅ `analyze_delays` - Consulter les retards académiques
- ✅ `view_dashboard` - Vue du tableau de bord

#### 3. Méthodes protégées

**LeaveService :**
- ✅ `submit_leave_request()` → `@require_permission('submit_leave')`
- ✅ `approve_leave_request()` → `@require_permission('approve_leave')`

#### 4. Fichiers modifiés

- ✅ `src/scripts/seed_auth.py` - Permissions mises à jour
- ✅ `src/services/permissions_config.py` - Configuration des onglets mise à jour
- ✅ `src/services/leave_service.py` - Décorateurs de permissions ajoutés
- ✅ `src/ui/tabs/leaves_tab.py` - Passage de `current_user` ajouté

#### 5. Scripts créés

- ✅ `scripts/update_permissions.py` - Script pour mettre à jour les permissions existantes
- ✅ `scripts/verify_roles_permissions.py` - Script de vérification

---

## 🔄 Pour appliquer les changements

### Option 1 : Réinitialiser complètement (recommandé pour nouveau projet)

```bash
python src/scripts/seed_auth.py
```

### Option 2 : Mettre à jour les permissions existantes

```bash
python scripts/update_permissions.py
```

### Vérifier les permissions

```bash
python scripts/verify_roles_permissions.py
```

---

## ⚠️ Notes importantes

1. **Utilisateurs existants** : Les utilisateurs existants conservent leurs rôles mais les permissions de ces rôles sont mises à jour
2. **Compatibilité** : L'ancienne permission `manage_leaves` existe toujours mais n'est plus assignée par défaut
3. **Interface** : Les onglets sont automatiquement filtrés selon les nouvelles permissions
4. **Méthodes** : Les méthodes de congés nécessitent maintenant les bonnes permissions et `current_user` doit être passé

---

## 📊 Comparaison avant/après

### Avant
- Admin : Toutes les permissions
- Pedagogical : Presque toutes les permissions
- Teacher : Dashboard + Activités + EDT
- Student : Dashboard + EDT

### Après
- Admin : Structure + Calendrier + Rapports + Retards
- Pedagogical : Activités + Ordonnancement + Retards + Approbation congés + EDT
- Teacher : EDT + Disponibilités + Soumission congés
- Student : EDT + Retards

---

**Status** : ✅ Implémenté et testé
