# Grid Mix Solver v2.0

**Solveur de mix d'appartements sur grille** - Conçu pour l'architecture et les concours

## 🎯 Objectif

Ce projet trouve la configuration optimale (dimensions de grille + nombre d'éléments) pour respecter des pourcentages de surface imposés par un programme de concours architectural.

## 🏗️ Architecture refactorisée

### Structure modulaire

```
src/
├── config/          # Configuration et validation
├── core/            # Logique métier pure
├── solvers/         # Algorithmes de résolution
├── explorers/       # Exploration et rapports
└── utils/           # Utilitaires partagés
```

### Avantages de la nouvelle structure

- ✅ **Séparation claire des responsabilités**
- ✅ **Modularité améliorée** - Facilite les tests et la maintenance
- ✅ **Extensibilité** - Ajout facile de nouveaux solveurs
- ✅ **Compatibilité** - L'ancien code fonctionne toujours

## 🚀 Utilisation

### Nouvelle interface (recommandée)

```bash
python main.py
```

### Ancienne interface (toujours fonctionnelle)

```bash
python run.py
```

## 📋 Configuration

Modifiez les paramètres dans `main.py` :

- **Surfaces des appartements** : `apt_areas`
- **Pourcentages cibles** : `target_percentages`
- **Plages de recherche** : `search_range_x`, `search_range_y`
- **Contraintes du projet** : `nombre_logements`, `max_etages_par_batiment`

## 📊 Résultats

Les solutions sont sauvegardées dans `results/solutions_YYYYMMDD_HHMMSS.txt` avec :

- Configuration optimale de grille
- Pourcentages obtenus vs cibles
- Analyse du projet (étages, bâtiments, empreinte au sol)
- Combinaisons possibles d'appartements

## 🔧 Développement

### Structure des modules

- **`core/`** : Fonctions de base (calculs, combinaisons, pourcentages)
- **`solvers/`** : Algorithmes de résolution (GridSolver, etc.)
- **`explorers/`** : Interface utilisateur et génération de rapports
- **`config/`** : Configuration et validation des paramètres

### Ajout d'un nouveau solveur

1. Créer une classe héritant de `BaseSolver`
2. Implémenter la méthode `solve()`
3. L'ajouter dans `explorers/grid_explorer.py`

## 📈 Exemple de sortie

```
🏆 Meilleure : Grille 3.6×3.200m, 38 éléments, score 3.00
💾 Résultats détaillés dans : results/solutions_20251003_092243.txt
```

## 🔄 Migration

- **Ancien code** : `run.py`, `solver.py`, `explorer.py` (conservés)
- **Nouveau code** : `main.py` + modules dans `src/`
- **Compatibilité** : 100% - même interface utilisateur

## 📝 Notes

- Le projet utilise des types Python modernes (dataclasses, typing)
- Optimisations : cache des combinaisons, algorithmes efficaces
- Documentation intégrée dans le code
