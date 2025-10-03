grid_mix_solver/
├─ __pycache__/               # Cache Python
├─ src/                       # Code source refactorisé (nouvelle structure)
│  ├─ __init__.py            # Package principal
│  ├─ config/                # Configuration et validation
│  │  ├─ __init__.py
│  │  ├─ settings.py         # Configuration par défaut
│  │  └─ validators.py       # Validation des paramètres
│  ├─ core/                  # Logique métier pure
│  │  ├─ __init__.py
│  │  ├─ grid.py             # Calculs de grille et unités
│  │  ├─ combinations.py     # Algorithmes de combinaisons
│  │  ├─ percentages.py      # Calculs de pourcentages et scores
│  │  └─ types.py            # Types et interfaces (Solution, Config, etc.)
│  ├─ solvers/               # Algorithmes de résolution
│  │  ├─ __init__.py
│  │  ├─ base.py             # Classe de base pour solveurs
│  │  ├─ direct_solver.py    # Mode direct (à implémenter)
│  │  ├─ grid_solver.py      # Mode recherche grille (implémenté)
│  │  └─ target_solver.py    # Mode recherche target (à implémenter)
│  ├─ explorers/             # Exploration et rapports
│  │  ├─ __init__.py
│  │  ├─ grid_explorer.py    # Interface principale refactorisée
│  │  └─ report_generator.py # Génération de rapports détaillés
│  └─ utils/                 # Utilitaires partagés
│     ├─ __init__.py
│     ├─ io.py               # Gestion fichiers (à implémenter)
│     └─ formatting.py       # Formatage des résultats (à implémenter)
├─ configs/                  # Configurations et exemples
│  ├─ default.py             # Configuration par défaut (à créer)
│  └─ examples/              # Exemples de configurations (à créer)
├─ tests/                    # Tests unitaires (à créer)
├─ memory-bank/
│  └─ arborescence.md        # Arborescence du dépôt (source unique)
├─ results/                  # Résultats sauvegardés (solutions_YYYYMMDD_HHMMSS.txt)
│  └─ …
├─ main.py                   # Nouveau point d'entrée refactorisé
├─ requirements.txt          # Dépendances (à créer)
└─ README.md                 # Documentation (à créer)


