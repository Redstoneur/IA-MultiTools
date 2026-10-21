#!/usr/bin/env python
"""
Script de lancement pour IA-MultiTools.

Ce script peut être exécuté directement depuis la racine du projet.
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importer et lancer l'application
from ia_multitools.main import main

if __name__ == "__main__":
    sys.exit(main())

