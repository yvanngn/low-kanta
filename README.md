# Low Kanta

Jeu point and click parodique (téléréalité de survie qui vire au mystère), dessiné et mis en musique par le code.

- Jeu : `low-kanta.html` (fichier unique). Mots de passe : numéro du chapitre (0 = intro, 1 = chapitre 1).
- Bible : `PERSONNAGES.md`. Règles de travail : `CLAUDE.md`.
- Tests : `sh tester.sh [menu intro galerie c1 jeu contenu]` (Python + Playwright).
- Push sur `main` → GitHub Actions rejoue tous les tests puis publie sur GitHub Pages (à activer : Settings → Pages → Source : GitHub Actions).
