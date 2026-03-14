# 🚀 Guide Rapide - Connexion Administrateur

## ⚡ Connexion rapide

### 1️⃣ Lancer l'application
```bash
python main.py
```

### 2️⃣ Utiliser les identifiants par défaut

| Champ | Valeur |
|-------|--------|
| **Identifiant** | `admin` |
| **Mot de passe** | `AdminPass123` |

### 3️⃣ Cliquer sur "Connexion"

---

## 🔧 Si le compte admin n'existe pas

```bash
python src/scripts/seed_auth.py
```

Puis réessayer la connexion avec les identifiants ci-dessus.

---

## ✅ Vérification rapide

Pour vérifier que tout est prêt :

```bash
python scripts/verify_roles_permissions.py
```

---

## 📋 Autres comptes par défaut

| Rôle | Username | Mot de passe |
|------|----------|--------------|
| Admin | `admin` | `AdminPass123` |
| Responsable pédagogique | `pedagog` | `PedagogPass123` |
| Enseignant | `enseignant` | `EnseignantPass123` |
| Étudiant | `etudiant` | `EtudiantPass123` |

---

**Voir la documentation complète** : `docs/GUIDE_CONNEXION_ADMIN.md`
