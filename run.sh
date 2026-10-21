#!/bin/bash
# Script de lancement pour Linux/Mac

echo "Démarrage de IA-MultiTools..."
echo ""

# Vérifier si l'environnement virtuel existe
if [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Lancer l'application
python run.py "$@"

