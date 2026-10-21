# IA-MultiTools

![Logo IA-MultiTools](assets/logo.svg)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0--only-orange.svg)

Application desktop Python multiplateforme proposant plusieurs outils linguistiques assistés par IA locale ou distante via une API compatible OpenAI.

## 🎯 Fonctionnalités

- 📖 **Définition** : Définitions de mots et concepts
- 🔄 **Synonymes/Antonymes** : Alternatives lexicales
- ✏️ **Correction de texte** : Correction orthographique et grammaticale
- 📧 **E-mails professionnels** : Amélioration de vos communications

## 🚀 Démarrage rapide

```bash
# Installation
pip install -r requirements.txt

# Lancement (recommandé)
python run.py

# Ou via module Python
python -m src.ia_multitools.main

# Mode debug
python run.py --debug
```

Au premier lancement, l'assistant permet de charger les modèles proposés par
votre serveur API et d'en choisir un dans une liste déroulante (ou de saisir son
nom). Vous pouvez aussi régler la température (0 à 2), le timeout en secondes
et la vérification des certificats SSL, activée par défaut et recommandée.
Le chargement des modèles utilise votre URL, votre clé API et vos réglages
SSL/timeout ; il ne garantit pas que chaque modèle prend en charge la génération
de texte. Testez la connexion avec le modèle choisi avant d'enregistrer.

## 🔐 Sécurité

- Chiffrement Fernet avec une clé aléatoire conservée dans le trousseau système
- Clé API stockée uniquement dans le trousseau système, jamais dans le fichier de configuration
- Trousseau système fonctionnel requis (Credential Manager sous Windows, Secret Service sous Linux)
- Historique chiffré
- Verrouillage automatique optionnel

## 📚 Documentation

Voir [README_FULL.md](README_FULL.md) pour la documentation complète.

## 📦 Construire un exécutable

Installez les dépendances de développement avec `python -m pip install -e ".[dev]"`,
puis lancez `.\build.bat` sous Windows ou `sh build.sh` sous Linux.
Les scripts utilisent l'environnement virtuel actif, sinon `.venv` s'il existe,
et transmettent les arguments à `build.py`.

L'exécutable est créé dans `dist/`. Pour nettoyer les fichiers de compilation,
utilisez `.\build.bat clean` ou `sh build.sh clean`.
Le workflow de release utilise ces mêmes scripts pour Windows et Linux.

Les données locales (`data/`, `logs/`), les archives de release et les fichiers
`.env` privés sont ignorés par Git ; `.env.example` reste versionné.

## 📄 Licence

GNU General Public License v3.0 (GPL-3.0-only) - Voir [LICENSE](LICENSE)
