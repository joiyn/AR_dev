plan_mix_solver_v3/
├─ solver.py               # Algorithme backtracking avec filtrage similarité configurable
├─ run.py                  # Config (avec paramètres similarité) + exécution + visualisation
├─ inspect_solution.py     # Inspection détaillée d'une solution .pkl
├─ visualizer.py           # Génération PNG avec matplotlib (affiche variance + compacité)
├─ view.py                 # Script visualisation des solutions existantes
├─ README.md               # Documentation complète du projet
├─ QUICKSTART.md           # Guide démarrage rapide
├─ PROMPT_FOR_AI.txt       # Contexte pour IA
├─ requirements.txt        # numpy, matplotlib
├─ results/                # Résultats de tests
│    └─ test_simple/       # Test simple
├─ memory-bank/            # Banque mémoire unique
│    └─ arborescence.md    # Vue hiérarchique du dépôt
└─ solutions/              # Fichiers .pkl et images PNG par session
    └─ session_*/          # Dossiers session (YYYYMMDD_HHMMSS)
         ├─ data/          # Fichiers .pkl (matrices numpy)
         └─ images/        # PNG générés + comparison.png

