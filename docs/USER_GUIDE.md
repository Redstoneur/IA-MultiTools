# Guide Utilisateur - IA-MultiTools

## Introduction

Bienvenue dans IA-MultiTools, votre assistant linguistique intelligent!

Cette application vous permet d'utiliser la puissance de l'IA pour:
- Obtenir des définitions claires de mots et concepts
- Trouver des synonymes et antonymes
- Corriger vos textes
- Améliorer vos e-mails professionnels

## Installation

### Prérequis

- Windows 10/11 ou Linux (Ubuntu 22.04+)
- Un serveur IA compatible OpenAI (local ou distant)

### Installation depuis l'exécutable

1. Téléchargez l'exécutable pour votre système depuis la page Releases
2. **Windows**: Double-cliquez sur `IA-MultiTools.exe`
3. **Linux**: 
   ```bash
   chmod +x IA-MultiTools
   ./IA-MultiTools
   ```

### Installation depuis les sources

```bash
# Cloner le projet
git clone <url>
cd IA-MultiTools

# Installer Python 3.12+
# Windows: Téléchargez depuis python.org
# Linux: sudo apt install python3.12

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python -m src.ia_multitools.main
```

## Configuration initiale

Au premier lancement:

1. Cliquez sur **⚙ Paramètres**
2. Allez dans l'onglet **🤖 Configuration IA**
3. Configurez votre connexion IA:

### Pour LM Studio (IA locale)

