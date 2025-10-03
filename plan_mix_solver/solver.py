"""
═══════════════════════════════════════════════════════════════════════════════
SOLVER DE PLACEMENT D'APPARTEMENTS - GÉNÉRATION DE DONNÉES
═══════════════════════════════════════════════════════════════════════════════

ÉTAPE 1 : Génère les solutions sous forme de matrices numpy
Les matrices seront ensuite visualisées avec matplotlib (étape 2)

Structure de données générée :
{
    "grid": np.array([[0, 1, 1, 2], [0, 1, 1, 2], ...]),  # Matrice des IDs
    "apartments": {
        1: {"type": "2.5p", "size": 5.5, "cells": [...], "facade_count": 4},
        2: {"type": "3.5p", "size": 7.5, "cells": [...], "facade_count": 3},
    },
    "circulation_cells": [(1, 0), (1, 1), ...],
    "metadata": {"grid_x": 3.5, "grid_y": 3.0, "score": 2, ...}
}

Où :
- grid[y, x] = 0 → circulation
- grid[y, x] = 1, 2, 3... → ID de l'appartement
"""

import numpy as np
from typing import Dict, List, Tuple, Set, Optional, Union
from collections import deque
import copy


class ApartmentSolver:
    """Solveur de placement d'appartements sur grille 2D"""
    
    def __init__(
        self,
        grid_x: float,
        grid_y: float,
        n_cells_x: int,
        n_cells_y: int,
        circulation_cells: List[Tuple[int, int]],
        apartments_to_place: Union[Dict[str, float], List[Tuple[str, float]]],
        max_solutions: int = 10,
        min_facade_cells: Optional[Dict[str, int]] = None,
        use_fine_grid: bool = True,
        fine_circulation_cells: Optional[List[Tuple[int, int]]] = None,
        max_enfilade_cells_per_apartment: Optional[int] = None,
        shape_variance_weight: float = 100,
        variance_filter_threshold: float = 1.5,
        max_placement_tries: int = 30
    ):
        """
        Initialise le solveur
        
        Args:
            grid_x, grid_y: Dimensions d'une cellule (en mètres)
            n_cells_x, n_cells_y: Dimensions du bâtiment (en cellules)
            circulation_cells: Liste des cellules de circulation [(x,y), ...] ou sous-cellules si use_fine_grid
            apartments_to_place: {"2.5p": 5.5, "3.5p": 7.5, ...}
            max_solutions: Nombre maximum de solutions à retourner
            min_facade_cells: Dict optionnel {"2.5p": 1, "3.5p": 2, ...} pour surcharger la règle par défaut
            use_fine_grid: Si True, utilise une grille 2x plus fine pour gérer les demi-cellules
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.use_fine_grid = use_fine_grid
        # Circulation: garder la grille principale telle que fournie, et gérer la circulation fine uniquement sur la grille fine
        self.circulation_cells = set(circulation_cells)
        self.fine_circulation_cells = set(fine_circulation_cells) if fine_circulation_cells else None
        
        # Calculer les cellules principales partiellement bloquées par la circulation fine
        self.partially_blocked_cells = set()
        if self.fine_circulation_cells:
            # Pour chaque sous-cellule de circulation fine, vérifier si sa cellule principale
            # n'est pas déjà entièrement en circulation
            for fx, fy in self.fine_circulation_cells:
                main_x, main_y = fx // 2, fy // 2
                if (main_x, main_y) not in self.circulation_cells:
                    # Cette cellule principale a de la circulation fine mais n'est pas
                    # elle-même marquée comme circulation → partiellement bloquée
                    self.partially_blocked_cells.add((main_x, main_y))
        # Normaliser les appartements sous forme de liste pour gérer les doublons
        if isinstance(apartments_to_place, dict):
            self.apartment_list: List[Tuple[str, float]] = [
                (apt_type, size) for apt_type, size in apartments_to_place.items()
            ]
        elif isinstance(apartments_to_place, list):
            self.apartment_list = list(apartments_to_place)
        else:
            raise TypeError("apartments_to_place doit être un dict ou une liste de tuples")
        self.max_solutions = max_solutions
        self.max_enfilade_cells_per_apartment = max_enfilade_cells_per_apartment
        
        # Paramètres de similarité géométrique
        self.shape_variance_weight = shape_variance_weight
        self.variance_filter_threshold = variance_filter_threshold
        self.max_placement_tries = max_placement_tries
        
        # Calculer les contraintes de façade pour chaque type
        self.facade_requirements = {}
        if min_facade_cells:
            # Utiliser les valeurs fournies
            for apt_type in {t for (t, _) in self.apartment_list}:
                self.facade_requirements[apt_type] = min_facade_cells.get(apt_type, 0)
        else:
            # Règle par défaut: nombre_de_pieces - 1.5 (arrondi, min 0)
            for apt_type in {t for (t, _) in self.apartment_list}:
                n_pieces = float(apt_type.replace('p', '').split('_')[0])
                required = int(round(n_pieces - 1.5))
                if required < 0:
                    required = 0
                self.facade_requirements[apt_type] = required
        
        # Stockage des solutions
        self.solutions = []
        self._seen_signatures: Set[bytes] = set()
        
        print(f"🔧 Initialisation du solveur")
        print(f"   Grille : {n_cells_x} × {n_cells_y} cellules ({grid_x}m × {grid_y}m)")
        if use_fine_grid:
            print(f"   Mode grille fine activé (pour gérer les demi-cellules)")
        print(f"   Circulation : {len(self.circulation_cells)} cellules")
        if self.partially_blocked_cells:
            print(f"   Cellules partiellement bloquées : {len(self.partially_blocked_cells)}")
        print(f"   Appartements : {len(self.apartment_list)}")
        for apt_type, size in self.apartment_list:
            facade_req = self.facade_requirements[apt_type]
            print(f"      • {apt_type} : {size} cellules, ≥{facade_req} en façade")
        print(f"   Similarité géométrique :")
        print(f"      • Poids variance : {self.shape_variance_weight}")
        print(f"      • Seuil filtrage : {self.variance_filter_threshold}x")
        print(f"      • Max placements testés : {self.max_placement_tries}")
    
    def solve(self) -> List[Dict]:
        """
        Lance la résolution et retourne les solutions
        
        Returns:
            Liste de solutions (dictionnaires avec grid, apartments, metadata)
        """
        print(f"\n🔍 Recherche de solutions...")
        
        # Créer la grille initiale (0 = libre, -1 = circulation)
        initial_grid = np.zeros((self.n_cells_y, self.n_cells_x), dtype=int)
        for x, y in self.circulation_cells:
            initial_grid[y, x] = -1
        
        # Liste normalisée des appartements à placer (préserve les doublons)
        apt_list = list(self.apartment_list)
        
        # Trier pour placer les plus gros en premier (heuristique classique)
        apt_list_sorted = sorted(enumerate(apt_list), key=lambda t: -t[1][1])
        apt_order = [i for i, _ in apt_list_sorted]
        apt_list_ordered = [apt_list[i] for i in apt_order]
        
        # Backtracking
        self._backtrack(initial_grid, apt_list_ordered, 0, {})
        
        # Trier par score (variance faible = meilleur score)
        self.solutions.sort(key=lambda s: s['metadata']['score'])
        
        # Le filtrage strict est déjà fait pendant la génération
        # Ici on applique juste un léger post-filtrage si nécessaire
        if len(self.solutions) > self.max_solutions:
            # Calculer le seuil de variance acceptable (basé sur les meilleures)
            n_best = max(3, len(self.solutions) // 5)
            best_variances = [s['metadata']['shape_variance'] for s in self.solutions[:n_best]]
            avg_best_variance = sum(best_variances) / len(best_variances)
            variance_threshold = avg_best_variance * self.variance_filter_threshold
            
            # Filtrer les solutions qui dépassent le seuil
            filtered_solutions = [
                s for s in self.solutions 
                if s['metadata']['shape_variance'] <= variance_threshold
            ]
            
            # Garder au moins quelques solutions même si le filtrage est strict
            if len(filtered_solutions) < 3:
                filtered_solutions = self.solutions[:min(3, len(self.solutions))]
        else:
            filtered_solutions = self.solutions
        
        # Limiter au nombre demandé
        best_solutions = filtered_solutions[:self.max_solutions]
        
        print(f"✅ {len(self.solutions)} solution(s) trouvée(s) (similarité appliquée pendant génération)")
        if len(filtered_solutions) < len(self.solutions):
            print(f"🎯 {len(filtered_solutions)} solution(s) après post-filtrage")
        print(f"📊 Retour des {len(best_solutions)} meilleures\n")
        
        return best_solutions
    
    def _backtrack(
        self,
        grid: np.ndarray,
        remaining_apts: List[Tuple[str, float]],
        apt_idx: int,
        placed_apts: Dict[int, Dict]
    ):
        """Backtracking récursif pour placer les appartements"""
        
        # Condition d'arrêt : tous les appartements sont placés
        if apt_idx >= len(remaining_apts):
            self._save_solution(grid, placed_apts)
            return
        
        # Limiter le nombre de solutions candidates explorées
        if len(self.solutions) >= self.max_solutions * 200:
            return
        
        apt_type, size = remaining_apts[apt_idx]
        apt_id = apt_idx + 1  # ID commence à 1 (0 = libre, -1 = circulation)
        
        # Trouver tous les placements possibles pour cet appartement
        placements = self._find_all_placements(grid, size, apt_id)
        
        # Trier les placements par compacité (privilégier les formes compactes)
        placements_with_compactness = []
        for placement in placements:
            compactness = self._calculate_compactness(placement)
            placements_with_compactness.append((compactness, placement))
        placements_with_compactness.sort(key=lambda x: -x[0])  # Tri décroissant par compacité
        placements = [p for _, p in placements_with_compactness]
        
        # Si des appartements sont déjà placés, filtrer strictement par similarité
        if placed_apts:
            placements = self._filter_similar_shapes_strict(placements, placed_apts)
            # Si aucun placement similaire trouvé, abandonner cette branche
            if not placements:
                return
        
        # Limiter le nombre de placements testés (favoriser qualité sur quantité)
        # Pour les demi-cellules, augmenter légèrement le nombre d'essais
        max_tries = int(self.max_placement_tries * 1.5) if abs(size - int(size) - 0.5) < 1e-9 else self.max_placement_tries
        for placement_cells in placements[:max_tries]:  # Limiter le nombre de tentatives
            # Créer une nouvelle grille avec l'appartement placé
            new_grid = grid.copy()
            
            # Placer l'appartement
            for x, y in placement_cells:
                new_grid[y, x] = apt_id
            
            # Vérifier les contraintes
            if self._check_constraints(new_grid, apt_id, placement_cells, apt_type):
                # Enregistrer les infos de l'appartement
                facade_count = self._count_facade_cells(placement_cells)
                new_placed_apts = placed_apts.copy()
                half_side = None
                if abs(size - int(size) - 0.5) < 1e-9:
                    half_side = self._select_half_side_any_boundary(placement_cells)
                    # Si aucune face claire (très improbable), on rejette ce placement
                    if half_side is None:
                        continue
                
                # Calculer les descripteurs de forme pour ce placement
                shape_desc = self._calculate_shape_descriptors(placement_cells)
                
                new_placed_apts[apt_id] = {
                    'type': apt_type,
                    'size': size,
                    'cells': placement_cells,
                    'facade_count': facade_count,
                    'uses_half_cell': abs(size - int(size) - 0.5) < 1e-9,
                    'half_side': half_side,
                    'shape_descriptors': shape_desc
                }
                
                # Continuer avec l'appartement suivant
                self._backtrack(new_grid, remaining_apts, apt_idx + 1, new_placed_apts)
    
    def _find_all_placements(
        self,
        grid: np.ndarray,
        size: float,
        apt_id: int
    ) -> List[List[Tuple[int, int]]]:
        """
        Trouve tous les placements possibles pour un appartement de taille donnée
        en utilisant flood-fill depuis différents points de départ
        """
        placements = []
        # Pour le placement principal, on place uniquement les cellules entières
        # Les demi-cellules seront ajoutées après dans une phase séparée
        is_half_cell = abs(size - int(size) - 0.5) < 1e-9
        target_cells = int(np.floor(size))  # 7.5 → 7, 8.5 → 8
        
        # Prioriser les départs proches de la circulation et/ou de la façade
        candidate_starts = []
        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                if grid[y, x] != 0:
                    continue
                # Ignorer les cellules partiellement bloquées comme points de départ
                if (x, y) in self.partially_blocked_cells:
                    continue
                near_circ = any((x+dx, y+dy) in self.circulation_cells for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)])
                on_facade = (x == 0 or x == self.n_cells_x - 1 or y == 0 or y == self.n_cells_y - 1)
                candidate_starts.append(((x, y), near_circ, on_facade))
        # Trier: d'abord proches circulation, puis façade, puis le reste
        candidate_starts.sort(key=lambda t: (not t[1], not t[2]))

        for (start, _, _) in candidate_starts:
            placement = self._flood_fill(grid, start, target_cells)
            if placement and len(placement) == target_cells:
                placement_set = frozenset(placement)
                if not any(frozenset(p) == placement_set for p in placements):
                    placements.append(placement)
        
        return placements
    
    def _flood_fill(
        self,
        grid: np.ndarray,
        start: Tuple[int, int],
        target_size: int
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Utilise flood-fill pour créer un placement connexe
        Retourne une liste de cellules ou None si impossible
        """
        visited = set()
        cells = []
        queue = deque([start])
        
        while queue and len(cells) < target_size:
            x, y = queue.popleft()
            
            if (x, y) in visited:
                continue
            
            # Vérifier que la cellule est dans la grille et libre
            if not (0 <= x < self.n_cells_x and 0 <= y < self.n_cells_y):
                continue
            
            if grid[y, x] != 0:  # Pas libre
                continue
            
            # Vérifier que la cellule n'est pas partiellement bloquée
            if (x, y) in self.partially_blocked_cells:
                continue
            
            visited.add((x, y))
            cells.append((x, y))
            
            # Ajouter les voisins (4-connexité)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    queue.append((nx, ny))
        
        if len(cells) == target_size:
            return cells
        return None
    
    def _check_constraints(
        self,
        grid: np.ndarray,
        apt_id: int,
        cells: List[Tuple[int, int]],
        apt_type: str
    ) -> bool:
        """Vérifie toutes les contraintes pour un appartement"""
        
        # 1. Vérifier la connexité (déjà garantie par flood-fill)
        
        # 2. Vérifier le contact avec la circulation
        if not self._touches_circulation(cells):
            return False
        
        # 3. Vérifier le nombre de cellules en façade
        facade_count = self._count_facade_cells(cells)
        required_facade = self.facade_requirements[apt_type]
        if facade_count < required_facade:
            return False

        # 4. Contrainte demi-cellule : si taille .5, il faut une face extérieure disponible
        # pour accueillir la demi-cellule sur un seul côté de l'appartement
        # (mesurée comme la direction avec longueur de frontière maximale)
        if abs(float(apt_type.replace('p', '').split('_')[0]) - int(float(apt_type.replace('p', '').split('_')[0]))) > 0:
            # La contrainte dépend de la taille réelle, pas du type; on vérifie via len(cells)
            # On utilise la présence d'une demi-cellule via la future taille; ici on ne l'a pas.
            # Cette vérification détaillée est effectuée lors de l'enregistrement de l'appartement.
            pass

        # 5. Contrainte d'enfilade (couloir): limiter les cellules de degré 2 colinéaires
        if self.max_enfilade_cells_per_apartment is not None:
            enfilade_count = self._count_enfilade_cells(cells)
            if enfilade_count > self.max_enfilade_cells_per_apartment:
                return False
        
        return True

    def _select_half_side_any_boundary(self, cells: List[Tuple[int, int]]) -> Optional[str]:
        """Sélectionne un côté ('top','bottom','left','right') pour la demi-cellule
        en se basant sur la plus grande longueur de frontière extérieure de l'appartement
        (tout voisin inexistant dans le set de cellules)."""
        cell_set = set(cells)
        counts = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
        for x, y in cells:
            if (x, y - 1) not in cell_set:
                counts['top'] += 1
            if (x, y + 1) not in cell_set:
                counts['bottom'] += 1
            if (x - 1, y) not in cell_set:
                counts['left'] += 1
            if (x + 1, y) not in cell_set:
                counts['right'] += 1
        best_side = None
        best_val = -1
        for side in ['top', 'bottom', 'left', 'right']:
            if counts[side] > best_val:
                best_val = counts[side]
                best_side = side
        return best_side if best_val > 0 else None
    
    def _touches_circulation(self, cells: List[Tuple[int, int]]) -> bool:
        """Vérifie qu'au moins une cellule touche la circulation"""
        for x, y in cells:
            # Vérifier les 4 voisins
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.circulation_cells:
                    return True
        return False
    
    def _count_facade_cells(self, cells: List[Tuple[int, int]]) -> int:
        """Compte combien de cellules sont sur le périmètre du bâtiment"""
        count = 0
        for x, y in cells:
            if (x == 0 or x == self.n_cells_x - 1 or 
                y == 0 or y == self.n_cells_y - 1):
                count += 1
        return count
    
    def _calculate_compactness(self, cells: List[Tuple[int, int]]) -> float:
        """Calcule le score de compacité d'un appartement.
        
        Compte le nombre de contacts internes (arêtes partagées entre cellules).
        Plus le score est élevé, plus l'appartement est compact.
        
        Args:
            cells: Liste des coordonnées (x, y) des cellules de l'appartement
            
        Returns:
            Nombre de contacts internes (arêtes partagées)
        """
        cell_set = set(cells)
        contacts = 0
        
        for x, y in cells:
            # Vérifier les 4 voisins
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor in cell_set:
                    contacts += 1
        
        # Diviser par 2 car chaque contact est compté deux fois
        return contacts / 2.0

    def _count_enfilade_cells(self, cells: List[Tuple[int, int]]) -> int:
        """Compte les cellules 'en couloir': degré 2 avec voisins colinéaires."""
        cell_set = set(cells)
        enfilade = 0
        for x, y in cells:
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                n = (x + dx, y + dy)
                if n in cell_set:
                    neighbors.append(n)
            if len(neighbors) == 2:
                (x1, y1), (x2, y2) = neighbors
                if x1 == x2 or y1 == y2:
                    enfilade += 1
        return enfilade
    
    def _calculate_shape_descriptors(self, cells: List[Tuple[int, int]]) -> Dict[str, float]:
        """
        Calcule des descripteurs géométriques pour caractériser la forme d'un appartement
        
        Returns:
            Dictionnaire avec:
            - aspect_ratio: ratio largeur/hauteur de la bounding box
            - normalized_perimeter: périmètre normalisé par la surface
            - moment_ratio: ratio des moments d'inertie (élongation)
        """
        if not cells:
            return {'aspect_ratio': 1.0, 'normalized_perimeter': 0.0, 'moment_ratio': 1.0}
        
        xs = [x for x, y in cells]
        ys = [y for x, y in cells]
        
        # Bounding box
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Aspect ratio (toujours >= 1 en prenant max/min)
        aspect_ratio = max(width, height) / max(min(width, height), 1)
        
        # Périmètre (nombre de côtés exposés)
        cell_set = set(cells)
        perimeter = 0
        for x, y in cells:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                if (x + dx, y + dy) not in cell_set:
                    perimeter += 1
        
        # Normaliser par la surface
        area = len(cells)
        normalized_perimeter = perimeter / area if area > 0 else 0
        
        # Moments d'inertie pour mesurer l'élongation
        # Centre de masse
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        
        # Moments d'inertie
        Ixx = sum((y - cy) ** 2 for x, y in cells)
        Iyy = sum((x - cx) ** 2 for x, y in cells)
        
        # Ratio des moments (toujours >= 1)
        moment_ratio = max(Ixx, Iyy) / max(min(Ixx, Iyy), 1e-6)
        
        return {
            'aspect_ratio': aspect_ratio,
            'normalized_perimeter': normalized_perimeter,
            'moment_ratio': moment_ratio
        }
    
    def _calculate_shape_variance(self, shape_descriptors: List[Dict[str, float]]) -> float:
        """
        Calcule la variance combinée des descripteurs de forme
        Plus la variance est faible, plus les appartements se ressemblent
        """
        if len(shape_descriptors) <= 1:
            return 0.0
        
        # Calculer la variance pour chaque descripteur
        variances = []
        
        for key in ['aspect_ratio', 'normalized_perimeter', 'moment_ratio']:
            values = [desc[key] for desc in shape_descriptors]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            variances.append(variance)
        
        # Variance totale = moyenne des variances normalisées
        # Pondération égale pour chaque descripteur
        total_variance = sum(variances) / len(variances)
        
        return total_variance
    
    def _filter_similar_shapes_strict(
        self, 
        placements: List[List[Tuple[int, int]]], 
        placed_apts: Dict[int, Dict]
    ) -> List[List[Tuple[int, int]]]:
        """
        Filtre STRICTEMENT les placements pour ne garder que ceux qui ressemblent aux appartements déjà placés
        Rejette complètement les placements trop différents selon le seuil de tolérance
        
        Args:
            placements: Liste de placements candidats
            placed_apts: Appartements déjà placés
            
        Returns:
            Liste de placements similaires seulement (peut être vide si aucun n'est assez similaire)
        """
        if not placements or not placed_apts:
            return placements
        
        # Calculer les descripteurs moyens des appartements déjà placés
        existing_descriptors = [apt['shape_descriptors'] for apt in placed_apts.values() if 'shape_descriptors' in apt]
        
        # Si aucun descripteur disponible (premier placement), retourner tel quel
        if not existing_descriptors:
            # Calculer les descripteurs pour les appartements déjà placés (sans shape_descriptors)
            existing_descriptors = []
            for apt in placed_apts.values():
                cells = apt.get('cells', [])
                if cells:
                    desc = self._calculate_shape_descriptors(cells)
                    existing_descriptors.append(desc)
        
        if not existing_descriptors:
            return placements
        
        # Calculer les moyennes des descripteurs existants
        avg_descriptors = {}
        for key in ['aspect_ratio', 'normalized_perimeter', 'moment_ratio']:
            values = [desc[key] for desc in existing_descriptors]
            avg_descriptors[key] = sum(values) / len(values)
        
        # Calculer aussi la variance actuelle pour définir le seuil acceptable
        current_variance = self._calculate_shape_variance(existing_descriptors)
        
        # Seuil de distance acceptable : basé sur la tolérance configurée
        # Plus le shape_variance_weight est élevé, plus le seuil est strict
        # Formule ajustée pour être plus progressive
        base_threshold = 1.0  # Seuil de base
        strictness_factor = max(0.1, min(2.0, 100.0 / self.shape_variance_weight))
        distance_threshold = base_threshold * strictness_factor
        
        # Si variance actuelle très faible (formes identiques), maintenir un seuil minimal
        if current_variance < 0.01:
            distance_threshold = max(distance_threshold * 0.7, 0.15)
        
        # Filtrer et scorer les placements
        similar_placements = []
        for placement in placements:
            desc = self._calculate_shape_descriptors(placement)
            
            # Distance euclidienne normalisée entre descripteurs
            distance = 0.0
            for key in ['aspect_ratio', 'normalized_perimeter', 'moment_ratio']:
                diff = (desc[key] - avg_descriptors[key]) ** 2
                distance += diff
            
            distance = distance ** 0.5  # Racine carrée pour distance euclidienne
            
            # Ne garder que si la distance est sous le seuil
            if distance <= distance_threshold:
                similar_placements.append((distance, placement))
        
        # Trier par distance croissante (plus similaires en premier)
        similar_placements.sort(key=lambda x: x[0])
        
        # Retourner seulement les placements (sans les scores)
        return [placement for _, placement in similar_placements]
    
    def _add_half_cells(self, grid: np.ndarray, apartments: Dict[int, Dict]) -> Optional[Tuple[np.ndarray, Dict[int, Dict]]]:
        """Ajoute les demi-cellules sur une grille fine pour les appartements qui en ont besoin"""
        if not self.use_fine_grid:
            return None
            
        # Créer la grille fine (2x plus grande)
        fine_grid = np.zeros((self.n_cells_y * 2, self.n_cells_x * 2), dtype=int)
        
        # Copier la grille normale sur la grille fine
        for y in range(self.n_cells_y):
            for x in range(self.n_cells_x):
                val = grid[y, x]
                # Remplir les 4 sous-cellules
                for dy in [0, 1]:
                    for dx in [0, 1]:
                        fine_grid[y*2 + dy, x*2 + dx] = val
        
        # Marquer la circulation fine si fournie
        if self.fine_circulation_cells:
            for fx, fy in self.fine_circulation_cells:
                fine_grid[fy, fx] = -1

        # Pour chaque appartement avec demi-cellule, ajouter 2 sous-cellules
        updated_apartments = {}
        for apt_id, apt_info in apartments.items():
            size = apt_info['size']
            if abs(size - int(size) - 0.5) < 1e-9:
                # Cet appartement a besoin d'une demi-cellule
                # Trouver où placer les 2 sous-cellules manquantes
                
                # D'abord, obtenir les sous-cellules actuelles
                fine_cells = []
                for x, y in apt_info['cells']:
                    for dy in [0, 1]:
                        for dx in [0, 1]:
                            fine_cells.append((x*2 + dx, y*2 + dy))
                
                # Chercher 2 sous-cellules adjacentes libres
                # Essayer toutes les orientations possibles (horizontal et vertical)
                placed = False
                fine_cells_set = set(fine_cells)
                
                # Liste de toutes les paires de sous-cellules adjacentes libres
                candidate_pairs = []
                
                for fx, fy in fine_cells:
                    # Pour chaque sous-cellule du bord, chercher un voisin libre
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        neighbor = (fx + dx, fy + dy)
                        if neighbor in fine_cells_set:
                            continue  # Pas un bord
                        
                        nx1, ny1 = fx + dx, fy + dy
                        
                        # Vérifier que le premier voisin est libre
                        if not (0 <= nx1 < self.n_cells_x * 2 and 0 <= ny1 < self.n_cells_y * 2):
                            continue
                        if fine_grid[ny1, nx1] != 0:
                            continue
                        
                        # Essayer les 2 orientations pour la paire
                        # Orientation 1: verticale (empilée en Y)
                        for perp_dir in [1, -1]:
                            nx2, ny2 = nx1, ny1 + perp_dir
                            if (0 <= nx2 < self.n_cells_x * 2 and 0 <= ny2 < self.n_cells_y * 2 and
                                fine_grid[ny2, nx2] == 0):
                                candidate_pairs.append([(nx1, ny1), (nx2, ny2)])
                        
                        # Orientation 2: horizontale (côte à côte en X)
                        for perp_dir in [1, -1]:
                            nx2, ny2 = nx1 + perp_dir, ny1
                            if (0 <= nx2 < self.n_cells_x * 2 and 0 <= ny2 < self.n_cells_y * 2 and
                                fine_grid[ny2, nx2] == 0):
                                candidate_pairs.append([(nx1, ny1), (nx2, ny2)])
                
                # Placer la première paire valide trouvée
                if candidate_pairs:
                    (nx1, ny1), (nx2, ny2) = candidate_pairs[0]
                    fine_grid[ny1, nx1] = apt_id
                    fine_grid[ny2, nx2] = apt_id
                    fine_cells.extend([(nx1, ny1), (nx2, ny2)])
                    placed = True
                
                if not placed:
                    # Impossible de placer la demi-cellule
                    return None
                
                # Mettre à jour les infos de l'appartement
                updated_apartments[apt_id] = apt_info.copy()
                updated_apartments[apt_id]['fine_cells'] = fine_cells
                updated_apartments[apt_id]['uses_half_cell'] = True
            else:
                # Pas de demi-cellule, copier tel quel
                fine_cells = []
                for x, y in apt_info['cells']:
                    for dy in [0, 1]:
                        for dx in [0, 1]:
                            fine_cells.append((x*2 + dx, y*2 + dy))
                updated_apartments[apt_id] = apt_info.copy()
                updated_apartments[apt_id]['fine_cells'] = fine_cells
                updated_apartments[apt_id]['uses_half_cell'] = False
        
        return fine_grid, updated_apartments
    
    def _save_solution(self, grid: np.ndarray, apartments: Dict[int, Dict]):
        """Enregistre une solution valide"""
        
        # Si grille fine activée, essayer d'ajouter les demi-cellules
        if self.use_fine_grid:
            result = self._add_half_cells(grid, apartments)
            if result is None:
                # Impossible de placer les demi-cellules, abandonner cette solution
                return
            fine_grid, updated_apartments = result
        else:
            fine_grid = None
            updated_apartments = apartments
        
        # Calculer les descripteurs de forme pour chaque appartement
        compactness_scores = []
        shape_descriptors = []  # Liste de dictionnaires avec les descripteurs
        
        for apt_id, apt_info in updated_apartments.items():
            # Utiliser fine_cells si disponible, sinon cells
            cells = apt_info.get('fine_cells', apt_info['cells'])
            
            # Compacité
            compactness = self._calculate_compactness(cells)
            compactness_scores.append(compactness)
            updated_apartments[apt_id]['compactness'] = compactness
            
            # Descripteurs géométriques
            descriptors = self._calculate_shape_descriptors(cells)
            shape_descriptors.append(descriptors)
            updated_apartments[apt_id]['shape_descriptors'] = descriptors
        
        # Calculer la variance des descripteurs de forme
        shape_variance = self._calculate_shape_variance(shape_descriptors)
        
        # Score global combinant compacité et similarité de forme
        # Plus la compacité est élevée = mieux
        # Plus la variance de forme est faible = mieux
        avg_compactness = sum(compactness_scores) / len(compactness_scores) if compactness_scores else 0
        
        # Score final = -compacité_moyenne + pénalité_variance
        # (négatif pour que tri croissant donne les meilleurs)
        # Pondération: la variance compte beaucoup plus pour privilégier la similarité
        score = -avg_compactness + shape_variance * self.shape_variance_weight
        
        # Stocker la solution
        if self.use_fine_grid and fine_grid is not None:
            solution = {
                'grid': grid.copy(),  # Grille normale
                'fine_grid': fine_grid,  # Grille fine avec demi-cellules
                'apartments': updated_apartments,
                'circulation_cells': list(self.circulation_cells),
                'metadata': {
                    'grid_x': self.grid_x,
                    'grid_y': self.grid_y,
                    'n_cells_x': self.n_cells_x,
                    'n_cells_y': self.n_cells_y,
                    'score': score,
                    'avg_compactness': avg_compactness,
                    'shape_variance': shape_variance,
                    'use_fine_grid': True
                }
            }
        else:
            solution = {
                'grid': grid.copy(),
                'apartments': copy.deepcopy(apartments),
                'circulation_cells': list(self.circulation_cells),
                'metadata': {
                    'grid_x': self.grid_x,
                    'grid_y': self.grid_y,
                    'n_cells_x': self.n_cells_x,
                    'n_cells_y': self.n_cells_y,
                    'score': score,
                    'avg_compactness': avg_compactness,
                    'shape_variance': shape_variance,
                    'use_fine_grid': False
                }
            }
        
        # Déduplication graphique par types: ignorer l'identité des appartements
        # Construire une grille de signature où chaque cellule d'appartement
        # est remplacée par un code déterministe dépendant uniquement du type (ex: '4.5p'),
        # la circulation (-1) et le vide (0) restant inchangés.
        if solution['metadata'].get('use_fine_grid') and 'fine_grid' in solution:
            grid_for_sig = solution['fine_grid']
        else:
            grid_for_sig = solution['grid']

        # Codes de type déterministes (ordre alphabétique des types)
        unique_types = sorted({apt_info['type'] for apt_info in solution['apartments'].values()})
        type_to_code = {apt_type: idx + 1 for idx, apt_type in enumerate(unique_types)}  # 1..N

        # Construire la grille de signature entière
        sig_grid = np.zeros_like(grid_for_sig, dtype=np.int16)
        # Remplissage cellule par cellule (petites tailles de grille → coût négligeable)
        for y in range(grid_for_sig.shape[0]):
            for x in range(grid_for_sig.shape[1]):
                v = grid_for_sig[y, x]
                if v == -1:
                    sig_grid[y, x] = -1
                elif v == 0:
                    sig_grid[y, x] = 0
                else:
                    apt_type = solution['apartments'][int(v)]['type']
                    sig_grid[y, x] = type_to_code[apt_type]

        sig = sig_grid.tobytes()
        if sig in self._seen_signatures:
            return
        self._seen_signatures.add(sig)
        self.solutions.append(solution)


