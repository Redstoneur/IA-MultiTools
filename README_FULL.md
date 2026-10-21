# IA-MultiTools

![Logo IA-MultiTools](assets/logo.svg)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0--only-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

Application desktop Python multiplateforme proposant plusieurs outils linguistiques assistés par IA locale ou distante via une API compatible OpenAI.

## 🎯 Fonctionnalités principales

### Outils linguistiques

- **📖 Définition** : Obtenez des définitions claires et concises de mots ou concepts
- **🔄 Synonymes et Antonymes** : Trouvez rapidement des alternatives lexicales
- **✏️ Correction de texte** : Corrigez orthographe, grammaire et ponctuation en une seule version
- **📧 Correction d'e-mails** : Corrigez vos messages en conservant leur ton ou en les professionnalisant
- **📟 Correction et traduction** : Corrigez le texte dans sa langue source, puis traduisez la version corrigée vers la langue de votre choix

Les cinq outils proposent des instructions complémentaires facultatives et une
sortie en texte brut ou Markdown. Les panneaux et les sections des paramètres
disposent d'un défilement vertical ; la navigation au clavier rend le champ actif
accessible même sur un petit écran.

### Caractéristiques techniques

- 🎨 **Interface moderne** avec mode sombre (ttkbootstrap)
- Compatibilité GUI : ttkbootstrap 1.x (`>=1.10.1,<2`) ; la version 2 modifie l'API utilisée par l'application.
- HTTPX est déclaré comme dépendance directe pour les connexions du client IA.
- 🔐 **Sécurité intégrée** : clés Fernet aléatoires conservées dans le trousseau système
- 🔑 **Clé API** stockée uniquement dans le trousseau système, jamais dans le fichier de configuration
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

Au premier lancement, un assistant redimensionnable et défilant s'ouvre :
1. Renseignez l'**URL de base**, par exemple `http://127.0.0.1:1234/v1`, et la **clé API** si le serveur l'exige.
2. Cliquez sur **Charger les modèles disponibles**, puis choisissez un modèle dans la liste déroulante. La saisie manuelle reste possible.
3. Réglez la **température** (0 à 2, valeur initiale 0.2), le **timeout** en secondes et la **vérification SSL**, activée par défaut et recommandée.
4. Testez la connexion avec ces réglages, puis enregistrez.

Le chargement des modèles utilise l'URL, la clé API et les réglages SSL/timeout
actuels. La présence d'un modèle dans la liste ne garantit pas qu'il prend en
charge la génération de texte.

Les mêmes réglages sont accessibles dans **Paramètres → Configuration IA**.
Toute modification nécessite une nouvelle validation avant sauvegarde. La
configuration enregistrée s'applique aux outils déjà ouverts, sans redémarrage.

### Utilisation des outils

#### Outil Définition
1. Onglet **Définition**
2. Saisissez un mot ou concept
3. Optionnel : limitez le nombre de mots, précisez vos instructions et choisissez Texte ou Markdown
4. Choisissez Texte ou Markdown et ajoutez des instructions complémentaires si besoin, puis cliquez sur **Générer**
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
3. Ajoutez des instructions optionnelles et activez **Ajouter une mise en forme Markdown** si souhaité (désactivé par défaut)
4. Cliquez sur **Corriger**
5. Récupérez une seule version corrigée, sans variantes ni explications

#### Outil E-mails
1. Onglet **E-mails**
2. Rédigez ou collez votre e-mail
3. Choisissez les options :
   - **Rendre professionnel** : décoché par défaut, conserve le registre d'origine ; coché, professionnalise sans remplacer le tutoiement par le vouvoiement.
   - **Ajouter formule de politesse** : décoché par défaut ; décoché, interdit d'ajouter des salutations ou clôtures, mais conserve celles déjà présentes.
   - **Ajouter une mise en forme Markdown** : désactivé par défaut.
4. Ajoutez des instructions spécifiques si besoin
5. Cliquez sur **Corriger**

#### Outil Correction et traduction
1. Ouvrez l'onglet **Traduction** et collez le texte à traiter.
2. Sélectionnez une **langue cible** dans la liste ou saisissez une autre langue. La valeur initiale est **Anglais** ; la langue source est détectée automatiquement.
3. Ajoutez des instructions complémentaires facultatives et activez Markdown si souhaité (désactivé par défaut).
4. Cliquez sur **Corriger et traduire**.
5. Copiez la traduction finale si besoin.

