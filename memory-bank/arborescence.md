AR_dev/
├─ .gitignore                      # Fichiers à ignorer par Git (Python, cache, OS)
├─ grid_mix_solver/                # Projet solveur de grille mixte
│  ├─ __pycache__/                 # Cache Python
│  ├─ explorer.py                  # Logique d'exploration et affichage (ajout: empreinte au sol)
│  ├─ memory-bank/
│  │  └─ arborescence.md          # Arborescence du dépôt (source unique)
│  ├─ results/                     # Résultats sauvegardés (solutions_YYYYMMDD_HHMMSS.txt)
│  │  └─ …
│  ├─ run.py                       # Configuration (paramètres utilisateur, point d'entrée)
│  └─ solver.py                    # Algorithmes de calcul (moteur du solveur)
└─ plan_mix_solver/                # Projet solveur de plan mixte
   ├─ __pycache__/                 # Cache Python
   ├─ inspect_solution.py          # Inspection et analyse des solutions
   ├─ memory-bank/
   │  └─ arborescence.md          # Arborescence du dépôt (source unique)
   ├─ PROMPT_FOR_AI.txt           # Instructions pour l'IA
   ├─ QUICKSTART.md               # Guide de démarrage rapide
   ├─ README.md                   # Documentation principale
   ├─ requirements.txt            # Dépendances Python
   ├─ run.py                      # Point d'entrée principal
   ├─ run2.py                     # Variante d'exécution 2
   ├─ run3.py                     # Variante d'exécution 3
   ├─ run4.py                     # Variante d'exécution 4
   ├─ run5.py                     # Variante d'exécution 5
   ├─ solutions/                  # Solutions générées par session
   │  └─ …                        # Dossiers de sessions avec data/ et images/
   ├─ solver.py                   # Algorithmes de calcul (moteur du solveur)
   ├─ view.py                     # Interface de visualisation
   └─ visualizer.py               # Outils de visualisation des solutions
