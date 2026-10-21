# 🐛 Guide de Débogage - ImportError

## ❌ Erreur Rencontrée

```
ImportError: attempted relative import with no known parent package
```

**Fichier**: `src/ia_multitools/main.py`  
**Ligne**: `from .core.config_manager import get_config_manager`

---

## 📚 Explication du Problème

### Cause Racine

Python distingue deux modes d'exécution:

#### 1. Exécution directe (❌ Incorrect)
```bash
python src/ia_multitools/main.py --debug
```

Quand vous exécutez un fichier `.py` directement:
- Le module s'appelle `__main__`
- Python ne connaît pas le package parent
- Les imports relatifs (`.core`, `..models`) échouent

#### 2. Exécution comme module (✅ Correct)
```bash
python -m src.ia_multitools.main --debug
```

Quand vous exécutez via `-m`:
- Python reconnaît la structure de package
- Les imports relatifs fonctionnent
- Le module garde son nom complet

### Pourquoi les Imports Relatifs?

Les imports relatifs sont préférés dans les packages pour:
- ✅ Éviter les conflits de noms
- ✅ Rendre le code portable
- ✅ Clarifier la structure du package
- ✅ Faciliter les refactorings

---

## ✅ Solutions Implémentées

### Solution 1: Script Wrapper (RECOMMANDÉ) ⭐

Un script `run.py` a été créé à la racine:

```python
# run.py
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from ia_multitools.main import main

if __name__ == "__main__":
    sys.exit(main())
```

**Utilisation:**
```bash
# Windows
python run.py --debug

# Ou avec script batch
run.bat --debug

# Linux
./run.sh --debug
```

**Avantages:**
- ✅ Simple à utiliser
- ✅ Fonctionne depuis n'importe où
- ✅ Supporte tous les arguments
- ✅ Compatible IDE

### Solution 2: Imports Dynamiques (Implémenté)

Le code de `main.py` a été modifié pour supporter **les deux modes**:

```python
try:
    # Essayer imports relatifs (python -m)
    from .core.config_manager import get_config_manager
    # ...
except ImportError:
    # Fallback sur imports absolus (exécution directe)
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from ia_multitools.core.config_manager import get_config_manager
    # ...
```

**Avantages:**
- ✅ Robuste
- ✅ Fonctionne dans tous les cas
- ✅ Transparent pour l'utilisateur

### Solution 3: Module Python

Méthode standard Python:

```bash
python -m src.ia_multitools.main --debug
```

**Avantages:**
- ✅ Méthode officielle Python
- ✅ Aucune modification nécessaire
- ✅ Recommandé par PEP

---

## 🚀 Méthodes de Lancement

### Depuis la Racine du Projet

```bash
# Option 1 - Script wrapper (le plus simple)
python run.py

# Option 2 - Avec batch Windows
run.bat

# Option 3 - Avec bash Linux/Mac
./run.sh

# Option 4 - Module Python
python -m src.ia_multitools.main

# Mode debug
python run.py --debug
```

### Depuis un IDE (PyCharm, VSCode)

#### PyCharm
1. Cliquez droit sur `run.py` → Run
2. Ou configurez:
   - Script path: `chemin/vers/run.py`
   - Parameters: `--debug` (optionnel)

#### VSCode
Créez `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "IA-MultiTools",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal",
            "args": []
        },
        {
            "name": "IA-MultiTools (Debug)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal",
            "args": ["--debug"]
        }
    ]
}
```

---

## 🔍 Vérification du Fix

### Test 1: Lancement Normal

```bash
python run.py
```

**Résultat attendu:**
```
2026-06-01 23:31:55,886 - __main__ - INFO - IA-MultiTools - Démarrage de l'application
2026-06-01 23:31:55,886 - __main__ - INFO - Mode debug: False
...
2026-06-01 23:31:57,763 - __main__ - INFO - Toutes les dépendances sont présentes
2026-06-01 23:31:57,763 - __main__ - INFO - Initialisation de la configuration...
```

### Test 2: Mode Debug

```bash
python run.py --debug
```

