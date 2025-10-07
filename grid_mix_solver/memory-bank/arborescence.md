grid_mix_solver/
├─ __pycache__/               # Cache Python
├─ configs/                   # Configurations et exemples (placeholder)
│    └─ examples/            # Exemples de configurations
├─ main.py                    # Point d'entrée refactorisé avec paramètres en haut
├─ memory-bank/
│    └─ arborescence.md      # Arborescence du dépôt (source unique)
├─ README.md                  # Documentation du projet
├─ results/                   # Résultats sauvegardés (solutions_YYYYMMDD_HHMMSS.txt)
│    └─ …
├─ src/                       # Code source refactorisé (nouvelle structure)
│    ├─ __init__.py          # Package principal
│    ├─ config/              # Configuration et validation
│    │    └─ __init__.py
│    ├─ core/                # Logique métier pure
│    │    ├─ __init__.py
│    │    ├─ combinations.py # Algorithmes de combinaisons
│    │    ├─ grid.py         # Calculs de grille et unités
│    │    ├─ percentages.py  # Calculs de pourcentages et scores
│    │    └─ types.py        # Types et interfaces (Config inclut search_combinations)
│    ├─ explorers/           # Exploration et rapports
│    │    ├─ __init__.py
│    │    ├─ grid_explorer.py# Interface principale refactorisée
│    │    └─ report_generator.py # Génération de rapports détaillés
│    ├─ solvers/             # Algorithmes de résolution
│    │    ├─ __init__.py
│    │    ├─ base.py         # Classe de base pour solveurs
│    │    └─ grid_solver.py  # Recherche; toggle search_combinations supporté
│    └─ utils/               # Utilitaires partagés
│         └─ __init__.py
└─ tests/                    # Tests unitaires (placeholder)


