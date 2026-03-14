# 🔧 Guide : Résoudre le problème "Python was not found"

## Problème

Vous rencontrez l'erreur :
```
Python was not found; run without arguments to install from the Microsoft Store
```

Cela signifie que Python n'est pas dans votre PATH système ou n'est pas installé.

## ✅ Solutions

### Solution 1 : Utiliser l'environnement virtuel (RECOMMANDÉ)

Votre projet a déjà des environnements virtuels (`venv` et `.venv`). Utilisez-les !

#### Sur Windows PowerShell :

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# OU si vous avez des problèmes de permissions :
.\venv\Scripts\activate.bat

# Vérifier que Python fonctionne
python --version

# Installer les dépendances si nécessaire
pip install -r requirements.txt

# Lancer l'application
python main.py
```

#### Si vous avez une erreur de politique d'exécution :

```powershell
# Exécuter cette commande en tant qu'administrateur
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Puis réessayer d'activer l'environnement
.\venv\Scripts\Activate.ps1
```

### Solution 2 : Installer Python depuis python.org

1. **Télécharger Python** :
   - Aller sur https://www.python.org/downloads/
   - Télécharger Python 3.8 ou supérieur
   - ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" lors de l'installation

2. **Vérifier l'installation** :
   ```powershell
   python --version
   ```

3. **Installer les dépendances** :
   ```powershell
   pip install -r requirements.txt
   ```

### Solution 3 : Utiliser le Python de l'environnement virtuel directement

Si l'environnement virtuel existe mais que vous ne pouvez pas l'activer :

```powershell
# Utiliser directement le Python de l'environnement virtuel
.\venv\Scripts\python.exe --version

# Lancer l'application avec ce Python
.\venv\Scripts\python.exe main.py

# Installer les dépendances
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Solution 4 : Créer un nouvel environnement virtuel

Si les environnements virtuels existants ne fonctionnent pas :

```powershell
# Trouver où Python est installé (peut être dans AppData)
# Chercher python.exe dans :
# C:\Users\VotreNom\AppData\Local\Programs\Python\
# ou
# C:\Python3x\

# Une fois Python trouvé, créer un nouvel environnement virtuel
# Remplacer le chemin par votre chemin Python
C:\Python3x\python.exe -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

## 🔍 Vérifier où Python est installé

### Méthode 1 : Chercher manuellement

1. Ouvrir l'Explorateur de fichiers
2. Aller dans `C:\Users\VotreNom\AppData\Local\Programs\Python\`
3. Chercher `python.exe`

### Méthode 2 : Via PowerShell

```powershell
# Chercher python.exe sur le système
Get-ChildItem -Path C:\ -Filter python.exe -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

### Méthode 3 : Vérifier les chemins courants

Python peut être installé dans :
- `C:\Python3x\` (x = version)
- `C:\Users\VotreNom\AppData\Local\Programs\Python\Python3x\`
- `C:\Program Files\Python3x\`
- `C:\Program Files (x86)\Python3x\`

## 📝 Scripts batch pour faciliter l'utilisation

### Créer `run.bat` dans le dossier du projet :

```batch
@echo off
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.
echo Lancement de l'application...
python main.py
pause
```

### Créer `install.bat` dans le dossier du projet :

```batch
@echo off
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo.
echo Installation des dependances...
pip install -r requirements.txt
pause
```

## ✅ Vérification finale

Après avoir résolu le problème, vérifiez que tout fonctionne :

```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Vérifier Python
python --version

# Vérifier pip
pip --version

# Vérifier les packages installés
pip list

# Lancer l'application
python main.py
```

## 🆘 Si rien ne fonctionne

1. **Réinstaller Python** depuis python.org en cochant "Add Python to PATH"
2. **Redémarrer** votre ordinateur après l'installation
3. **Utiliser un IDE** comme PyCharm ou VS Code qui gère automatiquement les environnements virtuels

## 📌 Note importante

Pour ce projet, vous avez besoin de :
- Python 3.8 ou supérieur
- Les packages listés dans `requirements.txt`
- Un environnement virtuel activé (recommandé)

Une fois Python fonctionnel, vous pourrez tester les corrections apportées au chargement des cohortes et enseignants !
