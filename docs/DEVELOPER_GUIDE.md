# Guide Développeur - IA-MultiTools

## Table des matières

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Configuration de l'environnement](#configuration-de-lenvironnement)
4. [Structure du projet](#structure-du-projet)
5. [Modules principaux](#modules-principaux)
6. [Ajout de nouvelles fonctionnalités](#ajout-de-nouvelles-fonctionnalités)
7. [Tests](#tests)
8. [Build et distribution](#build-et-distribution)

## Introduction

IA-MultiTools est une application desktop Python multiplateforme développée avec Tkinter/ttkbootstrap. Elle utilise une architecture orientée objet avec séparation stricte des responsabilités.

## Architecture

### Principes de conception

- **Séparation des responsabilités**: UI / Services / Core
- **Orienté objet**: Utilisation extensive de classes et dataclasses
- **Singleton pattern**: Pour les gestionnaires globaux
- **Threading**: Pour les appels IA non bloquants
- **Chiffrement first**: Toutes les données sensibles sont chiffrées

### Stack technique

- **Python 3.12+**
- **GUI**: Tkinter + ttkbootstrap
- **API IA**: openai (compatible avec services locaux)
- **Chiffrement**: cryptography (Fernet)
- **Stockage sécurisé**: keyring
- **Configuration**: dotenv, platformdirs
- **Tests**: pytest

## Configuration de l'environnement

### Installation

```bash
# Cloner le projet
git clone <url-du-repo>
cd IA-MultiTools

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Installer l'application et les outils de développement
python -m pip install -r requirements-dev.txt
```

### Configuration

Créer un fichier `.env` à la racine:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_MODEL=meta-llama-3.1-8b-instruct
```

## Structure du projet

```
src/ia_multitools/
├── main.py                  # Point d'entrée
├── core/                    # Modules fondamentaux
│   ├── encryption.py        # Chiffrement Fernet
│   ├── keyring_manager.py   # Interface trousseau système
│   ├── secure_storage.py    # Stockage sécurisé
│   ├── config_manager.py    # Gestion configuration
│   ├── authentication.py    # Authentification et verrouillage
│   ├── history_manager.py   # Historique chiffré
│   └── openai_client.py     # Client API OpenAI
├── services/                # Services métier
│   ├── definition_service.py
│   ├── synonym_service.py
│   ├── text_correction_service.py
│   └── email_correction_service.py
└── ui/                      # Interface utilisateur
    ├── main_window.py       # Fenêtre principale
    ├── settings_window.py   # Fenêtre paramètres
    ├── tabs/                # Onglets des outils
    └── widgets/             # Widgets personnalisés
```

## Modules principaux

### Core

#### encryption.py

Gère le chiffrement/déchiffrement avec Fernet. Clé liée au compte utilisateur.

```python
from core.encryption import get_encryption_manager

manager = get_encryption_manager()
encrypted = manager.encrypt("Secret")
decrypted = manager.decrypt(encrypted)
```

#### config_manager.py

Gère la configuration de l'application avec dataclasses.

```python
from core.config_manager import get_config_manager

config_manager = get_config_manager(debug_mode=False)
config = config_manager.get_config()
config_manager.save()
```

#### openai_client.py

Client pour API OpenAI et services compatibles.

```python
from core.openai_client import get_openai_client

client = get_openai_client()
response = client.simple_completion("Prompt")
```

### Services

Tous les services suivent le même pattern:

```python
class MyService:
    def __init__(self, openai_client, history_manager, system_prompt):
        self.client = openai_client
        self.history = history_manager
        self.system_prompt = system_prompt
    
    def validate_input(self, data):
        # Validation
        pass
    
    def process(self, data):
        # Traitement
        result = self.client.simple_completion(...)
        self.history.add_entry(...)
        return result
```

### UI

#### Onglets

Chaque onglet hérite du pattern:

```python
class MyTab:
    def __init__(self, parent, config_manager):
        self.frame = ttk.Frame(parent)
        self._build_ui()
    
    def _build_ui(self):
        # Construction de l'interface
        pass
    
    def _process(self):
        # Traitement en thread séparé
        def worker():
            result = service.process(...)
            self.frame.after(0, lambda: self._update_ui(result))
        
        threading.Thread(target=worker, daemon=True).start()
```

## Ajout de nouvelles fonctionnalités

### Ajouter un nouvel outil

1. **Créer le service** (`services/my_tool_service.py`):

```python
class MyToolService:
    TOOL_NAME = "my_tool"
    
    def __init__(self, openai_client, history_manager, system_prompt):
        # ...
    
    def process_request(self, data):
        # Logique métier
        pass
```

2. **Créer l'onglet** (`ui/tabs/my_tool_tab.py`):

```python
class MyToolTab:
    def __init__(self, parent, config_manager):
        self.frame = ttk.Frame(parent)
        self.service = get_my_tool_service()
        self._build_ui()
```

3. **Ajouter dans main_window.py**:

```python
from .tabs.my_tool_tab import MyToolTab

# Dans _create_tabs():
self.my_tool_tab = MyToolTab(self.notebook, self.config_manager)
self.notebook.add(self.my_tool_tab.frame, text="🔧 Mon Outil")
```

4. **Ajouter le prompt système** dans `config_manager.py`:

```python
@dataclass
class SystemPrompts:
    # ...
    my_tool: str = "Prompt système pour mon outil"
```

### Ajouter une nouvelle configuration

1. Dans `config_manager.py`, ajouter une nouvelle dataclass ou un champ:

```python
@dataclass
class MyConfig:
    option1: str = "default"
    option2: int = 42
```

2. L'intégrer dans `AppConfig`:

```python
@dataclass
class AppConfig:
    # ...
    my_config: MyConfig = field(default_factory=MyConfig)
```

3. Ajouter l'UI dans `settings_window.py`.

## Tests

### Exécuter les tests

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ -v --cov=src --cov-report=html

# Un fichier spécifique
pytest tests/core/test_encryption.py -v
```

### Écrire un test

```python
import pytest
from src.ia_multitools.core.my_module import MyClass

def test_my_function():
    """Test de ma fonction."""
    obj = MyClass()
    result = obj.my_method("input")
    assert result == "expected"

def test_with_mock():
    """Test avec mock."""
    with patch('module.dependency') as mock_dep:
        mock_dep.return_value = "mocked"
        # Test avec mock
```

## Build et distribution

### Scripts de compilation

Installez les dépendances dans un environnement Python 3.12 ou supérieur :

```bash
python -m pip install -r requirements-dev.txt
```

Sous Windows, lancez `.\build.bat`. Sous Linux, lancez `sh build.sh`.
Les deux scripts se placent à la racine du dépôt et appellent `build.py`
avec le Python de l'environnement virtuel actif, sinon celui de `.venv`
s'il existe, sinon celui du système.

Le build inclut les ressources et les imports nécessaires à l'application.
L'exécutable est créé dans `dist/`. Pour nettoyer les fichiers générés :
`.\build.bat clean` sous Windows ou `sh build.sh clean` sous Linux.
Ces commandes ne suppriment pas les données utilisateur.

Le workflow `.github/workflows/release.yml` utilise ces scripts et joint les
archives Windows et Linux à chaque release publiée. Les fichiers `.spec`
générés, `build/`, `dist/` et `release-assets/` ne doivent pas être versionnés.

## Bonnes pratiques

### Code style

- Suivre PEP 8
- Utiliser Black pour le formatage
- Type hints pour toutes les fonctions
- Docstrings pour classes et fonctions publiques

### Commits

Format: `[Type] Description courte`

Types: `Feature`, `Fix`, `Refactor`, `Docs`, `Test`, `Security`

Exemple:
```
[Feature] Ajout de l'outil de traduction
[Fix] Correction du bug de chiffrement
[Refactor] Amélioration du gestionnaire de configuration
```

### Sécurité

- Ne jamais committer de secrets
- Toujours chiffrer les données sensibles
- Valider toutes les entrées utilisateur
- Logger les erreurs sans exposer de données sensibles

## Ressources

- [Documentation ttkbootstrap](https://ttkbootstrap.readthedocs.io/)
- [API OpenAI](https://platform.openai.com/docs/api-reference)
- [Documentation cryptography](https://cryptography.io/)
- [PEP 8](https://peps.python.org/pep-0008/)

## Support

Pour toute question, ouvrez une Issue sur GitHub ou consultez CONTRIBUTING.md.
