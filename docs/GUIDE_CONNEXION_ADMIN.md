# 🔐 Guide de Connexion - Administrateur

## 📋 Comment se connecter en tant qu'Administrateur

### ✅ Méthode 1 : Utiliser le compte Admin par défaut

Le système crée automatiquement un compte administrateur lors de l'initialisation.

#### Identifiants par défaut :

| Champ | Valeur |
|-------|--------|
| **Identifiant** | `admin` ou `admin@example.com` |
| **Mot de passe** | `AdminPass123` |

#### Étapes de connexion :

1. **Lancer l'application**
   ```bash
   python main.py
   # ou
   python run.py
   ```

2. **La fenêtre de connexion s'ouvre automatiquement**

3. **Entrer les identifiants** :
   - Dans le champ "Email ou nom d'utilisateur" : `admin`
   - Dans le champ "Mot de passe" : `AdminPass123`

4. **Cliquer sur "Connexion"**

5. **Vous serez redirigé vers la fenêtre principale** avec tous les onglets administrateur

---

### 🔧 Initialiser le compte Admin (si nécessaire)

Si le compte admin n'existe pas encore, exécutez :

```bash
python src/scripts/seed_auth.py
```

Ce script crée :
- ✅ Les rôles (Admin, Pedagogical, Teacher, Student)
- ✅ Les permissions
- ✅ Les utilisateurs par défaut dont l'admin

---

### 📝 Créer un nouveau compte Administrateur

Si vous voulez créer un autre compte administrateur :

#### Option 1 : Via l'interface (si vous avez déjà un compte admin)

1. Se connecter avec le compte admin existant
2. Aller dans les paramètres utilisateurs (si disponible)
3. Créer un nouvel utilisateur avec le rôle Admin

#### Option 2 : Via le script Python

```python
from src.database.db_manager import db_manager
from src.services.auth_service import create_user
from src.database.repositories import UserRepository, RoleRepository

# Initialiser la base de données
db_manager.initialize()
session = db_manager.get_session()

# Créer l'utilisateur
user = create_user(
    username='nouveau_admin',
    email='admin2@example.com',
    password='VotreMotDePasse123',
    session=session
)

# Assigner le rôle Admin
user_repo = UserRepository(session)
role_repo = RoleRepository(session)
admin_role = role_repo.get_by_name('Admin')
if admin_role:
    user_repo.add_role(user, admin_role)
    session.commit()
    print("✅ Nouveau compte admin créé !")

session.close()
```

#### Option 3 : Via l'interface d'inscription

1. Cliquer sur "Créer un compte" dans la fenêtre de connexion
2. Remplir le formulaire :
   - Nom d'utilisateur : `votre_admin`
   - Email : `votre@email.com`
   - Mot de passe : (minimum 6 caractères)
   - Rôle : Sélectionner "Administrateur"
3. Cliquer sur "Créer le compte"

⚠️ **Note** : Cette méthode fonctionne seulement si les rôles existent déjà dans la base de données.

---

### 🔍 Vérifier que le compte Admin existe

Pour vérifier si le compte admin existe :

```bash
python scripts/verify_roles_permissions.py
```

Ou exécuter ce script Python :

```python
from src.database.db_manager import db_manager
from src.database.repositories import UserRepository

db_manager.initialize()
session = db_manager.get_session()
user_repo = UserRepository(session)

admin = user_repo.get_by_username('admin')
if admin:
    print(f"✅ Compte admin trouvé : {admin.email}")
    roles = [r.name for r in admin.roles]
    print(f"   Rôles : {', '.join(roles)}")
else:
    print("❌ Compte admin non trouvé. Exécutez: python src/scripts/seed_auth.py")

session.close()
```

---

### 🚨 Problèmes de connexion

#### Problème 1 : "Identifiants invalides"

**Solutions :**
1. Vérifier que vous utilisez le bon identifiant :
   - `admin` (nom d'utilisateur) OU
   - `admin@example.com` (email)
2. Vérifier le mot de passe : `AdminPass123`
3. Vérifier que le compte existe :
   ```bash
   python src/scripts/seed_auth.py
   ```

#### Problème 2 : "Aucun rôle actif associé"

**Solution :**
Le compte existe mais n'a pas de rôle assigné. Réassigner le rôle :

```python
from src.database.db_manager import db_manager
from src.database.repositories import UserRepository, RoleRepository

db_manager.initialize()
session = db_manager.get_session()
user_repo = UserRepository(session)
role_repo = RoleRepository(session)

admin_user = user_repo.get_by_username('admin')
admin_role = role_repo.get_by_name('Admin')

if admin_user and admin_role:
    user_repo.add_role(admin_user, admin_role)
    session.commit()
    print("✅ Rôle Admin assigné !")

session.close()
```

#### Problème 3 : La base de données n'est pas initialisée

**Solution :**
```bash
# Initialiser la base de données
python src/scripts/seed_auth.py
```

---

### 🔄 Réinitialiser le mot de passe Admin

Si vous avez oublié le mot de passe :

```python
from src.database.db_manager import db_manager
from src.database.repositories import UserRepository
from src.utils.passwords import hash_password

db_manager.initialize()
session = db_manager.get_session()
user_repo = UserRepository(session)

admin = user_repo.get_by_username('admin')
if admin:
    # Nouveau mot de passe
    new_password = 'NouveauMotDePasse123'
    admin.password_hash = hash_password(new_password)
    session.commit()
    print(f"✅ Mot de passe admin mis à jour : {new_password}")
else:
    print("❌ Compte admin non trouvé")

session.close()
```

---

### 📊 Permissions de l'Administrateur

Une fois connecté en tant qu'admin, vous avez accès à :

- ✅ **Structure** - Configurer structure universitaire
- ✅ **Calendrier** - Configurer calendrier académique
- ✅ **Rapports** - Générer les rapports
- ✅ **Retards** - Consulter les retards académiques
- ✅ **Dashboard** - Vue d'ensemble
- ✅ **Emplois du temps** - Consultation

---

### 🎯 Interface de connexion

L'interface de connexion affiche :

```
┌─────────────────────────────────────┐
│         Connexion                   │
│  Entrez vos identifiants pour       │
│  accéder à l'application             │
│                                     │
│  Email ou nom d'utilisateur:        │
│  [________________]                 │
│                                     │
│  Mot de passe:                      │
│  [________________]                 │
│                                     │
│  [   Connexion   ]                 │
│  [ Créer un compte ]                │
└─────────────────────────────────────┘
```

---

### ✅ Checklist de connexion Admin

- [ ] La base de données est initialisée
- [ ] Le script `seed_auth.py` a été exécuté
- [ ] Le compte admin existe (`admin` ou `admin@example.com`)
- [ ] Le mot de passe est correct (`AdminPass123`)
- [ ] Le rôle Admin est assigné au compte
- [ ] L'application démarre correctement

---

### 📞 Support

Si vous rencontrez des problèmes :

1. Vérifier les logs dans `logs/app.log`
2. Exécuter `python scripts/verify_roles_permissions.py`
3. Réinitialiser avec `python src/scripts/seed_auth.py`

---

**Dernière mise à jour** : 2025