- **URL de base**: `http://127.0.0.1:1234/v1`
- **Clé API**: `lm-studio` (ou n'importe quoi)
- **Modèle**: Le nom du modèle chargé dans LM Studio
- **Température**: `0.2` (recommandé pour précision)

### Pour OpenAI (officiel)

- **URL de base**: `https://api.openai.com/v1`
- **Clé API**: Votre clé API OpenAI
- **Modèle**: `gpt-4` ou `gpt-3.5-turbo`
- **Vérifier SSL**: ✓ Activé

4. Cliquez sur **🔍 Tester la connexion** pour vérifier
5. Cliquez sur **💾 Sauvegarder**

## Utilisation des outils

### 📖 Définition

Obtenez la définition d'un mot ou concept.

**Étapes:**
1. Accédez à l'onglet **📖 Définition**
2. Entrez le mot ou concept dans le champ
3. (Optionnel) Limitez le nombre de mots de la réponse
4. Choisissez le format (Texte ou Markdown)
5. Cliquez sur **🔍 Générer la définition**
6. La définition s'affiche dans la zone de résultat
7. Utilisez **📋 Copier** pour copier dans le presse-papiers

**Exemples:**
- "Intelligence artificielle"
- "Synapse"
- "Résilience"

### 🔄 Synonymes et Antonymes

Trouvez des synonymes et/ou antonymes d'un mot.

**Étapes:**
1. Accédez à l'onglet **🔄 Synonymes**
2. Entrez un mot
3. Choisissez le mode:
   - **Synonymes**: seulement les synonymes
   - **Antonymes**: seulement les antonymes
   - **Les deux**: les deux listes
4. Cliquez sur **🔍 Générer**
5. La liste s'affiche

**Exemples:**
- "Rapide" → Synonymes: vif, prompt, véloce...
- "Grand" → Antonymes: petit, minuscule, réduit...

### ✏️ Correction de texte

Corrigez l'orthographe, la grammaire et le style de vos textes.

**Étapes:**
1. Accédez à l'onglet **✏️ Correction**
2. Collez ou tapez votre texte
3. (Optionnel) Ajoutez des instructions spécifiques
4. Cliquez sur **✓ Corriger**
5. Le texte corrigé s'affiche en bas

**Instructions spéciales:**

Vous pouvez inclure des directives dans votre texte avec `<instruction>`:

```
Voici mon text avec des faute.

<instruction>Rends ce texte plus formel et professionnel</instruction>
```

**Exemples d'instructions:**
- "Simplifie les phrases"
- "Utilise un ton plus formel"
- "Corrige uniquement l'orthographe"

### 📧 E-mails

Améliorez et professionnalisez vos e-mails.

**Étapes:**
1. Accédez à l'onglet **📧 E-mails**
2. Écrivez ou collez votre e-mail
3. Activez les options:
   - **Rendre professionnel**: Ton plus formel
   - **Ajouter formule de politesse**: Commence par "Bonjour,"
4. (Optionnel) Ajoutez des instructions
5. Cliquez sur **✓ Corriger l'e-mail**

**Exemple:**

**Avant:**
```
salut je voulait savoir si tu pourrais m'aider avec le projet
```

**Après (avec options activées):**
```
Bonjour,

Je me permets de vous contacter afin de solliciter votre aide concernant le projet.

Cordialement,
```

## Paramètres avancés

### Sécurité

#### Chiffrement

- **Activer le chiffrement**: Chiffre toutes vos données (recommandé)
- **Utiliser le trousseau système**: Stocke les secrets dans le trousseau Windows/Linux

#### Verrouillage

- **Verrouillage de l'application**: Demande authentication au démarrage
- **Verrouillage automatique**: Verrouille après inactivité
  - Options: Désactivé, 5, 15, 30 ou 60 minutes

### Apparence

Personnalisez l'interface:

**Thèmes disponibles:**
- **darkly**: Sombre (par défaut)
- **solar**: Orange/gris
- **superhero**: Bleu/orange
- **cyborg**: Bleu sombre
- **vapor**: Rose/violet
- **cosmo**: Bleu clair
- **flatly**: Vert
- **journal**: Classique
- **litera**: Moderne clair

**Taille de police**: 8 à 18

⚠ Le changement de thème nécessite un redémarrage.

### Prompts système

Personnalisez les instructions données à l'IA pour chaque outil.

**Accès:** Paramètres → 📝 Prompts système

Vous pouvez modifier les prompts pour:
- Définition
- Synonymes
- Correction de texte
- E-mails

**Exemple de personnalisation:**

Pour des définitions plus détaillées:
```
Tu es un expert en linguistique. Fournis une définition détaillée
et académique du terme demandé, avec des exemples d'utilisation.
```

## Historique

L'application conserve un historique chiffré de toutes vos requêtes et réponses.

**Consulter l'historique:**
1. Menu **Outils** → **Historique**
2. Voir les statistiques d'utilisation

**Confidentialité:**
- L'historique est chiffré avec Fernet
- Stocké localement uniquement
- Pas de partage avec des tiers

**Nettoyage automatique:**

Par défaut, les entrées de plus de 90 jours sont supprimées automatiquement.

Configuration: Paramètres → Historique → Nettoyage automatique

## Dépannage

### L'application ne démarre pas

**Windows:**
- Vérifiez que vous avez Python 3.12+
- Désactivez temporairement l'antivirus
- Lancez en mode administrateur

**Linux:**
- Vérifiez les permissions: `chmod +x IA-MultiTools`
- Installez les dépendances système si nécessaire

### Erreur de connexion IA

**Vérifications:**
1. Le serveur IA est-il démarré?
2. L'URL est-elle correcte?
3. Le modèle est-il chargé (pour services locaux)?
4. Testez avec: Outils → Tester la connexion IA

**LM Studio:**
- Démarrez le serveur local dans LM Studio
- Chargez un modèle
- Vérifiez le port (par défaut 1234)

**OpenAI:**
- Vérifiez votre clé API
- Vérifiez votre quota/crédits
- Activez "Vérifier SSL"

### Les résultats sont incohérents

**Solutions:**
1. Baissez la température (0.1 - 0.3 pour plus de précision)
2. Modifiez les prompts système
3. Essayez un autre modèle
4. Vérifiez les instructions complémentaires

### L'application est lente

**Optimisations:**
1. Utilisez un serveur IA local (LM Studio)
2. Augmentez le timeout
3. Choisissez un modèle plus petit/rapide
4. Vérifiez votre connexion réseau (pour API distantes)

## Astuces et bonnes pratiques

### Définitions

- Soyez spécifique: "intelligence artificielle générative" plutôt que "IA"
- Utilisez la limite de mots pour des réponses courtes

### Synonymes

- Testez avec "Les deux" pour avoir une vue complète
- Les résultats varient selon le contexte du mot

### Correction de texte

- Utilisez les instructions embarquées `<instruction>` pour plus de contrôle
- Divisez les longs textes en plusieurs sections
- Relisez toujours le résultat, l'IA peut faire des erreurs

### E-mails

- Soyez clair dans votre intention initiale
- L'option "Rendre professionnel" change significativement le ton
- Personnalisez après correction si nécessaire

## Raccourcis clavier

- **Ctrl + S**: Sauvegarder (dans paramètres)
- **Ctrl + C**: Copier le résultat
- **Ctrl + V**: Coller dans les zones de texte
- **Ctrl + A**: Sélectionner tout

## Données et confidentialité

### Où sont stockées mes données?

- **Windows**: `%APPDATA%\IA-MultiTools\`
- **Linux**: `~/.config/ia-multitools/`
- **Mode debug**: Dossier de l'application

### Quelles données sont collectées?

- Aucune donnée n'est envoyée à des tiers
- L'historique est stocké localement et chiffré
- Les requêtes vont uniquement au serveur IA configuré

### Puis-je supprimer mes données?

Oui, supprimez simplement le dossier de données mentionné ci-dessus.

## Support et aide

### Besoin d'aide?

- Consultez le README_FULL.md
- Ouvrez une Issue sur GitHub
- Consultez les Discussions GitHub

### Signaler un bug

1. Menu Aide → À propos (notez la version)
2. Consultez les logs (dossier `logs/`)
3. Ouvrez une Issue avec:
   - Description du problème
   - Étapes pour reproduire
   - Version de l'application
   - Système d'exploitation
   - Logs pertinents (sans données sensibles!)

## Mises à jour

Vérifiez régulièrement les nouvelles versions sur GitHub.

**Installer une mise à jour:**
1. Téléchargez la nouvelle version
2. Fermez l'application actuelle
3. Remplacez l'ancien exécutable
4. Relancez l'application

Vos données et configuration sont préservées.

---

**Profitez d'IA-MultiTools!** 🚀

Pour plus d'informations, consultez le README_FULL.md ou la documentation complète.

