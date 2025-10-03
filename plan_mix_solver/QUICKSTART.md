# 🚀 Démarrage Rapide - plan_mix_solver

Guide ultra-rapide pour générer des plans d'appartements.

---

## ✅ Le projet est prêt !

- ✅ **Étape 1** : Génération de solutions (matrices numpy)
- ✅ **Étape 2** : Visualisation (images PNG)
- ✅ **Test réussi** : 54 solutions → 11 images PNG

---

## 📦 Installation

```bash
cd plan_mix_solver
pip install -r requirements.txt
```

---

## ⚡ Usage ultra-rapide

### Workflow complet en 2 commandes

```bash
# 1. Générer les solutions (fichiers .pkl)
python run.py

# 2. Visualiser (fichiers .png)
python view.py
```

**C'est tout !** Les images sont dans `solutions/session_YYYYMMDD_HHMMSS/images/`

---

## 🎨 Résultat

### Ce que vous obtenez

**Étape 1** (run.py) :
```
✅ 54 solution(s) trouvée(s)
📁 Fichiers dans : solutions/session_20251001_094124/
```

**Étape 2** (view.py) :
```
✅ 11 image(s) générée(s)
📁 Images dans : solutions/session_20251001_094124/images/
```

### Fichiers générés

```
solutions/session_YYYYMMDD_HHMMSS/
├─ solution_001.pkl, solution_002.pkl, ...  ← Données (matrices)
└─ images/
   ├─ solution_001.png  ← Plan individuel (55 KB)
   ├─ solution_002.png
   ├─ ...
   └─ comparison.png    ← Vue comparative (92 KB)
```

---

## ⚙️ Configuration

Éditez `run.py` pour changer :

```python
# Dimensions du bâtiment
n_cells_x = 8    # Largeur en cellules
n_cells_y = 4    # Hauteur en cellules

# Circulation (coordonnées x, y)
circulation_cells = [
    (2, 0), (2, 1), (2, 2), (2, 3),  # Colonne verticale
]

# Appartements à placer
apartments = {
    "2.5p": 4.0,   # Un 2.5 pièces de 4 cellules
    "3.5p": 5.0,   # Un 3.5 pièces de 5 cellules
}
```

---

## 📋 Contraintes automatiques

Le solver respecte automatiquement :

1. ✅ **Connexité** : Cellules adjacentes
2. ✅ **Circulation** : Contact obligatoire
3. ✅ **Façade** : Minimum de cellules en périmètre
   - 2.5p → ≥2 cellules
   - 3.5p → ≥3 cellules
   - 4.5p → ≥4 cellules
   - 5.5p → ≥5 cellules

---

## 🎯 Exemples d'utilisation

### Exemple 1 : Configuration par défaut

```bash
python run.py && python view.py
```

→ Génère des plans pour 2 appartements (2.5p + 3.5p) sur une grille 8×4

### Exemple 2 : Visualiser une session spécifique

```bash
python view.py solutions/session_20251001_094124
```

### Exemple 3 : Inspecter les données brutes

```bash
python inspect_solution.py
```

→ Affiche les matrices numpy et métadonnées

---

## 🔍 Options avancées

### Personnaliser la visualisation

Éditez `view.py` ou utilisez directement `visualizer.py` :

```python
from visualizer import SolutionVisualizer

visualizer = SolutionVisualizer(cell_width=1.5)  # Cellules plus grandes
visualizer.visualize(
    solution,
    "output.png",
    show_grid=True,      # Afficher la grille
    show_labels=True,    # Afficher les labels
    show_info=True,      # Panneau d'infos
    dpi=300              # Haute résolution
)
```

### Workflow intégré avec grid_mix_solver

```bash
# 1. Trouver les combinaisons optimales
cd ../grid_mix_solver
python run.py

# 2. Choisir une combinaison (ex: 5.5 + 7.5 + 9 + 9 = 31)
cd ../plan_mix_solver

# 3. Configurer run.py avec cette combinaison
# Éditer : apartments = {"2.5p": 5.5, "3.5p": 7.5, ...}

# 4. Générer et visualiser
python run.py && python view.py
```

---

## ⚠️ Troubleshooting

### Aucune solution trouvée

**Causes possibles** :
- Trop d'appartements pour la grille disponible
- Contraintes de façade trop strictes
- Circulation mal placée

**Solutions** :
```python
# Augmenter la grille
n_cells_x = 10  # Au lieu de 8
n_cells_y = 5   # Au lieu de 4

# Ou réduire les appartements
apartments = {
    "2.5p": 3.0,  # Au lieu de 4.0
}
```

### Calcul trop long

**Solutions** :
- Réduire `max_solutions` (défaut: 10)
- Réduire la taille de la grille
- Réduire le nombre d'appartements

```python
max_solutions = 5  # Au lieu de 10
```

---

## 📚 Documentation complète

Voir `README.md` pour :
- Structure des données en détail
- Algorithme de backtracking
- API du visualizer
- Améliorations futures

---

## 🎨 Personnalisation visuelle

Les couleurs et styles sont dans `visualizer.py` :

```python
APARTMENT_COLORS = [
    '#FFB6C1',  # Rose
    '#87CEEB',  # Bleu
    '#98FB98',  # Vert
    # ... modifiez à votre guise !
]
```

---

## ✨ Résumé

```
1. Configuration → run.py
2. Génération → python run.py
3. Visualisation → python view.py
4. Profit ! 🎉
```

**Le projet est complet et fonctionnel. Bon courage avec vos plans ! 🏗️**

