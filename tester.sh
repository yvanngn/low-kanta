#!/bin/sh
# Rejoue les tests : sh tester.sh c1   (groupes : menu intro galerie c1 jeu contenu ; sans argument : tout)
cd "$(dirname "$0")" && python3 tests/scenarios.py "$@"
