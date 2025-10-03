"""
═══════════════════════════════════════════════════════════════════════════════
VISUALISEUR DE SOLUTIONS - GÉNÉRATION D'IMAGES PNG
═══════════════════════════════════════════════════════════════════════════════

ÉTAPE 2 : Lit les solutions (.pkl) et génère des images PNG avec matplotlib

Ce module transforme les matrices numpy en plans architecturaux visuels.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import numpy as np
from typing import Dict
import pickle


class SolutionVisualizer:
    """Génère des visualisations graphiques à partir des solutions"""
    
    # Palette de couleurs pastel pour les appartements
    APARTMENT_COLORS = [
        '#FFB6C1',  # Rose clair
        '#87CEEB',  # Bleu ciel
        '#98FB98',  # Vert pâle
        '#FFD700',  # Or
        '#DDA0DD',  # Prune
        '#F0E68C',  # Kaki
        '#FFE4B5',  # Moccasin
        '#B0E0E6',  # Bleu poudre
        '#FFDAB9',  # Pêche
        '#E6E6FA',  # Lavande
    ]
    # Couleurs fixes par type (nombre de pièces)
    TYPE_COLOR_MAP = {
        '2.5p': '#D1D9AE',
        '3.5p': '#D9E6CF', 
        '4.5p': '#AACA97',
        '5.5p': '#8FC9B8',  # Violet
        '6.5p': '#F1C40F',  # Jaune
    }
    
    CIRCULATION_COLOR = '#D3D3D3'  # Gris clair
    EMPTY_COLOR = '#FFFFFF'        # Blanc
    GRID_COLOR = '#999999'         # Gris foncé pour les lignes
    
    def __init__(self, cell_width: float = 1.0):
        """
        Initialise le visualiseur
        
        Args:
            cell_width: Largeur de base pour l'affichage des cellules (en pouces)
        """
        self.cell_width = cell_width
    
    @staticmethod
    def load_solution(filepath: str) -> Dict:
        """Charge une solution depuis un fichier .pkl"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def visualize(
        self,
        solution: Dict,
        output_path: str,
        show_grid: bool = True,
        show_labels: bool = True,
        show_info: bool = True,
        dpi: int = 150
    ):
        """
        Génère et sauvegarde une visualisation d'une solution
        
        Args:
            solution: Dictionnaire de solution (depuis .pkl)
            output_path: Chemin du fichier PNG de sortie
            show_grid: Afficher la grille
            show_labels: Afficher les labels des appartements
            show_info: Afficher les informations sur le côté
            dpi: Résolution de l'image
        """
        
        # Utiliser la grille fine si disponible
        if solution['metadata'].get('use_fine_grid') and 'fine_grid' in solution:
            grid = solution['fine_grid']
            # La grille fine est déjà 2x plus grande
        else:
            grid = solution['grid']
        apartments = solution['apartments']
        metadata = solution['metadata']
        
        # Calculer la taille de la figure (tenir compte du ratio grid_x/grid_y)
        n_rows, n_cols = grid.shape
        sx = float(metadata.get('grid_x', 1.0))
        sy = float(metadata.get('grid_y', 1.0))
        
        # Si grille fine, ajuster l'échelle
        if metadata.get('use_fine_grid'):
            sx = sx / 2  # Chaque sous-cellule est 2x plus petite
            sy = sy / 2
        
        # Calculer la taille de figure en respectant les proportions réelles
        # Utiliser sx comme référence pour la largeur
        fig_width = n_cols * self.cell_width + (4 if show_info else 0)
        fig_height = n_rows * self.cell_width * (sy / sx)
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Dessiner le plan
        self._draw_plan(ax, grid, apartments, show_grid, show_labels, sx, sy, metadata)
        
        # Ajouter les informations
        if show_info:
            self._draw_info_panel(ax, solution, n_cols, sx, sy)
        
        # Configuration des axes
        ax.set_xlim(-0.5 * sx, n_cols * sx + (3.5 if show_info else 0.5) * sx)
        # Étendre la limite inférieure pour éviter une coupe d'un demi carré
        ax.set_ylim(-0.5 * sy, n_rows * sy + 0.5 * sy)
        # Ne pas forcer aspect='equal' pour permettre les rectangles
        # L'aspect ratio est géré par les dimensions de la figure
        ax.invert_yaxis()  # (0,0) en haut à gauche
        ax.axis('off')  # Masquer les axes
        
        # Title with compactness score and shape variance
        avg_compactness = metadata.get('avg_compactness', 0)
        shape_variance = metadata.get('shape_variance', 0)
        title = f"Solution - Compactness: {avg_compactness:.2f} | Shape Variance: {shape_variance:.4f}"
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        
        # Sauvegarder
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"   💾 Image saved: {output_path}")
    
    def _draw_plan(
        self,
        ax,
        grid: np.ndarray,
        apartments: Dict,
        show_grid: bool,
        show_labels: bool,
        sx: float,
        sy: float,
        metadata: Dict
    ):
        """Dessine le plan avec les appartements"""
        
        n_rows, n_cols = grid.shape
        
        # Créer un mapping Type → couleur (fixe), puis ID → couleur
        type_to_color = {}
        fallback_colors = iter(self.APARTMENT_COLORS)
        for apt_id in sorted(apartments.keys()):
            apt_type = apartments[apt_id]['type']
            if apt_type in self.TYPE_COLOR_MAP:
                type_to_color.setdefault(apt_type, self.TYPE_COLOR_MAP[apt_type])
            else:
                if apt_type not in type_to_color:
                    try:
                        type_to_color[apt_type] = next(fallback_colors)
                    except StopIteration:
                        type_to_color[apt_type] = '#777777'
        apt_colors = {apt_id: type_to_color[apartments[apt_id]['type']] for apt_id in apartments}
        
        # Dessiner chaque cellule
        for y in range(n_rows):
            for x in range(n_cols):
                cell_value = grid[y, x]
                
                # Déterminer la couleur
                if cell_value == -1:
                    color = self.CIRCULATION_COLOR
                elif cell_value == 0:
                    color = self.EMPTY_COLOR
                else:
                    color = apt_colors.get(cell_value, self.EMPTY_COLOR)
                
                # Dessiner le rectangle de la cellule
                rect = patches.Rectangle(
                    (x * sx, y * sy), sx, sy,
                    linewidth=0,
                    edgecolor='none',
                    facecolor=color,
                    alpha=0.8
                )
                ax.add_patch(rect)
                
                # Dessiner la bordure de la grille
                if show_grid:
                    # En grille fine, dessiner des lignes fines pour les sous-cellules
                    if metadata.get('use_fine_grid'):
                        border = patches.Rectangle(
                            (x * sx, y * sy), sx, sy,
                            linewidth=0.3,
                            edgecolor=self.GRID_COLOR,
                            facecolor='none',
                            alpha=0.3
                        )
                        ax.add_patch(border)
                    else:
                        border = patches.Rectangle(
                            (x * sx, y * sy), sx, sy,
                            linewidth=1.0,
                            edgecolor=self.GRID_COLOR,
                            facecolor='none',
                            alpha=0.5
                        )
                        ax.add_patch(border)
        
        # Ajouter les labels des appartements
        if show_labels:
            self._add_apartment_labels(ax, grid, apartments, sx, sy)
        
        # Marquer la circulation
        self._add_circulation_markers(ax, grid, sx, sy)
        
        # Si grille fine, dessiner les lignes de la grille principale par-dessus
        if metadata.get('use_fine_grid') and show_grid:
            self._draw_main_grid_lines(ax, metadata['n_cells_x'], metadata['n_cells_y'], sx, sy)
        
        # Dessiner les contours épais des appartements (pour bien les distinguer)
        self._draw_apartment_outlines(ax, grid, sx, sy)

        # Si pas de grille fine native, dessiner les demi-cellules manuellement
        if not metadata.get('use_fine_grid'):
            # Demi-cellule: dessiner un demi-rectangle attaché à la façade
            self._add_half_cell_rectangles(ax, apartments, apt_colors, n_cols, n_rows, sx, sy)
            
            # Fine grid (lignes à mi-cellule) au-dessus des recouvrements
            self._draw_fine_grid(ax, n_rows, n_cols, sx, sy)
    
    def _add_apartment_labels(self, ax, grid: np.ndarray, apartments: Dict, sx: float, sy: float):
        """Ajoute les labels au centre de chaque appartement"""
        
        for apt_id, apt_info in apartments.items():
            # Utiliser fine_cells si disponibles (grille fine)
            if 'fine_cells' in apt_info:
                cells = apt_info['fine_cells']
            else:
                cells = apt_info['cells']
            
            xs = [x for x, y in cells]
            ys = [y for x, y in cells]
            center_x = (sum(xs) / len(xs) + 0.5) * sx
            center_y = (sum(ys) / len(ys) + 0.5) * sy
            
            # Label principal
            label = f"{apt_info['type']}"
            ax.text(
                center_x, center_y - 0.15 * sy, label,
                ha='center', va='center',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='none')
            )
            
            # Sous-label avec la taille
            sublabel = f"{apt_info['size']}"
            if apt_info.get('uses_half_cell') and (abs(float(apt_info['size']) - int(float(apt_info['size'])) - 0.5) < 1e-9):
                sublabel += " (½)"
            ax.text(
                center_x, center_y + 0.15 * sy, sublabel,
                ha='center', va='center',
                fontsize=9, color='#555555'
            )
    
    def _add_circulation_markers(self, ax, grid: np.ndarray, sx: float, sy: float):
        """Ajoute des marqueurs pour la circulation"""
        
        n_rows, n_cols = grid.shape
        
        for y in range(n_rows):
            for x in range(n_cols):
                if grid[y, x] == -1:
                    # Ajouter un petit symbole au centre
                    ax.text(
                        x * sx + 0.5 * sx, y * sy + 0.5 * sy, '⬚',
                        ha='center', va='center',
                        fontsize=16, color='#666666', alpha=0.7
                    )

    def _draw_main_grid_lines(self, ax, n_main_cols: int, n_main_rows: int, sx: float, sy: float):
        """Dessine les lignes épaisses de la grille principale (cellules complètes)."""
        # En grille fine, sx et sy sont déjà divisés par 2
        # Donc on multiplie par 2 pour obtenir l'espacement des cellules principales
        main_sx = sx * 2
        main_sy = sy * 2
        
        # Lignes verticales
        for i in range(n_main_cols + 1):
            x = i * main_sx
            ax.plot([x, x], [0, n_main_rows * main_sy], color=self.GRID_COLOR, linewidth=1.5, alpha=0.7, zorder=10)
        
        # Lignes horizontales
        for j in range(n_main_rows + 1):
            y = j * main_sy
            ax.plot([0, n_main_cols * main_sx], [y, y], color=self.GRID_COLOR, linewidth=1.5, alpha=0.7, zorder=10)
    
    def _draw_apartment_outlines(self, ax, grid: np.ndarray, sx: float, sy: float):
        """Dessine un contour épais autour de chaque appartement (lignes noires)."""
        n_rows, n_cols = grid.shape
        edge_color = '#222222'
        lw = 2.0
        z = 20
        for y in range(n_rows):
            for x in range(n_cols):
                cur = grid[y, x]
                if cur <= 0:
                    continue
                # top
                if y == 0 or grid[y-1, x] != cur:
                    x0, y0 = x * sx, y * sy
                    x1, y1 = (x + 1) * sx, y * sy
                    ax.plot([x0, x1], [y0, y0], color=edge_color, linewidth=lw, zorder=z)
                # bottom
                if y == n_rows - 1 or grid[y+1, x] != cur:
                    x0, y0 = x * sx, (y + 1) * sy
                    x1, y1 = (x + 1) * sx, (y + 1) * sy
                    ax.plot([x0, x1], [y0, y0], color=edge_color, linewidth=lw, zorder=z)
                # left
                if x == 0 or grid[y, x-1] != cur:
                    x0, y0 = x * sx, y * sy
                    x1, y1 = x * sx, (y + 1) * sy
                    ax.plot([x0, x0], [y0, y1], color=edge_color, linewidth=lw, zorder=z)
                # right
                if x == n_cols - 1 or grid[y, x+1] != cur:
                    x0, y0 = (x + 1) * sx, y * sy
                    x1, y1 = (x + 1) * sx, (y + 1) * sy
                    ax.plot([x0, x0], [y0, y1], color=edge_color, linewidth=lw, zorder=z)

    def _draw_fine_grid(self, ax, n_rows: int, n_cols: int, sx: float, sy: float):
        """Dessine des lignes de grille supplémentaires à mi-cellule."""
        # Lignes verticales à x = i + 0.5
        for i in range(n_cols - 1):
            x = (i + 0.5) * sx
            ax.plot([x, x], [0, n_rows * sy], color='#CCCCCC', linewidth=0.6, alpha=0.4)
        # Lignes horizontales à y = j + 0.5
        for j in range(n_rows - 1):
            y = (j + 0.5) * sy
            ax.plot([0, n_cols * sx], [y, y], color='#CCCCCC', linewidth=0.6, alpha=0.4)

    def _add_half_cell_rectangles(self, ax, apartments: Dict, apt_colors: Dict[int, str], n_cols: int, n_rows: int, sx: float, sy: float):
        """Dessine une demi-cellule colorée accolée à la façade pour les tailles .5."""
        for apt_id, apt in apartments.items():
            size = float(apt.get('size', 0))
            if not (apt.get('uses_half_cell') and abs(size - int(size) - 0.5) < 1e-9):
                continue
            cells = apt.get('cells', [])
            if not cells:
                continue
            # Choisir un côté cohérent : utiliser half_side si fourni par le solver
            side = apt.get('half_side')
            # Si absent, estimer par la frontière la plus longue
            if side is None:
                counts = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
                cell_set = set(cells)
                for (x, y) in cells:
                    if (x, y - 1) not in cell_set:
                        counts['top'] += 1
                    if (x, y + 1) not in cell_set:
                        counts['bottom'] += 1
                    if (x - 1, y) not in cell_set:
                        counts['left'] += 1
                    if (x + 1, y) not in cell_set:
                        counts['right'] += 1
                side = max(counts, key=lambda k: counts[k])

            # Choisir une cellule en bord correspondant au côté
            chosen = None
            for (x, y) in cells:
                if side == 'top' and (y == 0 or (x, y - 1) not in set(cells)):
                    chosen = (x, y)
                    break
                if side == 'bottom' and (y == n_rows - 1 or (x, y + 1) not in set(cells)):
                    chosen = (x, y)
                    break
                if side == 'left' and (x == 0 or (x - 1, y) not in set(cells)):
                    chosen = (x, y)
                    break
                if side == 'right' and (x == n_cols - 1 or (x + 1, y) not in set(cells)):
                    chosen = (x, y)
                    break
            if chosen is None:
                # Sinon, prendre la première et dessiner en haut
                chosen, side = cells[0], 'top'
            x, y = chosen
            color = apt_colors.get(apt_id, '#000000')
            # D'abord masquer la demi-case non occupée en blanc
            # Attention: y est inversé (ax.invert_yaxis). Pour le côté 'top' visuel,
            # la moitié coloriée est en haut (y+0.5..y+1.0). La moitié blanche est en bas (y..y+0.5).
            if side == 'top':
                white_rect = patches.Rectangle((x * sx, y * sy), 1.0 * sx, 0.5 * sy, linewidth=0, edgecolor='none', facecolor=self.EMPTY_COLOR)
            elif side == 'bottom':
                white_rect = patches.Rectangle((x * sx, (y + 0.5) * sy), 1.0 * sx, 0.5 * sy, linewidth=0, edgecolor='none', facecolor=self.EMPTY_COLOR)
            elif side == 'left':
                white_rect = patches.Rectangle(((x + 0.5) * sx, y * sy), 0.5 * sx, 1.0 * sy, linewidth=0, edgecolor='none', facecolor=self.EMPTY_COLOR)
            else:  # right
                white_rect = patches.Rectangle((x * sx, y * sy), 0.5 * sx, 1.0 * sy, linewidth=0, edgecolor='none', facecolor=self.EMPTY_COLOR)
            ax.add_patch(white_rect)

            # Puis dessiner le demi-rectangle occupé selon la façade
            if side == 'top':
                rect = patches.Rectangle((x * sx, (y + 0.5) * sy), 1.0 * sx, 0.5 * sy, linewidth=0, edgecolor='none', facecolor=color, alpha=0.8)
            elif side == 'bottom':
                rect = patches.Rectangle((x * sx, y * sy), 1.0 * sx, 0.5 * sy, linewidth=0, edgecolor='none', facecolor=color, alpha=0.8)
            elif side == 'left':
                rect = patches.Rectangle((x * sx, y * sy), 0.5 * sx, 1.0 * sy, linewidth=0, edgecolor='none', facecolor=color, alpha=0.8)
            else:  # right
                rect = patches.Rectangle(((x + 0.5) * sx, y * sy), 0.5 * sx, 1.0 * sy, linewidth=0, edgecolor='none', facecolor=color, alpha=0.8)
            ax.add_patch(rect)
    
    def _draw_info_panel(self, ax, solution: Dict, grid_width: int, sx: float, sy: float):
        """Draws the information panel on the side, accounting for scale."""
        
        metadata = solution['metadata']
        apartments = solution['apartments']
        
        # Panel position (right of grid)
        panel_x = grid_width * sx + 0.5 * sx
        panel_y = 0
        
        # Title
        info_text = "📋 INFORMATION\n\n"
        
        # Grid
        info_text += f"Grid: {metadata['n_cells_x']} × {metadata['n_cells_y']} cells\n"
        info_text += f"Cell: {metadata['grid_x']}m × {metadata['grid_y']}m\n"
        cell_area = metadata['grid_x'] * metadata['grid_y']
        info_text += f"Cell area: {cell_area:.2f} m²\n\n"
        
        # Compactness score and shape variance
        avg_compactness = metadata.get('avg_compactness', 0)
        shape_variance = metadata.get('shape_variance', 0)
        info_text += f"Avg compactness: {avg_compactness:.2f}\n"
        info_text += f"Shape variance: {shape_variance:.4f}\n\n"
        
        # Apartments
        info_text += "Apartments:\n"
        for apt_id in sorted(apartments.keys()):
            apt = apartments[apt_id]
            area = apt['size'] * cell_area
            info_text += f"• {apt['type']}:\n"
            suffix = " +½" if apt.get('uses_half_cell') and (abs(float(apt['size']) - int(float(apt['size'])) - 0.5) < 1e-9) else ""
            info_text += f"  {apt['size']}{suffix} cells = {area:.1f} m²\n"
            info_text += f"  {apt['facade_count']} cells on facade\n"
        
        # Ajouter le texte
        ax.text(
            panel_x, panel_y + 1.5 * sy,
            info_text,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(
                boxstyle='round,pad=0.8',
                facecolor='#F5F5F5',
                alpha=0.95,
                edgecolor='#CCCCCC',
                linewidth=1
            ),
            family='monospace'
        )
    
    def visualize_multiple(
        self,
        solution_files: list,
        output_dir: str,
        **kwargs
    ):
        """
        Visualise plusieurs solutions
        
        Args:
            solution_files: Liste de chemins vers des fichiers .pkl
            output_dir: Dossier de sortie pour les images
            **kwargs: Arguments passés à visualize()
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎨 Génération de {len(solution_files)} visualisation(s)...")
        
        for i, filepath in enumerate(solution_files, 1):
            # Charger la solution
            solution = self.load_solution(filepath)
            
            # Générer le nom de fichier de sortie
            basename = os.path.basename(filepath).replace('.pkl', '.png')
            output_path = os.path.join(output_dir, basename)
            
            # Visualiser
            self.visualize(solution, output_path, **kwargs)
        
        print(f"✅ {len(solution_files)} image(s) générée(s) dans {output_dir}")


def create_comparison_view(solution_files: list, output_path: str, max_cols: int = 3):
    """
    Creates a comparison view of multiple solutions on a single image
    
    Args:
        solution_files: List of paths to .pkl files
        output_path: Output PNG file path
        max_cols: Maximum number of columns in the grid
    """
    n_solutions = len(solution_files)
    
    # Calculate optimal grid layout for A3/A4 portrait ratio (~1.4)
    # Try to get close to portrait format while fitting all solutions
    n_cols = max_cols
    n_rows = (n_solutions + n_cols - 1) // n_cols
    
    # Adjust for better aspect ratio (closer to printable format)
    while n_cols > 2 and (n_cols / n_rows) > 1.5:
        n_cols -= 1
        n_rows = (n_solutions + n_cols - 1) // n_cols
    
    # Calculate figure size for good readability
    # Each cell should be large enough to read labels
    cell_size = 3.5  # inches per solution
    fig_width = n_cols * cell_size
    fig_height = n_rows * cell_size
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
    
    if n_solutions == 1:
        axes = np.array([axes])
    axes = axes.flatten() if n_rows > 1 or n_cols > 1 else np.array([axes])
    
    visualizer = SolutionVisualizer(cell_width=0.4)
    
    for i, filepath in enumerate(solution_files):
        solution = SolutionVisualizer.load_solution(filepath)
        ax = axes[i]
        
        # Draw solution respecting grid_x, grid_y
        metadata = solution['metadata']
        
        # Use fine grid if available
        if metadata.get('use_fine_grid') and 'fine_grid' in solution:
            grid = solution['fine_grid']
        else:
            grid = solution['grid']
            
        sx = float(metadata.get('grid_x', 1.0))
        sy = float(metadata.get('grid_y', 1.0))
        
        # Adjust scale for fine grid
        if metadata.get('use_fine_grid'):
            sx = sx / 2
            sy = sy / 2
            
        visualizer._draw_plan(
            ax,
            grid,
            solution['apartments'],
            show_grid=True,
            show_labels=True,
            sx=sx,
            sy=sy,
            metadata=metadata
        )
        
        # Configuration
        n_rows_grid, n_cols_grid = grid.shape
        ax.set_xlim(-0.5 * sx, n_cols_grid * sx + 0.5 * sx)
        ax.set_ylim(-0.5 * sy, n_rows_grid * sy + 0.5 * sy)
        # Ne pas forcer aspect='equal' pour respecter les rectangles
        ax.invert_yaxis()
        ax.axis('off')
        avg_compactness = solution['metadata'].get('avg_compactness', 0)
        shape_variance = solution['metadata'].get('shape_variance', 0)
        ax.set_title(f"Sol {i+1} (C:{avg_compactness:.1f} V:{shape_variance:.3f})", 
                    fontsize=9, pad=8, fontweight='normal')
    
    # Hide unused axes
    for i in range(n_solutions, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle("Solutions Comparison", fontsize=13, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"   💾 Comparison view saved: {output_path}")