Le traitement effectue deux requêtes successives : correction dans la langue
source, puis traduction du texte corrigé. Seule la traduction finale est affichée
et enregistrée dans l'historique. Si une étape échoue, aucun résultat partiel
n'est enregistré. **Réinitialiser** vide les champs et rétablit Anglais et le
Markdown désactivé.

#### Instructions, format et réponses structurées

Les instructions complémentaires et le prompt personnalisé de chaque outil
sont transmis à chaque requête. Les options explicites sélectionnées priment
sur les anciennes consignes contradictoires. Markdown produit du balisage
copiable ; les zones de résultat affichent ce balisage en texte, sans rendu HTML.

Les outils demandent une sortie structurée avec `response_format: json_schema`
pour permettre un décodage contraint côté serveur lorsque celui-ci le prend en
charge. L'application valide la structure et affiche uniquement le résultat,
sans enveloppe JSON. Si le serveur indique explicitement que cette fonctionnalité
n'est pas prise en charge, un avertissement est journalisé et la requête est
réessayée en texte libre. Les autres erreurs ne déclenchent pas ce repli.
Le schéma contraint la structure, pas la justesse linguistique ni le respect
sémantique de toutes les consignes, qui restent dépendants du modèle.

## 🔐 Sécurité

### Chiffrement des données

Les données utilisateur persistées sont **chiffrées au repos** avec Fernet. La clé Fernet aléatoire est conservée dans le trousseau système :
- Configuration (config.enc)
- Historique (history.enc)
- Prompts personnalisés (prompts.enc)
- Cache (cache.enc)

### Trousseau système

Le trousseau système est requis pour accéder aux données chiffrées et enregistrer une clé API. Il n'existe pas de repli vers un fichier local :
- **Windows** : DPAPI / Credential Manager
- **Linux** : Secret Service / GNOME Keyring / KWallet

Sous Linux, une session D-Bus avec Secret Service (par exemple GNOME Keyring ou KWallet) doit être disponible. L'application refuse de sauvegarder des données si le trousseau ne peut pas être utilisé.

Une clé API fournie par `OPENAI_API_KEY` est utilisée en mémoire pour la session. Pour la conserver entre les démarrages, enregistrez-la depuis les paramètres afin qu'elle soit placée dans le trousseau système.

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
OPENAI_VERIFY_SSL=true
```

La validation des certificats TLS est activée par défaut. Ne désactivez `OPENAI_VERIFY_SSL` que pour un serveur de confiance utilisant un certificat non standard.

### Prompts système personnalisables

Depuis l'interface **Paramètres → Prompts système**, vous pouvez personnaliser les instructions données à l'IA pour chaque outil.
Cela inclut **Correction et traduction**. Les outils relisent le prompt enregistré
avant chaque traitement ; il n'est pas nécessaire de les fermer puis de les rouvrir.

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
│   ├── email_correction_service.py
│   ├── translation_service.py  # Correction puis traduction
│   └── output_rules.py         # Règles de sortie communes
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

### Scripts de build PyInstaller

Installez les dépendances de développement :

```bash
python -m pip install -e ".[dev]"
```

**Windows :**
```bash
.\build.bat
```

**Linux :**
```bash
sh build.sh
```

Les scripts utilisent l'environnement virtuel actif, sinon `.venv` s'il existe,
puis le Python système, et appellent `build.py` depuis la racine du dépôt.
L'exécutable sera dans `dist/`. Pour nettoyer les fichiers de compilation :
`.\build.bat clean` sous Windows ou `sh build.sh clean` sous Linux.

Le workflow de release utilise ces mêmes scripts et joint les archives Windows
et Linux à chaque release publiée. Les caches, les fichiers de build, les archives
locales, `data/`, `logs/` et les fichiers `.env` privés sont ignorés par Git ;
`.env.example` reste versionné.

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

Ce projet est sous licence GNU General Public License v3.0 (GPL-3.0-only). Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) pour le thème moderne
- [OpenAI](https://openai.com/) pour l'API
- [cryptography](https://cryptography.io/) pour le chiffrement
- Communauté Open Source
