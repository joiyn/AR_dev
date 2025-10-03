"""
═══════════════════════════════════════════════════════════════════════════════
VISUALISATION DES SOLUTIONS (ÉTAPE 2)
═══════════════════════════════════════════════════════════════════════════════

Ce script lit les solutions .pkl et génère des images PNG

USAGE :
    # Visualiser la dernière session
    python view.py
    
    # Visualiser une session spécifique
    python view.py solutions/session_20251001_094124
    
    # Visualiser un fichier spécifique
    python view.py solutions/session_20251001_094124/solution_001.pkl
"""

import sys
import os
from pathlib import Path
from visualizer import SolutionVisualizer, create_comparison_view


def find_latest_session():
    """Trouve la dernière session de solutions"""
    solutions_dir = Path("solutions")
    if not solutions_dir.exists():
        return None
    
    sessions = sorted(solutions_dir.glob("session_*"))
    return sessions[-1] if sessions else None


def visualize_session(session_dir: Path, create_comparison: bool = True):
    """Visualise toutes les solutions d'une session"""
    
    print("═" * 80)
    print("VISUALISATION DES SOLUTIONS (ÉTAPE 2)")
    print("═" * 80)
    print()
    print(f"📂 Session : {session_dir}")
    print()
    
    # Trouver tous les fichiers .pkl
    solution_files = sorted(session_dir.glob("solution_*.pkl"))
    
    if not solution_files:
        print("❌ Aucun fichier .pkl trouvé dans cette session")
        return
    
    print(f"📊 {len(solution_files)} solution(s) trouvée(s)")
    print()
    
    # Créer le dossier de sortie
    output_dir = session_dir / "images"
    output_dir.mkdir(exist_ok=True)
    
    # Créer le visualiseur
    visualizer = SolutionVisualizer(cell_width=1.2)
    
    # Visualiser chaque solution
    print("🎨 Génération des images individuelles...")
    for solution_file in solution_files:
        solution = visualizer.load_solution(solution_file)
        output_path = output_dir / f"{solution_file.stem}.png"
        visualizer.visualize(
            solution,
            str(output_path),
            show_grid=True,
            show_labels=True,
            show_info=True,
            dpi=150
        )
    
    print()
    
    # Créer une vue comparative
    if create_comparison and len(solution_files) > 1:
        print("🎨 Génération de la vue comparative...")
        comparison_path = output_dir / "comparison.png"
        create_comparison_view(
            [str(f) for f in solution_files[:min(9, len(solution_files))]],
            str(comparison_path),
            max_cols=3
        )
        print()
    
    print("═" * 80)
    print("✅ VISUALISATION TERMINÉE")
    print("═" * 80)
    print(f"📁 Images générées dans : {output_dir}")
    print()
    print("Fichiers créés :")
    for img_file in sorted(output_dir.glob("*.png")):
        size_kb = img_file.stat().st_size / 1024
        print(f"   • {img_file.name} ({size_kb:.1f} KB)")
    print()


def visualize_single_file(filepath: Path):
    """Visualise un seul fichier .pkl"""
    
    print("═" * 80)
    print("VISUALISATION D'UNE SOLUTION")
    print("═" * 80)
    print()
    print(f"📄 Fichier : {filepath}")
    print()
    
    # Créer le dossier de sortie à côté du fichier
    output_path = filepath.parent / f"{filepath.stem}.png"
    
    # Visualiser
    visualizer = SolutionVisualizer(cell_width=1.2)
    solution = visualizer.load_solution(str(filepath))
    visualizer.visualize(
        solution,
        str(output_path),
        show_grid=True,
        show_labels=True,
        show_info=True,
        dpi=150
    )
    
    print()
    print("═" * 80)
    print("✅ TERMINÉ")
    print("═" * 80)
    print(f"📄 Image : {output_path}")
    print()


if __name__ == "__main__":
    
    # Déterminer ce qu'il faut visualiser
    if len(sys.argv) > 1:
        # Chemin fourni en argument
        target = Path(sys.argv[1])
        
        if target.is_file() and target.suffix == '.pkl':
            # Fichier .pkl spécifique
            visualize_single_file(target)
        
        elif target.is_dir():
            # Dossier de session
            visualize_session(target)
        
        else:
            print(f"❌ Chemin invalide : {target}")
            print()
            print("USAGE :")
            print("  python view.py                              # Dernière session")
            print("  python view.py solutions/session_XXXXXX     # Session spécifique")
            print("  python view.py path/to/solution_001.pkl     # Fichier spécifique")
            sys.exit(1)
    
    else:
        # Par défaut : dernière session
        session = find_latest_session()
        
        if session is None:
            print("❌ Aucune session trouvée dans solutions/")
            print()
            print("💡 Lancez d'abord : python run.py")
            sys.exit(1)
        
        visualize_session(session)

