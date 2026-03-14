# 🚀 Diagramme de Déploiement

## Vue d'ensemble

Ce document décrit l'architecture de déploiement du système d'ordonnancement académique.

---

## 🖥️ Architecture de Déploiement

```
┌─────────────────────────────────────────────────────────────┐
│                    POSTE CLIENT                             │
│                  (Windows/Linux/Mac)                        │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │         APPLICATION DESKTOP                        │   │
│  │              (PyQt5)                               │   │
│  │                                                    │   │
│  │  ┌──────────────────────────────────────────┐    │   │
│  │  │         INTERFACE GRAPHIQUE              │    │   │
│  │  │          (main_window.py)                │    │   │
│  │  │                                          │    │   │
│  │  │  • 7 Onglets                            │    │   │
│  │  │  • Dialogues                            │    │   │
│  │  │  • Widgets                              │    │   │
│  │  └──────────────────────────────────────────┘    │   │
│  │                     ↕                              │   │
│  │  ┌──────────────────────────────────────────┐    │   │
│  │  │           COUCHE MÉTIER                  │    │   │
│  │  │                                          │    │   │
│  │  │  • Managers (Structure, Activity, ...)   │    │   │
│  │  │  • Services (Pfair, Calendar, ...)       │    │   │
│  │  │  • Validators                            │    │   │
│  │  │  • Exporters                             │    │   │
│  │  └──────────────────────────────────────────┘    │   │
│  │                     ↕                              │   │
│  │  ┌──────────────────────────────────────────┐    │   │
│  │  │         COUCHE DONNÉES                   │    │   │
│  │  │                                          │    │   │
│  │  │  • Repositories (13)                     │    │   │
│  │  │  • Models SQLAlchemy                     │    │   │
│  │  │  • Database Manager                      │    │   │
│  │  └──────────────────────────────────────────┘    │   │
│  └────────────────────────────────────────────────────┘   │
│                     ↕                                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │         BASE DE DONNÉES LOCALE                     │   │
│  │              (SQLite)                              │   │
│  │                                                    │   │
│  │  Fichier: data/ordonnancement.db                  │   │
│  │  Taille: ~10-50 MB                                │   │
│  │  Tables: 12                                       │   │
│  │  Mode: WAL (Write-Ahead Logging)                 │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │            SYSTÈME DE FICHIERS                     │   │
│  │                                                    │   │
│  │  • logs/        → Fichiers de log                 │   │
│  │  • outputs/     → Exports (PDF, Excel)            │   │
│  │  • backups/     → Sauvegardes BD                  │   │
│  │  • config/      → Fichiers JSON                   │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Composants Logiciels

### **1. Application Desktop (Python + PyQt5)**

```
┌─────────────────────────────────┐
│  EXÉCUTABLE: main.py            │
├─────────────────────────────────┤
│  Runtime: Python 3.8+           │
│  Framework UI: PyQt5            │
│  ORM: SQLAlchemy                │
│  Taille: ~500 KB (code)         │
└─────────────────────────────────┘
```

**Dépendances** :
- PyQt5 (Interface)
- SQLAlchemy (ORM)
- pandas, openpyxl (Excel)
- reportlab (PDF)
- pytest (Tests)

---

### **2. Base de Données (SQLite)**

```
┌─────────────────────────────────┐
│  FICHIER: ordonnancement.db     │
├─────────────────────────────────┤
│  Type: SQLite 3                 │
│  Mode: WAL                      │
│  Taille: 10-50 MB               │
│  Tables: 12                     │
│  Indexes: 15+                   │
│  Contraintes: Clés étrangères   │
└─────────────────────────────────┘
```

**Optimisations** :
- Journal WAL pour performances
- Cache 64 MB
- Pragma foreign_keys ON
- Pragma synchronous NORMAL

---

### **3. Système de Fichiers**

```
academic-scheduler/
├── data/                    [BD et données]
│   └── ordonnancement.db   (10-50 MB)
│
├── logs/                    [Journaux]
│   ├── app.log             (Max 10 MB, 5 backups)
│   ├── errors.log          (Max 10 MB, 3 backups)
│   ├── database.log        (Max 10 MB)
│   └── pfair.log           (Max 10 MB)
│
├── outputs/                 [Fichiers générés]
│   ├── schedules/          (PDFs)
│   ├── exports/            (Excel)
│   └── reports/            (Rapports)
│
├── backups/                 [Sauvegardes]
│   └── *.db                (Max 10 backups)
│
└── config/                  [Configuration]
    ├── app_config.json
    └── algorithm_params.json
