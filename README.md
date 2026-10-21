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

## 🔐 Sécurité

- Chiffrement Fernet avec une clé aléatoire conservée dans le trousseau système
- Clé API stockée uniquement dans le trousseau système, jamais dans le fichier de configuration
- Trousseau système fonctionnel requis (Credential Manager sous Windows, Secret Service sous Linux)
- Historique chiffré
- Verrouillage automatique optionnel

## 📚 Documentation

Voir [README_FULL.md](README_FULL.md) pour la documentation complète.

## 📄 Licence

GNU General Public License v3.0 (GPL-3.0-only) - Voir [LICENSE](LICENSE)
