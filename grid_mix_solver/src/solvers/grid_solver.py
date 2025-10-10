"""
Solveur pour la recherche de dimensions de grille optimales
"""
from typing import List, Tuple, Optional, Dict
from itertools import product
import math

from .base import BaseSolver
from ..core.types import Solution, GridConfig
from ..core.grid import quantize, units_per_type
from ..core.combinations import all_sum_combinations
from ..core.percentages import analyze_combination_percentages, analyze_combinations_percentages, percentage_match_score, percentages_within_tolerance


class GridSolver(BaseSolver):
    """Solveur pour trouver les dimensions de grille optimales"""
    
    def solve(self) -> List[Solution]:
        """Résout en cherchant les dimensions de grille optimales"""
        results = []
        
        # Explorer différents nombres d'éléments de grille
        for target_elem in range(self.config.target_elements_range[0], self.config.target_elements_range[1] + 1):
            # Explorer en fixant y et variant x
            steps_y = int((self.config.search_range_y.max_val - self.config.search_range_y.min_val) / self.config.search_range_y.step) + 1 if not self.config.search_range_y.is_fixed else 1
            
            for i in range(steps_y):
                y_val = self.config.search_range_y.min_val + i * self.config.search_range_y.step
                results_y = self._find_grid_dimensions(
                    float(target_elem),
                    fixed_dimension=('y', y_val)
                )
                results.extend(results_y)
        
        # Trier par score (meilleur d'abord)
        results.sort(key=lambda x: x.score)
        return results
    
    def _find_grid_dimensions(
        self,
        target_elements: float,
        fixed_dimension: Optional[Tuple[str, float]] = None
    ) -> List[Solution]:
        """Trouve les dimensions de grille optimales pour un target_elements donné"""
        results = []
        
        if fixed_dimension:
            dim_name, dim_value = fixed_dimension
            if dim_name == 'x':
                for y in self._get_search_values(self.config.search_range_y):
                    results.extend(self._evaluate_grid(dim_value, y, target_elements))
            else:
                for x in self._get_search_values(self.config.search_range_x):
                    results.extend(self._evaluate_grid(x, dim_value, target_elements))
        else:
            for x in self._get_search_values(self.config.search_range_x):
                for y in self._get_search_values(self.config.search_range_y):
                    results.extend(self._evaluate_grid(x, y, target_elements))
        
        results.sort(key=lambda x: x.score)
        return results
    
    def _get_search_values(self, search_range) -> List[float]:
        """Génère les valeurs de recherche pour une plage donnée"""
        if search_range.is_fixed:
            return [search_range.min_val]
        
        steps = int((search_range.max_val - search_range.min_val) / search_range.step) + 1
        return [search_range.min_val + i * search_range.step for i in range(steps)]
    
    def _evaluate_grid(
        self,
        grid_x: float,
        grid_y: float,
        target_elements: float
    ) -> List[Solution]:
        """Évalue une grille donnée et retourne les solutions valides"""
        try:
            results = []
            # Mode sans recherche de combinaisons: produire une solution pour chaque (x, y, target)
            if not self.config.search_combinations:
                # Construire une solution minimale sans combinaisons
                # Pour rester compatible avec les analyses ultérieures, on met les pourcentages cibles
                percentages = dict(self.config.target_percentages)
                score = 0.0
                return [self._create_solution(int(target_elements), grid_x, grid_y, [], percentages, score)]
            
            if not self.config.round_variations:
                # Mode simple : une seule méthode d'arrondi
                per_type = units_per_type(
                    GridConfig(grid_x, grid_y), 
                    self.config.apt_areas, 
                    quantum=self.config.quantum, 
                    method=self.config.method
                )
                unique_values = sorted(set(per_type.values()))
                
                val_to_types = self._create_val_to_types_mapping(per_type)
                
                combos = all_sum_combinations(unique_values, target_elements, quantum=self.config.quantum)
                
                if not combos:
                    return []

                # Sélectionner les N meilleures combinaisons
                selected_combos = self._select_best_combinations(combos, val_to_types)
                if not selected_combos:
                    return []
                
                # Calculer les pourcentages agrégés sur les combinaisons sélectionnées
                percentages = analyze_combinations_percentages(selected_combos, val_to_types, self.config.apt_areas)
                if percentages is None:
                    return []
                
                if not percentages_within_tolerance(percentages, self.config.target_percentages, self.config.percentage_tolerance):
                    return []
                
                score = percentage_match_score(percentages, self.config.target_percentages)
                return [self._create_solution(int(target_elements), grid_x, grid_y, selected_combos, percentages, score)]
            
            # Mode avec variations d'arrondi
            cell_area = grid_x * grid_y
            if cell_area <= 0:
                return []
            
            types_list = []
            candidates_per_type = []
            
            for apt, area in self.config.apt_areas.items():
                if area <= 0:
                    return []
                raw_units = area / cell_area
                lower = quantize(raw_units, quantum=self.config.quantum, method="floor")
                upper = quantize(raw_units, quantum=self.config.quantum, method="ceil")
                if lower == upper:
                    # exact: tester valeur exacte et + quantum
                    candidates = [float(lower), float(lower + self.config.quantum)]
                else:
                    candidates = sorted({float(lower), float(upper)})
                types_list.append(apt)
                candidates_per_type.append(candidates)
            
            # Cache local des combinaisons par set d'unités (clé entière)
            scale = round(1.0 / self.config.quantum)
            combos_by_values_key = {}

            for choice in product(*candidates_per_type):
                scenario_per_type = {apt: units for apt, units in zip(types_list, choice)}
                unique_values = sorted(set(scenario_per_type.values()))
                
                val_to_types = self._create_val_to_types_mapping(scenario_per_type)
                # Ambiguïté: si une valeur d'unités correspond à plusieurs types, inutile de poursuivre
                if any(len(t) != 1 for t in val_to_types.values()):
                    continue
                
                key_int = tuple(sorted(int(round(v * scale)) for v in unique_values))
                if key_int in combos_by_values_key:
                    combos = combos_by_values_key[key_int]
                else:
                    combos = all_sum_combinations(unique_values, target_elements, quantum=self.config.quantum)
                    combos_by_values_key[key_int] = combos
                if not combos:
                    continue
                
                # Sélectionner les N meilleures combinaisons
                selected_combos = self._select_best_combinations(combos, val_to_types)
                if not selected_combos:
                    continue
                
                # Calculer les pourcentages agrégés sur les combinaisons sélectionnées
                percentages = analyze_combinations_percentages(selected_combos, val_to_types, self.config.apt_areas)
                if percentages is None:
                    continue
                
                if not percentages_within_tolerance(percentages, self.config.target_percentages, self.config.percentage_tolerance):
                    continue
                
                score = percentage_match_score(percentages, self.config.target_percentages)
                results.append(self._create_solution(int(target_elements), grid_x, grid_y, selected_combos, percentages, score))
            
            return results
        except (ValueError, ZeroDivisionError):
            pass
        
        return []
    
    def _create_val_to_types_mapping(self, per_type: Dict[str, float]) -> Dict[float, List[str]]:
        """Crée le mapping valeur -> types"""
        val_to_types = {}
        for apt, units in per_type.items():
            val_to_types.setdefault(units, []).append(apt)
        return val_to_types
    
    def _select_best_combinations(
        self, 
        combos: List[Tuple[float, ...]], 
        val_to_types: Dict[float, List[str]]
    ) -> List[Tuple[float, ...]]:
        """
        Sélectionne les N meilleures combinaisons qui, ensemble, 
        donnent les pourcentages les plus proches des cibles.
        
        Stratégie :
        1. Score chaque combinaison individuellement
        2. Trie par score
        3. Garde les N meilleures
        4. Vérifie que l'ensemble respecte les tolérances
        """
        if not combos:
            return []
        
        # Si pas de limite, retourner toutes les combinaisons
        max_combos = self.config.max_combinations_per_solution
        if max_combos is None or len(combos) <= max_combos:
            return combos
        
        # Scorer chaque combinaison individuellement
        scored_combos = []
        for combo in combos:
            percentages = analyze_combination_percentages(combo, val_to_types, self.config.apt_areas)
            if percentages is None:
                continue
            score = percentage_match_score(percentages, self.config.target_percentages)
            scored_combos.append((score, combo))
        
        if not scored_combos:
            return []
        
        # Trier par score (meilleur score = plus petit)
        scored_combos.sort(key=lambda x: x[0])
        
        # Garder les N meilleures
        selected = [combo for score, combo in scored_combos[:max_combos]]
        
        return selected

    def _find_one_combination(self, values: List[float], target: float) -> List[Tuple[float, ...]]:
        """Retourne au plus une combinaison qui somme à target, sinon []."""
        scale = round(1.0 / self.config.quantum)
        vals_int = sorted(set(int(round(v * scale)) for v in values))
        target_int = int(round(target * scale))
        if not vals_int or min(vals_int) <= 0 or target_int < 0:
            return []
        # DP pour décider faisabilité et reconstruire UNE solution
        reachable = [False] * (target_int + 1)
        prev = [-1] * (target_int + 1)
        choice = [-1] * (target_int + 1)
        reachable[0] = True
        for i, v in enumerate(vals_int):
            for s in range(v, target_int + 1):
                if not reachable[s] and reachable[s - v]:
                    reachable[s] = True
                    prev[s] = s - v
                    choice[s] = i
        if not reachable[target_int]:
            return []
        # Reconstruction
        sol_int: List[int] = []
        s = target_int
        while s > 0 and choice[s] != -1:
            v_idx = choice[s]
            v = vals_int[v_idx]
            sol_int.append(v)
            s = prev[s]
        if sum(sol_int) != target_int:
            return []
        sol = tuple(v / scale for v in sol_int)
        return [sol]
