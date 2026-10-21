# IA-MultiTools

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

Application desktop Python multiplateforme proposant plusieurs outils linguistiques assistés par IA locale ou distante via une API compatible OpenAI.

## 🎯 Fonctionnalités principales

### Outils linguistiques

- **📖 Définition** : Obtenez des définitions claires et concises de mots ou concepts
- **🔄 Synonymes et Antonymes** : Trouvez rapidement des alternatives lexicales
- **✏️ Correction de texte** : Corrigez orthographe, grammaire et style
- **📧 Correction d'e-mails** : Professionnalisez vos communications électroniques

### Caractéristiques techniques

- 🎨 **Interface moderne** avec mode sombre (ttkbootstrap)
- 🔐 **Sécurité intégrée** : chiffrement Fernet de toutes les données
- 🔑 **Support trousseau système** : Keyring (Windows/Linux)
- 📚 **Historique chiffré** de vos requêtes et réponses
- 🌐 **Compatible API OpenAI** : OpenAI, LM Studio, LocalAI, llama.cpp, etc.
- 🚀 **Traitement asynchrone** : interface non bloquante
- 📝 **Export** en Texte ou Markdown
- ⚙️ **Hautement configurable** : prompts système personnalisables
- 🔒 **Verrouillage optionnel** de l'application
- 📊 **Logging avec rotation** pour le débogage

## 🔧 Prérequis

- **Python 3.12+**
- **Windows 10/11** ou **Linux** (testé sur Ubuntu 22.04+)
- Connexion à un serveur compatible API OpenAI (local ou distant)

## 📦 Installation

### Option 1 : Depuis les sources (développeurs)

```bash
# Cloner le repository
git clone https://github.com/votre-username/IA-MultiTools.git
cd IA-MultiTools

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Option 2 : Exécutable autonome (utilisateurs finaux)

Téléchargez l'exécutable correspondant à votre plateforme depuis la page [Releases](https://github.com/votre-username/IA-MultiTools/releases):
- `IA-MultiTools.exe` pour Windows
- `IA-MultiTools` pour Linux

## 🚀 Utilisation

### Lancement

**Depuis les sources :**
```bash
python -m src.ia_multitools.main
```

**Mode debug :**
```bash
python -m src.ia_multitools.main --debug
```

**Exécutable :**
- Windows : Double-cliquez sur `IA-MultiTools.exe`
- Linux : `./IA-MultiTools` (assurez-vous qu'il est exécutable : `chmod +x IA-MultiTools`)

### Configuration initiale

Au premier lancement :
1. Accédez aux **Paramètres** (bouton ou menu)
2. Configurez la **connexion IA** :
   - **URL de base** : `http://127.0.0.1:1234/v1` (exemple pour LM Studio)
   - **Clé API** : votre clé (ou `sk-dummy` pour services locaux)
   - **Modèle** : nom du modèle (ex: `meta-llama-3.1-8b-instruct`)
   - **Température** : 0.2 (recommandé pour précision)
3. Sauvegardez

### Utilisation des outils

#### Outil Définition
1. Onglet **Définition**
2. Saisissez un mot ou concept
3. Optionnel : limitez le nombre de mots
4. Cliquez sur **Générer**
5. Copiez le résultat si besoin

#### Outil Synonymes
1. Onglet **Synonymes**
2. Saisissez un mot
3. Choisissez : Synonymes / Antonymes / Les deux
4. Cliquez sur **Générer**
5. Obtenez une liste concise

#### Outil Correction de texte
1. Onglet **Correction**
2. Collez votre texte
3. Ajoutez des instructions optionnelles
4. Cliquez sur **Corriger**
5. Récupérez le texte corrigé

#### Outil E-mails
1. Onglet **E-mails**
2. Rédigez ou collez votre e-mail
3. Activez les options :
   - Rendre professionnel
   - Ajouter formule de politesse
4. Ajoutez des instructions spécifiques si besoin
5. Cliquez sur **Corriger**

