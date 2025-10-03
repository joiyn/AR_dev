"""
═══════════════════════════════════════════════════════════════════════════════
GÉNÉRATION DE SOLUTIONS DE PLACEMENT (ÉTAPE 1)
═══════════════════════════════════════════════════════════════════════════════

Ce script génère les solutions de placement sous forme de données (matrices numpy)
qui seront ensuite visualisées avec matplotlib (étape 2, à venir).

USAGE :
    python run.py
    
SORTIE :
    - Fichiers .pkl dans le dossier solutions/
    - Résumé textuel dans la console
"""

from solver import ApartmentSolver, print_solution_summary
import pickle
import os
from datetime import datetime
from visualizer import SolutionVisualizer, create_comparison_view

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Dimensions de la cellule unitaire (en mètres)
grid_x = 3.7
grid_y = 3.7

# Dimensions du bâtiment (en nombre de cellules)
n_cells_x = 8
n_cells_y = 5

# Circulation sur la grille principale (coordonnées x, y de cellules)
# ⚠️ ATTENTION : (0, 0) = coin haut-gauche
circulation_cells = [
    (2, 2),
    (3, 2),
    (4, 2),
    (5, 2),
]

# Circulation fine (optionnel) sur la sous-grille 2x (coordonnées de sous-cellules)
# Exemple: pour marquer seulement la moitié supérieure de (4,1), utiliser [(4*2,1*2), (4*2+1,1*2)]
# Laisser None pour ne pas utiliser
fine_circulation_cells = None
# [
#     (12, 4),
#     (12, 5),
#     (3, 4),
#     (3, 5),
# ]

# Appartements à placer
# Format accepté :
#   - Liste de tuples [("type", taille_en_cellules), ...] pour autoriser les doublons
#   - OU dict {"type": taille_en_cellules} (doublons non supportés par le type dict)
# apartments = [
#     ("4.5p", 7.5),
#     ("5.5p", 8.5),
#     ("5.5p", 8.5),
#     ("5.5p", 8.5)
# ]
apartments = [
    ("2.5p", 5),
    ("3.5p", 7),
    ("3.5p", 7),
    ("4.5p", 7.5),
    ("5.5p", 8.5),
]

# Nombre maximum de solutions à générer
max_solutions = 100

# Contrainte de façade personnalisée (optionnel)
# Par défaut: round(nombre_de_pieces - 1.5), min 0
# Exemple: {"2.5p": 1, "3.5p": 2, "4.5p": 3}
min_facade_cells = {
    "2.5p": 1,
    "3.5p": 2,
    "4.5p": 3,
    "5.5p": 4
    }  # ou {"2.5p": 1} pour forcer 1 cellule en façade pour 2.5p

# Dossier de sortie
output_dir = "solutions"

# Limite d'enfilade (couloir): nombre max de cellules en file par appartement
# Exemple: 2 → jusqu'à 2 cellules peuvent former un couloir
max_enfilade_cells_per_apartment = 1

# ═══════════════════════════════════════════════════════════════════════════
# PARAMÈTRES DE SIMILARITÉ GÉOMÉTRIQUE
# ═══════════════════════════════════════════════════════════════════════════

# Poids de la variance de forme dans le score (plus élevé = plus de similarité exigée)
# Valeurs recommandées :
#   - 10   : Similarité faible (formes variées acceptées)
#   - 50   : Similarité moyenne
#   - 100  : Similarité forte (formes très proches)
#   - 200+ : Similarité très forte (formes quasi identiques)
shape_variance_weight = 10

# Seuil de variance pour le filtrage final (multiplicateur)
# Définit la tolérance par rapport aux meilleures solutions
# Valeurs recommandées :
#   - 1.2  : Très strict (seulement les plus similaires)
#   - 1.5  : Strict (défaut)
#   - 2.0  : Modéré (plus de variations acceptées)
#   - 3.0+ : Permissif (variations importantes acceptées)
variance_filter_threshold = 3