```

---

## 🔧 Configuration Matérielle Requise

### **Minimum**
```
┌─────────────────────────────────┐
│  CPU: 1.5 GHz, 2 cores          │
│  RAM: 2 GB                      │
│  Disque: 500 MB libres          │
│  OS: Windows 10 / Linux / Mac   │
│  Python: 3.8+                   │
└─────────────────────────────────┘
```

### **Recommandé**
```
┌─────────────────────────────────┐
│  CPU: 2.0+ GHz, 4 cores         │
│  RAM: 4 GB                      │
│  Disque: 2 GB libres            │
│  OS: Windows 11 / Ubuntu 22+    │
│  Python: 3.10+                  │
│  Écran: 1920x1080               │
└─────────────────────────────────┘
```

---

## 🌐 Scénarios de Déploiement

### **Scénario 1 : Mono-Poste (Actuel)**

```
┌──────────────────────┐
│   POSTE UNIQUE       │
│                      │
│  Application + BD    │
│  Tout en local       │
└──────────────────────┘
```

**Avantages** :
- ✅ Simple à déployer
- ✅ Pas de réseau requis
- ✅ Performance maximale
- ✅ Données locales sécurisées

**Inconvénients** :
- ❌ Pas de collaboration
- ❌ Une seule installation

**Usage** : Bureau administratif, test, développement

---

### **Scénario 2 : Multi-Postes avec BD Partagée**

```
┌──────────────┐     ┌──────────────┐
│  Poste 1     │     │  Poste 2     │
│  Application │     │  Application │
└──────┬───────┘     └──────┬───────┘
       │                    │
       └────────┬───────────┘
                │
        ┌───────▼────────┐
        │  SERVEUR FILE  │
        │                │
        │  ordonnancement│
        │      .db       │
        └────────────────┘
```

**Caractéristiques** :
- BD SQLite sur partage réseau
- Chaque poste a l'application
- Verrouillage SQLite pour concurrence

**Avantages** :
- ✅ Données centralisées
- ✅ Collaboration possible

**Inconvénients** :
- ❌ Performance réseau
- ❌ Risque de verrouillage

**Usage** : Petit département (2-5 utilisateurs)

---

### **Scénario 3 : Architecture Client-Serveur** (Future)

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Client 1 │  │ Client 2 │  │ Client 3 │
│  PyQt5   │  │  PyQt5   │  │  Web     │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────┬───┴─────────────┘
               │ HTTP/REST
        ┌──────▼────────┐
        │  API SERVER   │
        │  (FastAPI)    │
        └──────┬────────┘
               │
        ┌──────▼────────┐
        │  PostgreSQL   │
        │   DATABASE    │
        └───────────────┘
```

**Caractéristiques** :
- API REST centrale
- BD PostgreSQL
- Clients légers

**Avantages** :
- ✅ Scalabilité
- ✅ Accès distant
- ✅ Web + Desktop

---

## 🔐 Sécurité

### **Données Locales**
```
┌─────────────────────────────┐
│  PROTECTION DONNÉES         │
├─────────────────────────────┤
│  • BD SQLite locale         │
│  • Permissions filesystem   │
│  • Sauvegardes chiffrées    │
│  • Logs sensibles filtrés   │
└─────────────────────────────┘
```

### **Sauvegardes**
- Automatiques quotidiennes
- Max 10 copies conservées
- Rotation automatique
- Fichiers dans backups/

---

## 📊 Performance

### **Temps de Réponse Attendus**

| Opération | Temps |
|-----------|-------|
| Lancement app | < 3s |
| Génération EDT (100 jours) | < 30s |
| Calcul retards | < 1s |
| Export PDF | < 5s |
| Export Excel | < 2s |
| Sauvegarde BD | < 1s |

### **Capacité**

| Élément | Limite |
|---------|--------|
| Universités | Illimitées |
| Cohortes actives | ~100 |
| Activités/cohorte | ~50 |
| Créneaux/semestre | ~5000 |
| Enseignants | ~500 |
| Étudiants | ~10,000 |

---

## 🚀 Installation

### **Windows**
```bash
# 1. Installer Python 3.10+
# Télécharger depuis python.org

# 2. Extraire le projet
unzip academic-scheduler.zip

# 3. Installer dépendances
cd academic-scheduler
pip install -r requirements.txt

# 4. Initialiser
python init_db.py --with-test-data

# 5. Lancer
python main.py
```

### **Linux**
```bash
# 1. Python déjà installé généralement
python3 --version

# 2. Installer pip si nécessaire
sudo apt install python3-pip

# 3. Extraire et installer
unzip academic-scheduler.zip
cd academic-scheduler
pip3 install -r requirements.txt

# 4. Initialiser et lancer
python3 init_db.py --with-test-data
python3 main.py
```

### **macOS**
```bash
# 1. Installer Python via Homebrew
brew install python@3.10

# 2. Suivre les mêmes étapes que Linux
```

---

## 🔧 Maintenance

### **Sauvegardes**
```
Automatique :
- Quotidienne au lancement
- Lors de la fermeture
- Max 10 backups
```

### **Logs**
```
Rotation automatique :
- app.log : 10 MB, 5 backups
- errors.log : 10 MB, 3 backups
```

### **Nettoyage**
```
Outputs :
- Auto-nettoyage après 30 jours
- Configurable dans app_config.json
```

---

## 📝 Notes pour Draw.io

Pour créer le diagramme :
1. Utiliser des cubes 3D pour les serveurs/postes
2. Cylindres pour les bases de données
3. Rectangles pour les composants logiciels
4. Flèches pour les connexions
5. Couleurs :
   - Infrastructure : Gris
   - Application : Bleu
   - Base de données : Vert
   - Filesystem : Orange