**Résultat attendu:**
```
2026-06-01 23:31:55,886 - __main__ - INFO - Mode debug: True
2026-06-01 23:31:55,886 - __main__ - INFO - Fichier de logs: logs\ia_multitools.log
...
```

### Test 3: Via Module

```bash
python -m src.ia_multitools.main --debug
```

**Résultat attendu:** Identique au test 2.

---

## 🛠️ Dépannage Avancé

### Problème: `ModuleNotFoundError: No module named 'ia_multitools'`

**Vérifications:**
1. Êtes-vous dans le bon dossier?
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   # Doit afficher: .../IA-MultiTools
   ```

2. La structure est-elle correcte?
   ```bash
   ls -la src/ia_multitools/  # Linux/Mac
   dir src\ia_multitools\     # Windows
   # Doit contenir: __init__.py, main.py, core/, services/, ui/
   ```

3. Le fichier `__init__.py` existe-t-il?
   ```bash
   # Vérifier la présence de __init__.py
   test -f src/ia_multitools/__init__.py && echo "OK" || echo "MANQUANT"
   ```

### Problème: `AttributeError` dans les imports

**Cause:** Import circulaire ou module incomplet

**Solution:**
```bash
# Vérifier la syntaxe Python
python -m py_compile src/ia_multitools/main.py

# Vérifier tous les fichiers
find src -name "*.py" -exec python -m py_compile {} \;  # Linux
```

### Problème: Scripts batch/bash ne fonctionnent pas

**Windows (run.bat):**
```bash
# Vérifier les permissions
icacls run.bat

# Exécuter manuellement
cmd /c run.bat
```

**Linux (run.sh):**
```bash
# Rendre exécutable
chmod +x run.sh

# Vérifier
ls -l run.sh

# Doit afficher: -rwxr-xr-x
```

---

## 📖 Concepts Python Importants

### Différence entre Script et Module

#### Script (exécution directe)
```python
# Exécuté avec: python script.py
if __name__ == "__main__":
    print(__name__)  # Affiche: __main__
```

#### Module (exécution via -m)
```python
# Exécuté avec: python -m package.module
if __name__ == "__main__":
    print(__name__)  # Affiche: package.module
```

### sys.path

Python cherche les modules dans `sys.path`:

```python
import sys
print(sys.path)
# [
#   '/chemin/courant',
#   '/python/lib',
#   ...
# ]
```

Le script `run.py` ajoute `src/` à `sys.path`.

### Imports Relatifs vs Absolus

```python
# Import relatif (préféré dans un package)
from .core import config_manager
from ..models import User

# Import absolu (fonctionne partout)
from ia_multitools.core import config_manager
from ia_multitools.models import User
```

---

## ✅ Checklist de Résolution

- [ ] Utiliser `python run.py` au lieu de `python src/ia_multitools/main.py`
- [ ] Vérifier que vous êtes dans le dossier racine du projet
- [ ] Confirmer que `src/ia_multitools/__init__.py` existe
- [ ] Tester avec `python -m src.ia_multitools.main`
- [ ] Vérifier les logs pour d'autres erreurs
- [ ] Confirmer que les dépendances sont installées

---

## 📞 Support

Si le problème persiste:

1. **Vérifier la version Python:**
   ```bash
   python --version
   # Doit être 3.12+
   ```

2. **Réinstaller les dépendances:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Supprimer les caches:**
   ```bash
   # Windows
   del /s /q __pycache__
   del /s /q *.pyc
   
   # Linux
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```

4. **Ouvrir une Issue** avec:
   - Version Python
   - Système d'exploitation
   - Commande exacte utilisée
   - Logs complets

---

## 📚 Références

- [PEP 328 - Imports: Multi-Line and Absolute/Relative](https://www.python.org/dev/peps/pep-0328/)
- [Python Modules Documentation](https://docs.python.org/3/tutorial/modules.html)
- [Python -m flag documentation](https://docs.python.org/3/using/cmdline.html#cmdoption-m)

---

**Résolu**: Le problème d'import a été corrigé avec plusieurs solutions compatible. ✅

