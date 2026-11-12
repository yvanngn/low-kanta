# Low Kanta — règles de travail
Mêmes règles que les autres jeux (garde-fou tokens, réponses courtes, lecture ciblée, tout coder puis tester une seule fois).
- Jeu : `low-kanta.html` (fichier unique). Bible : `PERSONNAGES.md`.
- Push sur `main` : GitHub Actions teste et publie sur GitHub Pages ; republier l’artifact claude.ai seulement sur demande.
- Tests : `sh tester.sh <groupe>` (groupes : menu intro galerie c1 jeu contenu), sortie `2>&1 | grep -A3 "ÉCHEC\|vérifications"`. Ne rejouer que le groupe modifié.
- Texte, dessin ou son seulement : pas de tests (sauf texte vérifié dans `tests/scenarios.py`, voir `grep`), `contenu` suffit.
- Toute nouvelle partie ou fonctionnalité = un test dans `tests/scenarios.py` (table `GROUPES`). Ne jamais tester l'absence d'un élément supprimé.
- `contenu` vérifie l'absence des mots interdits (nom de l'émission, du vrai présentateur, origines).

## Interface (skill `interface-jeu`)
- Clic droit : jamais le menu du navigateur dans le jeu (écouteur `contextmenu` sur `#game`, dans `low-kanta.html`), sauf dans les champs de saisie. Testé dans le groupe du menu.
