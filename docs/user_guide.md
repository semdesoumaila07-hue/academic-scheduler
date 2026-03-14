# 📖 Guide Utilisateur

Guide complet pour utiliser le Système d'Ordonnancement Académique P-équitable.

---

## 🚀 Démarrage Rapide

### Installation

**1. Télécharger le projet**
```bash
# Extraire academic-scheduler.zip
unzip academic-scheduler.zip
cd academic-scheduler
```

**2. Installer les dépendances**
```bash
pip install -r requirements.txt
```

**3. Initialiser la base de données**
```bash
# Avec données de test (recommandé pour commencer)
python init_db.py --with-test-data

# OU base vide
python create_db.py
```

**4. Lancer l'application**
```bash
python main.py
```

🎉 **L'interface graphique s'ouvre !**

---

## 🎯 Interface Principale

L'application comporte **7 onglets principaux** :

### **1. 📊 Tableau de bord**
Vue d'ensemble de l'activité du système.

**Informations affichées** :
- Nombre de cohortes actives
- Nombre d'activités en cours
- Retard global en heures
- Nombre d'enseignants

**Actions** : Consultation uniquement

---

### **2. 🏛️ Structure**
Gestion de la structure universitaire.

#### **Créer une Université**
1. Cliquer sur **"Nouvelle Université"**
2. Remplir :
   - Nom : `Université Thomas Sankara`
   - Code : `UTS`
   - Adresse, Ville, Pays
3. Cliquer **"Enregistrer"**

#### **Créer une UFR**
1. Cliquer sur **"Nouvelle UFR"**
2. Remplir :
   - Nom : `UFR Sciences Exactes et Appliquées`
   - Code : `UFR-SEA`
   - Directeur
   - Université parente
3. Enregistrer

#### **Créer un Programme**
1. Cliquer sur **"Nouveau Programme"**
2. Remplir :
   - Nom : `Licence Informatique`
   - Code : `L3-INFO`
   - Niveau : `Licence 3`
   - Durée : `1 an`
   - UFR parente
3. Enregistrer

#### **Créer une Cohorte**
1. Cliquer sur **"Nouvelle Cohorte"**
2. Remplir :
   - Nom : `L3 Info 2025-2026`
   - Année académique : `2025-2026`
   - Semestre : `1`
   - Effectif : `45`
   - Programme parent
   - Date début : `01/10/2025`
   - Date fin : `31/03/2026`
3. Enregistrer

**✅ Votre structure est créée !**

---

### **3. 👨‍🏫 Enseignants**
Gestion des enseignants.

#### **Ajouter un Enseignant**
1. Cliquer sur **"➕ Nouvel Enseignant"**
2. Remplir le formulaire :
   - **Nom complet*** : `Dr. Marie KABORE`
   - **Email*** : `marie.kabore@uts.bf`
   - **Téléphone** : `+226 70 12 34 56`
   - **Spécialité*** : `Algorithmique`
   - **Statut*** : `Permanent` / `Vacataire` / `Contractuel`
   - **Max h/semaine** : `40`
   - **Max h/jour** : `8`
3. Cliquer **"💾 Enregistrer"**

**Champs obligatoires** : Marqués avec *

#### **Voir l'emploi du temps d'un enseignant**
1. Sélectionner un enseignant dans la liste
2. Cliquer sur **"Voir emploi du temps"**
3. Une fenêtre s'ouvre avec la grille hebdomadaire

---

### **4. 📚 Activités**
Gestion des activités académiques.

#### **Créer une Activité**
1. Cliquer sur **"➕ Nouvelle Activité"**
2. Remplir :
   - **Nom*** : `Algorithmique avancée`
   - **Code*** : `ALGO-301`
   - **Type*** : `Cours Magistral` / `TD` / `TP` / `Examen`
   - **Volume horaire*** : `30` heures
   - **Priorité** : `1-10` (8 par défaut)
   - **Date d'activation** : Date de début
   - **Deadline** : Date limite
3. Cliquer **"💾 Enregistrer"**

**💡 Important** : Le volume horaire (Ci) sera utilisé dans le calcul Pfair.

#### **Voir les Activités Urgentes**
1. Cliquer sur **"⚠️ Activités Urgentes"**
2. La liste affiche toutes les activités avec **α ≥ 0.5**
3. Les activités **α ≥ 1.0** sont critiques (en rouge)

**Légende** :
- 🔴 **Critique** : α ≥ 1.0 (doit être planifié immédiatement)
- 🟠 **Urgent** : 0.5 ≤ α < 1.0 (nécessite attention)
- 🟢 **Normal** : α < 0.5 (dans les temps)

---

### **5. 🗓️ Emplois du temps**
**⭐ FONCTIONNALITÉ PRINCIPALE**

#### **Générer un Emploi du Temps (Pfair)**

**Étape 1 : Préparer**
1. Aller dans l'onglet **"🗓️ Emplois du temps"**
2. Cliquer sur **"🔄 Générer Emploi du Temps (Pfair)"**