## 🔐 Sécurité

### Chiffrement des données

Toutes les données utilisateur sont **chiffrées au repos** avec Fernet (cryptography) :
- Configuration (config.enc)
- Historique (history.enc)
- Prompts personnalisés (prompts.enc)
- Cache (cache.enc)

### Trousseau système

L'application utilise le trousseau système lorsque disponible :
- **Windows** : DPAPI / Credential Manager
- **Linux** : Secret Service / GNOME Keyring / KWallet

### Verrouillage automatique

Configurez un verrouillage automatique après inactivité :
- Désactivé
- 5, 15, 30 ou 60 minutes

### Localisation des données

- **Mode production** : Dossier utilisateur
  - Windows : `%APPDATA%\IA-MultiTools\`
  - Linux : `~/.config/ia-multitools/`
- **Mode debug (--debug)** : Dossier de l'application

## ⚙️ Configuration avancée

### Variables d'environnement

Vous pouvez préconfigurer l'application avec un fichier `.env` :

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=meta-llama-3.1-8b-instruct
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_TEMPERATURE=0.2
OPENAI_TIMEOUT=60
OPENAI_VERIFY_SSL=false
```

### Prompts système personnalisables

Depuis l'interface **Paramètres → Prompts système**, vous pouvez personnaliser les instructions données à l'IA pour chaque outil.

### Compatibilité API OpenAI

L'application fonctionne avec tout service compatible OpenAI API :
- **OpenAI** (officiel)
- **LM Studio** (IA locale)
- **LocalAI** (IA locale)
- **Text Generation WebUI** (oobabooga)
- **llama.cpp Server**
- **Ollama** (avec proxy OpenAI)
- Tous les proxys compatibles

## 🏗️ Architecture

```
src/ia_multitools/
├── main.py                    # Point d'entrée
├── core/                      # Noyau applicatif
│   ├── config_manager.py      # Gestion configuration
│   ├── encryption.py          # Chiffrement Fernet
│   ├── authentication.py      # Authentification
│   ├── keyring_manager.py     # Interface trousseau système
│   ├── secure_storage.py      # Stockage sécurisé
│   ├── history_manager.py     # Historique chiffré
│   └── openai_client.py       # Client API OpenAI
├── services/                  # Services métier
│   ├── definition_service.py
│   ├── synonym_service.py
│   ├── text_correction_service.py
│   └── email_correction_service.py
├── ui/                        # Interface utilisateur
│   ├── main_window.py         # Fenêtre principale
│   ├── settings_window.py     # Fenêtre paramètres
│   ├── widgets/               # Widgets personnalisés
│   └── tabs/                  # Onglets des outils
└── models/                    # Modèles de données
```

### Principes de conception

- **Architecture orientée objet**
- **Séparation stricte** : UI / Services / Core
- **Type hints** et docstrings complets
- **PEP 8** compliant
- **Traitement asynchrone** pour les appels IA
- **Gestion d'erreurs robuste**

## 🔨 Build et distribution

### Build PyInstaller

**Windows :**
```bash
pyinstaller --onefile --windowed --name IA-MultiTools --icon=assets/icon.ico src/ia_multitools/main.py
```

**Linux :**
```bash
pyinstaller --onefile --windowed --name IA-MultiTools src/ia_multitools/main.py
```

L'exécutable sera dans le dossier `dist/`.

## 🧪 Tests

Exécuter les tests unitaires :

```bash
pytest tests/ -v
```

Avec couverture :

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## 📝 Logging

Les logs sont sauvegardés dans :
- **Production** : `%APPDATA%\IA-MultiTools\logs\` (Windows) ou `~/.config/ia-multitools/logs/` (Linux)
- **Debug** : `./logs/`

Rotation automatique (10 MB max par fichier, 5 backups).

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) pour le thème moderne
- [OpenAI](https://openai.com/) pour l'API
- [cryptography](https://cryptography.io/) pour le chiffrement
- Communauté Open Source



