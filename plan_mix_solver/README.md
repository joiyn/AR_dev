# Plan Mix Solver - Générateur de solutions de placement

Solveur de placement d'appartements sur grille 2D avec contraintes architecturales.

## 🎯 Architecture en 2 étapes

### ✅ Étape 1 : Génération de données (TERMINÉ)

Le solver génère toutes les configurations possibles et les sauvegarde sous forme de **matrices numpy**.

**Fichiers** :
- `solver.py` : Algorithme de backtracking
- `run.py` : Configuration et exécution
- `inspect_solution.py` : Inspection des solutions sauvegardées

**Sortie** : Fichiers `.pkl` dans `solutions/session_YYYYMMDD_HHMMSS/`

### ✅ Étape 2 : Visualisation (TERMINÉ)

Le visualizer lit les fichiers `.pkl` et génère des **images PNG** avec matplotlib.

**Fichiers** :
- `visualizer.py` : Module de visualisation avec matplotlib
- `view.py` : Script d'exécution de la visualisation

**Sortie** : Images PNG dans `solutions/session_YYYYMMDD_HHMMSS/images/`

---

## 🚀 Utilisation complète

### Étape 1 : Générer les solutions

#### 1.1 Configuration

Éditez `run.py` :

```python
# Dimensions de la cellule
grid_x = 3.5  # mètres
grid_y = 3.0  # mètres

# Dimensions du bâtiment
n_cells_x = 8  # cellules
n_cells_y = 4  # cellules

# Circulation (coordonnées x, y)
circulation_cells = [
    (2, 0), (2, 1), (2, 2), (2, 3),
]

# Appartements à placer
apartments = {
    "2.5p": 4.0,   # Type: nombre de cellules
    "3.5p": 5.0,
}
```

#### 1.2 Exécution

```bash
python run.py
```

#### 1.3 Résultat

```
✅ 54 solution(s) trouvée(s)
📊 Retour des 10 meilleures
📁 Fichiers dans : solutions/session_20251001_094124
```

### Étape 2 : Visualiser les solutions

```bash
# Visualiser automatiquement la dernière session
python view.py

# Ou spécifier une session
python view.py solutions/session_20251001_094124

# Ou visualiser un fichier spécifique
python view.py solutions/session_20251001_094124/solution_001.pkl
```

#### Résultat

```
✅ VISUALISATION TERMINÉE
📁 Images générées dans : solutions/session_20251001_094124/images

Fichiers créés :
   • solution_001.png (55 KB)  ← Plan individuel
   • solution_002.png (55 KB)
   • ...
   • comparison.png (92 KB)    ← Vue comparative
```

### Workflow rapide

```bash
# Tout en une fois
python run.py && python view.py
```

### Inspection (optionnel)

```bash
python inspect_solution.py
```

Affiche les détails bruts d'une solution (matrices, coordonnées, etc.)

---

## 📊 Structure des données

Chaque solution est un dictionnaire Python sauvegardé en `.pkl` :

```python
{
    "grid": np.array([
        [1, 1, -1, 2, 2, 2, 0, 0],  # -1=circulation, 0=vide, 1,2=appartements
        [1, 0, -1, 0, 2, 0, 0, 0],
        [1, 0, -1, 0, 2, 0, 0, 0],
        [0, 0, -1, 0, 0, 0, 0, 0],
    ]),
    
    "apartments": {
        1: {
            "type": "2.5p",
            "size": 4.0,
            "cells": [(0,0), (1,0), (0,1), (0,2)],
            "facade_count": 4
        },
        2: {
            "type": "3.5p",
            "size": 5.0,
            "cells": [(3,0), (4,0), (5,0), (4,1), (4,2)],
            "facade_count": 3
        },
    },
    
    "circulation_cells": [(2,0), (2,1), (2,2), (2,3)],
    
    "metadata": {
        "grid_x": 3.5,
        "grid_y": 3.0,
        "n_cells_x": 8,
        "n_cells_y": 4,
        "score": 0
    }
}
```

---

## 📋 Contraintes respectées

1. **Connexité** : Toutes les cellules d'un appartement sont adjacentes (4-connexité)
2. **Circulation** : Chaque appartement touche au moins une cellule de circulation
3. **Façade minimale** : 
   - 2.5p → ≥2 cellules en façade
   - 3.5p → ≥3 cellules en façade
   - 4.5p → ≥4 cellules en façade
   - 5.5p → ≥5 cellules en façade

---

## 📝 Exemple de résultat

```
🏆 Solution 1 (score: 0)
   Grille : 8 × 4
   • Apt 1 (2.5p) : 4.0 cellules, 4 en façade, 4 cellules utilisées
   • Apt 2 (3.5p) : 5.0 cellules, 3 en façade, 5 cellules utilisées
   Matrice :
       1  1 ⬜  2  2  2       
       1    ⬜     2          
       1    ⬜     2          
            ⬜                
```

Légende :
- `⬜` = Circulation
- `1, 2, 3...` = ID de l'appartement
- ` ` (vide) = Cellule libre

---

## 🔄 Workflow complet

```
1. Configuration (run.py)
   ↓
2. Génération (solver.py) ← ÉTAPE 1 ✅
   ↓
3. Sauvegarde (.pkl)
   ↓
4. Visualisation (view.py) ← ÉTAPE 2 ✅
   ↓
5. Images PNG
```

---

## ⚙️ Algorithme

L'algorithme utilise du **backtracking avec contraintes** :

1. Placer les appartements un par un
2. Pour chaque appartement :
   - Trouver tous les placements possibles (flood-fill)
   - Vérifier les contraintes (connexité, circulation, façade)
   - Si valide → continuer avec l'appartement suivant
   - Sinon → backtrack
3. Sauvegarder les solutions valides

**Complexité** : NP-complet (peut être long pour grandes grilles)

---

## 🎯 Améliorations futures

- [ ] Gérer les cellules coupées (0.5) pour tailles non-entières
- [ ] Optimiser la vitesse de calcul (parallélisation, pruning)
- [ ] Ajouter d'autres critères de scoring (compacité, orientation, etc.)
- [ ] Export en DXF/SVG pour CAO
- [ ] Interface graphique interactive

---

## 💾 Dépendances

```bash
pip install -r requirements.txt
```

Contenu :
- `numpy>=1.21.0` (matrices de données)
- `matplotlib>=3.5.0` (visualisation)

---

## 📸 Exemple de sortie

**Image individuelle** : Plan détaillé avec :
- Couleurs différentes par appartement
- Labels avec type et taille
- Marqueurs de circulation
- Panneau d'informations (grille, surfaces, façades)

**Vue comparative** : Grille 3×3 montrant jusqu'à 9 solutions côte à côte

---

**Status** : ✅ Projet complet et fonctionnel
- ✅ Étape 1 : 54 solutions générées
- ✅ Étape 2 : 11 images PNG créées
