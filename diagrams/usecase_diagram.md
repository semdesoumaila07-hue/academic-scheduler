# 🎯 Diagramme de Cas d'Utilisation

## Vue d'ensemble

Ce document décrit tous les cas d'utilisation du système d'ordonnancement académique.

---

## 👥 Acteurs

### **Acteur Principal**
- **👨‍💼 Administrateur** : Gère tout le système

### **Acteurs Secondaires**
- **👨‍🏫 Enseignant** : Consulte emploi du temps, demande congés
- **👨‍🎓 Étudiant** : Consulte emploi du temps

---

## 🎯 Cas d'Utilisation Principaux

```
                    ┌─────────────────────────────────┐
                    │  Système d'Ordonnancement      │
                    │         Académique             │
                    └─────────────────────────────────┘

┌──────────────┐
│Administrateur│
│      👨‍💼      │
└──────┬───────┘
       │
       │──────────► (Gérer Structure Universitaire)
       │                      │
       │                      ├─► (Créer Université)
       │                      ├─► (Créer UFR)
       │                      ├─► (Créer Programme)
       │                      └─► (Créer Cohorte)
       │
       │──────────► (Gérer Enseignants)
       │                      │
       │                      ├─► (Ajouter Enseignant)
       │                      ├─► (Modifier Enseignant)
       │                      └─► (Supprimer Enseignant)
       │
       │──────────► (Gérer Activités)
       │                      │
       │                      ├─► (Créer Activité)
       │                      ├─► (Assigner Enseignant)
       │                      ├─► (Voir Activités Urgentes)
       │                      └─► (Calculer Retards)
       │
       │──────────► (Générer Emploi du Temps) ⭐
       │                      │
       │                      ├─► (Tester Faisabilité)
       │                      ├─► (Exécuter Algorithme Pfair)
       │                      ├─► (Détecter Conflits)
       │                      └─► (Créer Créneaux)
       │
       │──────────► (Modifier Emploi du Temps)
       │                      │
       │                      ├─► (Créer Créneau Manuel)
       │                      ├─► (Supprimer Créneau)
       │                      └─► (Résoudre Conflits)
       │
       │──────────► (Gérer Congés)
       │                      │
       │                      ├─► (Approuver Demande)
       │                      ├─► (Rejeter Demande)
       │                      └─► (Voir Demandes Pendantes)
       │
       │──────────► (Configurer Calendrier)
       │                      │
       │                      ├─► (Ajouter Jour Férié)
       │                      └─► (Ajouter Vacances)
       │
       │──────────► (Exporter Données)
       │                      │
       │                      ├─► (Exporter PDF)
       │                      ├─► (Exporter Excel)
       │                      └─► (Générer Rapports)
       │
       └──────────► (Voir Statistiques)

┌──────────────┐
│  Enseignant  │
│     👨‍🏫      │
└──────┬───────┘
       │
       │──────────► (Consulter Emploi du Temps)
       │
       │──────────► (Demander Congé)
       │                      │
       │                      ├─► (Soumettre Demande)
       │                      ├─► (Annuler Demande)
       │                      └─► (Voir Statut Demandes)
       │
       └──────────► (Voir Activités Assignées)

┌──────────────┐
│   Étudiant   │
│     👨‍🎓      │
└──────┬───────┘
       │
       └──────────► (Consulter Emploi du Temps)
```

---

## 📋 Description Détaillée des Cas d'Utilisation

### **CU01 : Créer Université**

**Acteur** : Administrateur  
**Préconditions** : Aucune  
**Postconditions** : Université créée dans le système

**Scénario principal** :
1. L'admin clique sur "Nouvelle Université"
2. Le système affiche le formulaire
3. L'admin remplit les champs (nom, code, adresse, ville, pays)
4. L'admin clique "Enregistrer"
5. Le système valide les données
6. Le système crée l'université
7. Le système affiche un message de succès

**Scénarios alternatifs** :
- 5a. Données invalides → Afficher erreurs
- 5b. Code déjà existant → Afficher erreur de duplication

---

### **CU02 : Générer Emploi du Temps (Pfair)** ⭐

**Acteur** : Administrateur  
**Préconditions** :
- Au moins une cohorte existe
- Des activités sont créées pour la cohorte
- Des enseignants sont assignés

**Postconditions** :
- Emploi du temps généré
- Créneaux horaires créés

**Scénario principal** :
1. L'admin sélectionne une cohorte
2. L'admin définit la période (date début, date fin)
3. L'admin spécifie les salles disponibles
4. L'admin clique "Générer Emploi du Temps (Pfair)"
5. **Le système teste la faisabilité** (U ≤ 1.0)
6. **Le système calcule D_effectif**
7. **Le système calcule U(τi) pour chaque activité**
8. **Pour chaque jour ouvrable :**
   - Calcule α(τi, t) pour chaque activité
   - Identifie les activités urgentes (α ≥ 1)
   - Trie par α décroissant
   - Crée les créneaux horaires
   - Vérifie les conflits
   - Assigne les salles
9. Le système affiche les résultats
10. Le système affiche les statistiques

