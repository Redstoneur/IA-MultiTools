# Guide de contribution

Merci de votre intérêt pour contribuer à IA-MultiTools ! Ce document fournit les lignes directrices pour contribuer au projet.

## Code de conduite

Soyez respectueux, professionnel et constructif dans toutes les interactions.

## Comment contribuer

### Signaler des bugs

1. Vérifiez que le bug n'a pas déjà été signalé dans les Issues
2. Créez une nouvelle Issue avec:
   - Un titre descriptif
   - Les étapes pour reproduire le bug
   - Le comportement attendu vs observé
   - Votre environnement (OS, version Python)
   - Les logs pertinents (sans informations sensibles)

### Proposer des fonctionnalités

1. Ouvrez une Issue pour discuter de la fonctionnalité
2. Attendez les retours avant de commencer le développement
3. Assurez-vous que la fonctionnalité s'aligne avec les objectifs du projet

### Soumettre des modifications

1. **Fork** le projet
2. **Créez une branche** pour votre fonctionnalité (`git checkout -b feature/MaFonctionnalite`)
3. **Committez** vos changements (`git commit -m 'Ajout de MaFonctionnalite'`)
4. **Poussez** vers la branche (`git push origin feature/MaFonctionnalite`)
5. **Ouvrez une Pull Request**

## Standards de code

### Style Python

- Suivez **PEP 8**
- Utilisez **Black** pour le formatage (ligne max: 100 caractères)
- Utilisez **type hints** pour toutes les fonctions
- Ajoutez des **docstrings** pour toutes les classes et fonctions publiques

Exemple:
```python
def ma_fonction(param: str, count: int = 5) -> list[str]:
    """
    Description courte de la fonction.
    
    Args:
        param: Description du paramètre
        count: Nombre d'éléments à retourner (défaut: 5)
    
    Returns:
        Liste de chaînes de caractères
    
    Raises:
        ValueError: Si count est négatif
    """
    pass
```

### Architecture

- **Séparation stricte** UI / Services / Core
- **Aucune logique métier** dans les fichiers UI
- Utilisez des **dataclasses** pour les modèles de données
- Privilégiez la **composition** à l'héritage

### Sécurité

- Ne commitez **jamais** de secrets, clés API ou données sensibles
- Utilisez le système de chiffrement fourni pour toute donnée utilisateur
- Validez toutes les entrées utilisateur
- Gérez les erreurs de manière appropriée

### Tests

- Écrivez des tests unitaires pour les nouvelles fonctionnalités
- Assurez-vous que tous les tests passent avant de soumettre
- Visez une couverture de code > 80%

Exécuter les tests:
```bash
pytest tests/
```

### Documentation

- Mettez à jour le README si nécessaire
- Documentez les nouvelles fonctionnalités dans CHANGELOG.md
- Ajoutez des commentaires pour le code complexe
- Maintenez les docstrings à jour

## Structure du commit

Utilisez des messages de commit clairs et descriptifs:

```
[Type] Résumé court (< 72 caractères)

Description détaillée optionnelle expliquant:
- Pourquoi ce changement est nécessaire
- Comment il résout le problème
- Tout effet secondaire potentiel
```

Types de commit:
- `[Feature]` - Nouvelle fonctionnalité
- `[Fix]` - Correction de bug
- `[Refactor]` - Refactoring sans changement de fonctionnalité
- `[Docs]` - Documentation uniquement
- `[Test]` - Ajout ou modification de tests
- `[Security]` - Correction de sécurité
- `[Perf]` - Amélioration de performance

## Environnement de développement

### Installation

```bash
# Cloner le repository
git clone https://github.com/votre-username/IA-MultiTools.git
cd IA-MultiTools

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Lancer l'application en mode debug

```bash
python -m src.ia_multitools.main --debug
```

### Outils de qualité

```bash
# Formatage
black src/

# Vérification des types
mypy src/

# Linting
pylint src/

# Tests
pytest tests/ -v --cov=src
```

## Revue de code

Toutes les Pull Requests seront revues. Attendez-vous à:
- Des questions sur les choix de conception
- Des suggestions d'amélioration
- Des demandes de tests supplémentaires
- Des corrections de style ou de documentation

## Licence

En contribuant, vous acceptez que vos contributions soient sous licence GNU General Public License v3.0 (GPL-3.0-only).

## Questions ?

N'hésitez pas à ouvrir une Issue pour toute question !
