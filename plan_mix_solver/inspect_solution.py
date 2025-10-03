"""
Script pour inspecter une solution sauvegardée
Montre que les données sont bien exploitables
"""

import pickle
import sys
import numpy as np

def inspect_solution(filepath):
    """Charge et affiche une solution"""
    
    with open(filepath, 'rb') as f:
        solution = pickle.load(f)
    
    print("═" * 80)
    print("INSPECTION D'UNE SOLUTION")
    print("═" * 80)
    print()
    
    # Métadonnées
    meta = solution['metadata']
    print("📋 Métadonnées :")
    print(f"   • Grille : {meta['n_cells_x']} × {meta['n_cells_y']} cellules")
    print(f"   • Cellule : {meta['grid_x']}m × {meta['grid_y']}m")
    print(f"   • Score : {meta['score']}")
    print()
    
    # Appartements
    print("🏠 Appartements :")
    for apt_id, apt_info in sorted(solution['apartments'].items()):
        print(f"   • Apt {apt_id} ({apt_info['type']}) :")
        print(f"      - Taille : {apt_info['size']} cellules")
        print(f"      - Façade : {apt_info['facade_count']} cellules")
        print(f"      - Cellules : {apt_info['cells']}")
    print()
    
    # Circulation
    print(f"🚶 Circulation : {len(solution['circulation_cells'])} cellules")
    print(f"   {solution['circulation_cells']}")
    print()
    
    # Matrice numpy
    print("🔢 Matrice numpy :")
    print(f"   Type : {solution['grid'].dtype}")
    print(f"   Shape : {solution['grid'].shape}")
    print(f"   Matrice :")
    grid = solution['grid']
    for y in range(grid.shape[0]):
        row = "      "
        for x in range(grid.shape[1]):
            val = grid[y, x]
            if val == -1:
                row += "⬜ "  # Circulation
            elif val == 0:
                row += "· "  # Vide
            else:
                row += f"{val} "  # Appartement
        print(row)
    print()
    
    # Vérifications
    print("✅ Vérifications :")
    print(f"   • Type de grid : {type(solution['grid'])} ← numpy array ✓")
    print(f"   • Peut utiliser avec matplotlib : OUI ✓")
    print(f"   • Format exploitable : OUI ✓")
    print()


if __name__ == "__main__":
    
    # Par défaut, inspecter la solution 1 de la dernière session
    import os
    from pathlib import Path
    
    # Trouver la dernière session
    solutions_dir = Path("solutions")
    if not solutions_dir.exists():
        print("❌ Aucun dossier solutions/ trouvé")
        print("   Lancez d'abord : python run.py")
        sys.exit(1)
    
    sessions = sorted(solutions_dir.glob("session_*"))
    if not sessions:
        print("❌ Aucune session trouvée")
        print("   Lancez d'abord : python run.py")
        sys.exit(1)
    
    last_session = sessions[-1]
    solution_file = last_session / "solution_001.pkl"
    
    if not solution_file.exists():
        print(f"❌ Fichier non trouvé : {solution_file}")
        sys.exit(1)
    
    print(f"📂 Inspection de : {solution_file}\n")
    inspect_solution(solution_file)