# Nombre max de placements testés par appartement
# Réduit l'exploration pour privilégier la qualité sur la quantité
# Valeurs recommandées :
#   - 20-30  : Rapide, très sélectif
#   - 30-50  : Équilibré (défaut)
#   - 50-100 : Plus d'exploration, moins sélectif
max_placement_tries = 1000

# ═══════════════════════════════════════════════════════════════════════════
# PARAMÈTRES DE VISUALISATION
# ═══════════════════════════════════════════════════════════════════════════
show_grid = True
show_labels = True
show_info = True
dpi = 150
cell_width_inches = 1.2  # largeur visuelle d'une cellule
max_comparison_cols = 3   # nb max de colonnes pour la vue comparative


# ═══════════════════════════════════════════════════════════════════════════
# EXÉCUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 80)
    print("GÉNÉRATION DE SOLUTIONS DE PLACEMENT (ÉTAPE 1 : DONNÉES + ÉTAPE 2 : IMAGES)")
    print("═" * 80)
    print()

    # Créer le solveur
    solver = ApartmentSolver(
        grid_x=grid_x,
        grid_y=grid_y,
        n_cells_x=n_cells_x,
        n_cells_y=n_cells_y,
        circulation_cells=circulation_cells,
        apartments_to_place=apartments,
        max_solutions=max_solutions,
        min_facade_cells=min_facade_cells,
        fine_circulation_cells=fine_circulation_cells,
        max_enfilade_cells_per_apartment=max_enfilade_cells_per_apartment,
        shape_variance_weight=shape_variance_weight,
        variance_filter_threshold=variance_filter_threshold,
        max_placement_tries=max_placement_tries
    )

    # Générer les solutions
    solutions = solver.solve()

    if not solutions:
        print("❌ Aucune solution trouvée")
        print()
        print("💡 SUGGESTIONS :")
        print("   • Vérifier que la somme des appartements ≤ cellules disponibles")
        print("   • Réduire les tailles des appartements")
        print("   • Augmenter la taille du bâtiment (n_cells_x, n_cells_y)")
        print("   • Vérifier que les contraintes de façade sont réalistes")
        print()
    else:
        # Créer le dossier de sortie
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(output_dir, f"session_{timestamp}")
        data_dir = os.path.join(session_dir, "data")
        images_dir = os.path.join(session_dir, "images")
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        print("═" * 80)
        print(f"RÉSUMÉ DES SOLUTIONS")
        print("═" * 80)
        print()

        solution_files = []

        # Afficher et sauvegarder chaque solution
        for i, solution in enumerate(solutions, 1):
            # Afficher
            print_solution_summary(solution, i)

            # Sauvegarder dans le dossier data/
            output_path = os.path.join(data_dir, f"solution_{i:03d}.pkl")
            with open(output_path, 'wb') as f:
                pickle.dump(solution, f)
            solution_files.append(output_path)

            print(f"   💾 Saved: {output_path}\n")

        print("═" * 80)
        print("🎨 GÉNÉRATION DES IMAGES")
        print("═" * 80)

        visualizer = SolutionVisualizer(cell_width=cell_width_inches)
        # Visualiser chaque solution
        for pkl_path in solution_files:
            solution = visualizer.load_solution(pkl_path)
            img_path = os.path.join(images_dir, os.path.basename(pkl_path).replace('.pkl', '.png'))
            visualizer.visualize(
                solution,
                img_path,
                show_grid=show_grid,
                show_labels=show_labels,
                show_info=show_info,
                dpi=dpi
            )

        # Vue comparative (TOUTES les solutions)
        if len(solution_files) > 1:
            comparison_path = os.path.join(images_dir, "comparison.png")
            create_comparison_view(solution_files, comparison_path, max_cols=max_comparison_cols)

        print("═" * 80)
        print("✅ TERMINÉ")
        print("═" * 80)
        print(f"📊 {len(solutions)} solution(s) générée(s)")
        print(f"📁 Session folder: {session_dir}")
        print(f"💾 Data files (.pkl): {data_dir}")
        print(f"🖼️  Images (.png): {images_dir}")
        print()