**Étape 2 : Configurer**
Une fenêtre s'ouvre :
- **Cohorte** : Sélectionner la cohorte (ex: L3 Info 2025-2026)
- **Période** :
  - Date de début : `01/01/2026`
  - Date de fin : `30/06/2026`
- **Salles disponibles** : `A101, A102, B201, B202, C301` (séparer par des virgules)
- **Remplacer l'existant** : ☐ Cocher pour remplacer

**Étape 3 : Lancer**
1. Cliquer **"Générer"**
2. L'algorithme Pfair s'exécute :
   - ✅ Calcul de D_effectif (jours ouvrables)
   - ✅ Calcul de U(τi) pour chaque activité
   - ✅ Test de faisabilité (U ≤ 1.0)
   - ✅ Calcul de α pour chaque jour
   - ✅ Priorisation des activités urgentes
   - ✅ Création des créneaux horaires

**Étape 4 : Résultat**
```
✅ Emploi du temps généré avec succès !

Statistiques :
- Créneaux créés : 45
- Heures planifiées : 90h
- Retard total : 2.5h
- Conflits détectés : 0

Charge de la cohorte : U = 0.66 (66%)
```

#### **Visualiser l'Emploi du Temps**
1. Cliquer sur **"👁️ Visualiser"**
2. Une grille hebdomadaire s'affiche :

```
┌──────┬─────────┬─────────┬──────────┬─────────┬──────────┬─────────┐
│      │ Lundi   │ Mardi   │ Mercredi │ Jeudi   │ Vendredi │ Samedi  │
├──────┼─────────┼─────────┼──────────┼─────────┼──────────┼─────────┤
│ 8-10h│ ALGO    │ BD      │ RÉSEAUX  │ WEB     │ ALGO     │         │
│      │ KABORE  │ TRAORE  │ SAWADOGO │OUATTARA │ KABORE   │         │
│      │ A101    │ B202    │ C301     │ A102    │ A101     │         │
├──────┼─────────┼─────────┼──────────┼─────────┼──────────┼─────────┤
│10-12h│ TD ALGO │ TP BD   │          │ TD WEB  │ RÉSEAUX  │         │
│      │ KABORE  │ TRAORE  │          │OUATTARA │ SAWADOGO │         │
│      │ A101    │ B202    │          │ A102    │ C301     │         │
└──────┴─────────┴─────────┴──────────┴─────────┴──────────┴─────────┘
```

#### **Exporter l'Emploi du Temps**
1. Cliquer sur **"📥 Exporter"**
2. Choisir le format :
   - **PDF** : Grille formatée A4 paysage
   - **Excel** : Tableau éditable
3. Le fichier est sauvegardé dans `outputs/`

---

### **6. 🏖️ Congés**
Gestion des demandes de congé.

#### **Soumettre une Demande**
1. Cliquer sur **"➕ Nouvelle Demande"**
2. Remplir :
   - **Type de congé** : `Congé annuel` / `Maladie` / `Formation` / `Autre`
   - **Date de début** : `01/02/2026`
   - **Date de fin** : `07/02/2026`
   - **Raison** : Expliquer (minimum 10 caractères)
3. Cliquer **"📨 Soumettre"**

**Statut** : `⏳ En attente` → Nécessite approbation

#### **Approuver/Rejeter une Demande** (Admin)
1. Cliquer sur **"⏳ En attente"**
2. Sélectionner une demande
3. Cliquer sur :
   - **"✅ Approuver"** : Les créneaux de l'enseignant seront automatiquement bloqués
   - **"❌ Rejeter"** : Indiquer la raison du rejet

**💡 Impact** : Une demande approuvée bloque automatiquement les créneaux de l'enseignant dans l'emploi du temps.

---

### **7. 📅 Calendrier**
Configuration du calendrier académique.

#### **Ajouter un Jour Férié**
1. Cliquer sur **"➕ Ajouter Jour Férié"**
2. Remplir :
   - Nom : `Fête Nationale`
   - Date : `05/08/2026`
   - Récurrent : ☑ (si chaque année)
3. Enregistrer

**Effet** : Ce jour sera exclu du calcul de D_effectif.

#### **Ajouter une Période de Vacances**
1. Cliquer sur **"🏖️ Ajouter Vacances"**
2. Remplir :
   - Nom : `Vacances de Noël`
   - Date début : `20/12/2025`
   - Date fin : `05/01/2026`
   - Type : `Vacances de Noël`
3. Enregistrer

**Effet** : Ces jours seront exclus de l'ordonnancement.

---

## 🔬 Comprendre l'Algorithme Pfair

### **Qu'est-ce que Pfair ?**

**Pfair** (Proportionate Fair) est un algorithme d'ordonnancement temps réel qui garantit une progression **équitable** de toutes les activités.

**Principe** : Chaque activité doit progresser proportionnellement au temps écoulé.

### **Formules Clés**

#### **1. Facteur de charge**
```
U(τi) = Ci / D_effectif

Ci = Volume horaire total de l'activité
D_effectif = Nombre de jours ouvrables
```

**Exemple** :
- Activité "Algorithmique" : Ci = 30h
- Période : 100 jours ouvrables
- U = 30/100 = 0.3