**Scénarios alternatifs** :
- 5a. **U > 1.0** → Afficher "Impossible à ordonnancer"
- 8a. **Conflit détecté** → Afficher conflits et proposer résolution
- 8b. **Pas de salle disponible** → Alerter l'admin

**Règles métier** :
- U = Σ U(τi) ≤ 1.0 (faisabilité)
- α ≥ 1.0 → Activité urgente (priorité)
- Créneaux entre 7h et 20h
- Durée créneaux : 30min - 4h
- Respect limites enseignants

---

### **CU03 : Soumettre Demande de Congé**

**Acteur** : Enseignant  
**Préconditions** : Enseignant connecté

**Scénario principal** :
1. L'enseignant clique "Nouvelle Demande"
2. Le système affiche le formulaire
3. L'enseignant remplit :
   - Type de congé
   - Date début
   - Date fin
   - Raison
4. L'enseignant clique "Soumettre"
5. **Le système valide la demande**
6. **Le système vérifie les chevauchements**
7. **Le système calcule l'impact sur l'emploi du temps**
8. Le système crée la demande (statut: EN_ATTENTE)
9. Le système envoie notification à l'admin

**Scénarios alternatifs** :
- 6a. **Chevauchement détecté** → Afficher erreur
- 7a. **Impact important** → Alerter enseignant et admin

---

### **CU04 : Approuver Demande de Congé**

**Acteur** : Administrateur  
**Préconditions** : Demande en attente

**Scénario principal** :
1. L'admin voit la liste des demandes pendantes
2. L'admin sélectionne une demande
3. L'admin clique "Approuver"
4. **Le système bloque les créneaux de l'enseignant**
5. Le système change le statut à APPROVED
6. Le système envoie notification à l'enseignant

**Postconditions** :
- Demande approuvée
- Créneaux bloqués automatiquement

---

### **CU05 : Détecter Conflits**

**Acteur** : Système (automatique)  
**Déclencheur** : Création/Modification de créneau

**Scénario principal** :
1. Un créneau est créé/modifié
2. **Le système vérifie les conflits enseignants**
3. **Le système vérifie les conflits cohortes**
4. **Le système vérifie les conflits salles**
5. Le système retourne les résultats

**Types de conflits** :
- **TEACHER_CONFLICT** : Enseignant a 2 cours simultanés
- **COHORT_CONFLICT** : Cohorte a 2 cours simultanés
- **ROOM_CONFLICT** : Salle occupée 2 fois

---

### **CU06 : Calculer Retards**

**Acteur** : Système (automatique ou manuel)  
**Déclencheur** : Demande de statistiques

**Scénario principal** :
1. Le système sélectionne une activité
2. **Calcule U(τi) = Ci / D_effectif**
3. **Calcule t (jours écoulés)**
4. **Calcule lag = U × t - H(t)**
5. **Calcule α = lag / U**
6. **Détermine urgence** :
   - α ≥ 1.0 → Critique
   - α ≥ 0.5 → Urgent
   - α < 0.5 → Normal
7. Retourne les métriques

---

### **CU07 : Exporter en PDF**

**Acteur** : Administrateur  
**Préconditions** : Emploi du temps généré

**Scénario principal** :
1. L'admin clique "Exporter PDF"
2. Le système génère le PDF (format A4 paysage)
3. Le système organise par semaines
4. Le système crée la grille hebdomadaire
5. Le système sauvegarde dans outputs/schedules/
6. Le système affiche le chemin du fichier

---

## 🔗 Relations entre Cas d'Utilisation

### **Include (Obligatoire)**
```
(Générer Emploi du Temps)
    «include» → (Tester Faisabilité)
    «include» → (Calculer D_effectif)
    «include» → (Calculer Facteurs de Charge)
    «include» → (Détecter Conflits)
```

### **Extend (Optionnel)**
```
(Créer Créneau Manuel)
    «extend» → (Générer Emploi du Temps)
    
(Résoudre Conflits)
    «extend» → (Détecter Conflits)
```

### **Généralisation**
```
(Exporter PDF)  ╲
(Exporter Excel) ├─→ (Exporter Données)
(Générer Rapport) ╱
```

---

## 🎯 Priorités

| Priorité | Cas d'Utilisation |
|----------|-------------------|
| **Critique** | CU02 - Générer Emploi du Temps |
| **Haute** | CU01 - Gérer Structure |
| **Haute** | CU04 - Gérer Activités |
| **Moyenne** | CU03 - Gérer Congés |
| **Moyenne** | CU07 - Exporter |
| **Basse** | CU08 - Statistiques |

---

## 📊 Fréquence d'Utilisation

| Cas d'Utilisation | Fréquence |
|-------------------|-----------|
| Consulter EDT | Quotidienne |
| Générer EDT | Mensuelle/Semestrielle |
| Demander Congé | Hebdomadaire |
| Créer Activité | Hebdomadaire |
| Exporter PDF | Mensuelle |

---

## 📝 Notes pour Draw.io

Pour créer le diagramme :
1. Utiliser les formes ovales pour les cas d'utilisation
2. Stick figures pour les acteurs
3. Rectangle pour le système
4. Flèches avec labels pour les relations
5. Couleurs :
   - Acteurs : Bleu
   - CU Critiques : Rouge
   - CU Importantes : Orange
   - CU Normales : Vert