# 🔐 Guide de Connexion - Système d'Ordonnancement Académique

## 🚀 Connexion Rapide - Administrateur

### Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| **Identifiant** | `admin` |
| **Mot de passe** | `AdminPass123` |

**OU**

| Champ | Valeur |
|-------|--------|
| **Identifiant** | `admin@example.com` |
| **Mot de passe** | `AdminPass123` |

---

## 📋 Étapes de connexion

### 1. Lancer l'application

```bash
python main.py
```

### 2. Fenêtre de connexion

Une fenêtre de connexion s'ouvre automatiquement avec deux champs :
- **Email ou nom d'utilisateur**
- **Mot de passe**

### 3. Entrer les identifiants

- Dans "Email ou nom d'utilisateur" : `admin`
- Dans "Mot de passe" : `AdminPass123`

### 4. Cliquer sur "Connexion"

Vous serez automatiquement redirigé vers la fenêtre principale avec tous les onglets administrateur.

---

## 🔧 Initialisation (première fois)

Si c'est la première fois que vous utilisez l'application :

```bash
# 1. Initialiser la base de données et créer les comptes
python src/scripts/seed_auth.py

# 2. Lancer l'application
python main.py

# 3. Se connecter avec admin / AdminPass123
```

---

## 👥 Tous les comptes par défaut

Après l'exécution de `seed_auth.py`, ces comptes sont créés :

| Rôle | Username | Email | Mot de passe |
|------|----------|-------|--------------|
| 👑 **Admin** | `admin` | `admin@example.com` | `AdminPass123` |
| 👨‍🏫 **Responsable pédagogique** | `pedagog` | `pedagog@example.com` | `PedagogPass123` |
| 🎓 **Enseignant** | `enseignant` | `enseignant@example.com` | `EnseignantPass123` |
| 🎒 **Étudiant** | `etudiant` | `etudiant@example.com` | `EtudiantPass123` |

---

## ✅ Vérification

Pour vérifier que le compte admin existe :

```bash
python scripts/verify_roles_permissions.py
```

---

## 🆘 Problèmes courants

### "Identifiants invalides"
- Vérifier que vous utilisez `admin` ou `admin@example.com`
- Vérifier le mot de passe : `AdminPass123`
- Exécuter `python src/scripts/seed_auth.py` pour créer le compte

### "Aucun rôle actif associé"
- Le compte existe mais n'a pas de rôle
- Exécuter `python src/scripts/seed_auth.py` pour réassigner les rôles

### La fenêtre de connexion ne s'ouvre pas
- Vérifier que Python et PyQt5 sont installés
- Vérifier les logs dans `logs/app.log`

---

## 📚 Documentation complète

- **Guide détaillé** : `docs/GUIDE_CONNEXION_ADMIN.md`
- **Guide rapide** : `GUIDE_RAPIDE_CONNEXION.md`
- **Rôles et permissions** : `docs/ROLES_ET_PERMISSIONS.md`

---

**Note** : Pour des raisons de sécurité, changez le mot de passe par défaut après la première connexion !