def print_solution_summary(solution: Dict, index: int = 1):
    """Affiche un résumé d'une solution"""
    score = solution['metadata']['score']
    avg_compactness = solution['metadata'].get('avg_compactness', 0)
    shape_variance = solution['metadata'].get('shape_variance', 0)
    print(f"{'🏆' if index == 1 else '📌'} Solution {index}")
    print(f"   Compacité moy: {avg_compactness:.2f} | Variance forme: {shape_variance:.4f}")
    print(f"   Grille : {solution['metadata']['n_cells_x']} × {solution['metadata']['n_cells_y']}")
    
    for apt_id, apt_info in sorted(solution['apartments'].items()):
        compactness = apt_info.get('compactness', 0)
        # Si grille fine, afficher le nombre de sous-cellules
        if 'fine_cells' in apt_info:
            print(f"   • Apt {apt_id} ({apt_info['type']}) : {apt_info['size']} cellules, "
                  f"{apt_info['facade_count']} façade, {len(apt_info['fine_cells'])} sous-cell., compact: {compactness:.1f}")
        else:
            print(f"   • Apt {apt_id} ({apt_info['type']}) : {apt_info['size']} cellules, "
                  f"{apt_info['facade_count']} façade, {len(apt_info['cells'])} utilisées, compact: {compactness:.1f}")
    
    print(f"   Matrice :")
    grid = solution['grid']
    for y in range(grid.shape[0]):
        row = "      "
        for x in range(grid.shape[1]):
            val = grid[y, x]
            if val == -1:
                row += "⬜ "  # Circulation
            elif val == 0:
                row += "   "  # Vide
            else:
                row += f"{val:2d} "  # Appartement
        print(row)
    print()