#### **2. Retard (lag)**
```
lag(τi, t) = U(τi) × t - H(t)

t = Temps écoulé (en jours)
H(t) = Heures déjà réalisées
```

**Exemple après 20 jours** :
- Heures attendues : 0.3 × 20 = 6h
- Heures réalisées : 4h
- Retard : 6 - 4 = 2h

#### **3. Ratio α**
```
α(τi, t) = lag(τi, t) / U(τi)
```

**Interprétation** :
- **α ≥ 1.0** : Activité URGENTE (retard d'au moins 1 jour)
- **α ≥ 0.5** : Activité importante
- **α < 0.5** : Activité normale

#### **4. Test de Faisabilité**
```
U = Σ U(τi) ≤ 1.0

Si U > 1.0 → Impossible à ordonnancer
```

**Exemple** :
- Activité 1 : U1 = 0.3
- Activité 2 : U2 = 0.2
- Activité 3 : U3 = 0.25
- Total : U = 0.75 ≤ 1.0 ✅ Faisable

---

## 📊 Cas d'Usage Pratiques

### **Cas 1 : Nouvelle Année Académique**

**Objectif** : Planifier un semestre complet

**Étapes** :
1. Créer la structure (Université → UFR → Programme → Cohorte)
2. Ajouter les enseignants
3. Créer toutes les activités du semestre
4. Configurer le calendrier (jours fériés, vacances)
5. Générer l'emploi du temps avec Pfair
6. Exporter en PDF et distribuer

**Durée** : ~30 minutes pour une cohorte

---

### **Cas 2 : Ajuster en Cours de Semestre**

**Problème** : Un enseignant est malade

**Solution** :
1. Aller dans **"🏖️ Congés"**
2. Soumettre une demande de congé maladie
3. Approuver la demande → Les créneaux sont automatiquement bloqués
4. Aller dans **"🗓️ Emplois du temps"**
5. Créer manuellement des créneaux de remplacement
6. Ou régénérer partiellement l'emploi du temps

---

### **Cas 3 : Identifier les Retards**

**Objectif** : Voir quelles activités sont en retard

**Étapes** :
1. Aller dans **"📚 Activités"**
2. Cliquer sur **"⚠️ Activités Urgentes"**
3. La liste affiche les activités avec leur α
4. Prioriser les activités avec α ≥ 1.0 (critiques)
5. Planifier des rattrapages

---

## ⚠️ Résolution de Problèmes

### **Erreur : "Charge totale U > 1.0"**

**Cause** : Trop d'activités pour la période donnée

**Solution** :
1. Réduire le volume horaire de certaines activités
2. Allonger la période
3. Répartir sur plusieurs semestres

---

### **Conflits Détectés**

**Types de conflits** :
- **Enseignant** : Même enseignant, 2 cours simultanés
- **Cohorte** : Même cohorte, 2 cours simultanés
- **Salle** : Même salle, 2 cours simultanés

**Solution** :
1. Afficher les détails du conflit
2. Modifier manuellement les créneaux
3. Ou régénérer avec plus de salles disponibles

---

### **Activités Urgentes**

**Problème** : Plusieurs activités avec α ≥ 1.0

**Solution** :
1. Planifier immédiatement des rattrapages
2. Augmenter la fréquence des cours
3. Vérifier si des créneaux sont disponibles

---

## 💡 Bonnes Pratiques

### **Avant de Générer**
- ✅ Vérifier que toutes les activités ont un enseignant assigné
- ✅ Configurer le calendrier (jours fériés, vacances)
- ✅ Définir les salles disponibles
- ✅ Vérifier les disponibilités des enseignants

### **Pendant le Semestre**
- 📊 Consulter régulièrement le tableau de bord
- ⚠️ Surveiller les activités urgentes (α ≥ 0.5)
- 📅 Mettre à jour les demandes de congés
- 💾 Faire des sauvegardes régulières

### **Après Génération**
- 👁️ Vérifier l'emploi du temps visuellement
- 🔍 Détecter les conflits éventuels
- 📥 Exporter et distribuer
- 📧 Envoyer aux enseignants et étudiants

---

## 🎓 FAQ

**Q : Puis-je modifier manuellement l'emploi du temps généré ?**  
R : Oui, utilisez **"Créer créneau manuel"** dans l'onglet Emplois du temps.

**Q : Que se passe-t-il si U > 1.0 ?**  
R : L'ordonnancement est impossible. Réduisez les volumes horaires ou allongez la période.

**Q : Comment annuler un emploi du temps ?**  
R : Régénérez avec l'option **"Remplacer l'existant"** cochée.

**Q : Les weekends sont-ils comptés dans D_effectif ?**  
R : Non, seuls les jours ouvrables (lundi-vendredi) sont comptés.

**Q : Puis-je avoir plusieurs cohortes ?**  
R : Oui, créez autant de cohortes que nécessaire et générez un emploi du temps pour chacune.

---

## 📞 Support

Pour toute question :
1. Consulter la documentation (`docs/`)
2. Vérifier les logs (`logs/app.log`)
3. Relire ce guide
4. Contacter l'administrateur système

---

**Bon ordonnancement ! 🚀🎓**