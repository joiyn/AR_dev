"""
Fonctions de base pour résolution de mix d'appartements sur grille
"""
from itertools import combinations_with_replacement
from typing import Dict, List, Tuple, Optional
from functools import lru_cache, reduce
import math

def quantize(value: float, quantum: float = 0.5, method: str = "round") -> float:
    """Quantifie une valeur selon un quantum et une méthode"""
    k = value / quantum
    if method == "round":
        n = round(k)
    elif method == "floor":
        import math
        n = math.floor(k)
    elif method == "ceil":
        import math
        n = math.ceil(k)
    else:
        raise ValueError("method must be 'round', 'floor', or 'ceil'")
    return n * quantum

def units_per_type(
    grid_x: float, grid_y: float, 
    apt_areas: Dict[str, float],
    quantum: float = 0.5,
    method: str = "round"
) -> Dict[str, float]:
    """Calcule le nombre d'unités de grille par type d'appartement"""
    cell_area = grid_x * grid_y
    if cell_area <= 0:
        raise ValueError("grid_x and grid_y must be positive")
    res = {}
    for apt, area in apt_areas.items():
        if area <= 0:
            raise ValueError(f"Area for '{apt}' must be positive")
        raw_units = area / cell_area
        res[apt] = float(quantize(raw_units, quantum=quantum, method=method))
    return res

_combos_cache: Dict[Tuple[Tuple[int, ...], int], List[Tuple[float, ...]]] = {}

def all_sum_combinations(values: List[float], target: float, quantum: float = 0.5) -> List[Tuple[float, ...]]:
    """Trouve toutes les combinaisons de valeurs qui somment à target (optimisée).

    Optimisations:
    - Conversion entière et PGCD pour réduire le problème
    - DP avec mémoïsation pour énumérer toutes les combinaisons sans doublons
    - Cache inter-appels basé sur (vals_int, target_int)
    """
    scale = round(1.0 / quantum)
    vals_int = sorted(set(int(round(v * scale)) for v in values))
    target_int = int(round(target * scale))
    if not vals_int or min(vals_int) <= 0:
        raise ValueError("Values must be positive.")

    cache_key = (tuple(vals_int), target_int)
    if cache_key in _combos_cache:
        return _combos_cache[cache_key]

    g = reduce(math.gcd, vals_int)
    if target_int % g != 0:
        _combos_cache[cache_key] = []
        return []
    vals_norm = [v // g for v in vals_int]
    target_norm = target_int // g

    @lru_cache(maxsize=None)
    def dfs(start_idx: int, remaining: int) -> Tuple[Tuple[int, ...], ...]:
        if remaining == 0:
            return ((),)
        results_local: List[Tuple[int, ...]] = []
        for i in range(start_idx, len(vals_norm)):
            v = vals_norm[i]
            if v > remaining:
                break
            for tail in dfs(i, remaining - v):
                results_local.append((v,) + tail)
        return tuple(results_local)

    combos_norm = dfs(0, target_norm)
    combos_int = [tuple(v * g for v in combo) for combo in combos_norm]
    sols_float = [tuple(v / scale for v in combo) for combo in combos_int]
    sols_float_sorted = sorted(sols_float, key=lambda x: (len(x), x))
    _combos_cache[cache_key] = sols_float_sorted
    return sols_float_sorted

def analyze_combinations_percentages(
    combos: List[Tuple[float, ...]],
    val_to_types: Dict[float, List[str]],
    apt_areas: Dict[str, float]
) -> Optional[Dict[str, float]]:
    """
    Calcule les pourcentages de m² par type pour un ensemble de combinaisons.
    Retourne None si ambiguïté (plusieurs types pour une même valeur).
    """
    # Vérifier qu'il n'y a pas d'ambiguïté
    for types in val_to_types.values():
        if len(types) != 1:
            return None
    
    # Compter occurrences par valeur
    value_counts: Dict[float, int] = {}
    for combo in combos:
        for v in combo:
            value_counts[v] = value_counts.get(v, 0) + 1
    
    # Calculer m² par type
    sqm_by_type: Dict[str, float] = {}
    total_sqm = 0.0
    for v, count in value_counts.items():
        apt = val_to_types[v][0]
        sqm = apt_areas[apt] * count
        sqm_by_type[apt] = sqm_by_type.get(apt, 0.0) + sqm
        total_sqm += sqm
    
    # Calculer pourcentages
    if total_sqm == 0:
        return None
    
    percentages = {apt: (sqm / total_sqm * 100.0) for apt, sqm in sqm_by_type.items()}
    return percentages

def percentage_match_score(actual: Dict[str, float], target: Dict[str, float]) -> float:
    """
    Score de correspondance entre pourcentages réels et cibles.
    Retourne la somme des écarts absolus (0 = parfait).
    """
    all_types = set(actual.keys()) | set(target.keys())
    total_diff = 0.0
    for apt in all_types:
        diff = abs(actual.get(apt, 0.0) - target.get(apt, 0.0))
        total_diff += diff
    return total_diff

def percentages_within_tolerance(
    actual: Dict[str, float],
    target: Dict[str, float],
    percentage_tolerance: float = 2.5
) -> bool:
    """
    Vérifie que chaque pourcentage réel est dans la plage [cible ± tolerance].
    """
    all_types = set(actual.keys()) | set(target.keys())
    for apt in all_types:
        actual_val = actual.get(apt, 0.0)
        target_val = target.get(apt, 0.0)
        if abs(actual_val - target_val) > percentage_tolerance:
            return False
    return True

# ============= MODES D'UTILISATION =============

def mode_direct(
    grid_x: float,
    grid_y: float,
    apt_areas: Dict[str, float],
    target_elements: float,
    quantum: float = 0.5,
    method: str = "round"
) -> Tuple[Dict[str, float], List[Tuple[float, ...]], Dict[str, float]]:
    """
    Mode direct : dimensions + target → combinaisons + pourcentages
    
    Retourne : (unités_par_type, combinaisons, pourcentages)
    """
    per_type = units_per_type(grid_x, grid_y, apt_areas, quantum=quantum, method=method)
    unique_values = sorted(set(per_type.values()))
    combos = all_sum_combinations(unique_values, target_elements, quantum=quantum)
    
    # Créer mapping valeur → types
    val_to_types: Dict[float, List[str]] = {}
    for apt, units in per_type.items():
        val_to_types.setdefault(units, []).append(apt)
    
    percentages = analyze_combinations_percentages(combos, val_to_types, apt_areas) or {}
    
    return per_type, combos, percentages

def mode_find_target_elements(
    grid_x: float,
    grid_y: float,
    apt_areas: Dict[str, float],
    target_percentages: Dict[str, float],
    quantum: float = 0.5,
    method: str = "round",
    search_range: Tuple[int, int] = (10, 50),
    percentage_tolerance: float = 2.5
) -> List[Tuple[float, List[Tuple[float, ...]], Dict[str, float], float]]:
    """
    Dimensions fixées → trouve target_elements optimal
    
    percentage_tolerance : plage acceptable pour chaque type (ex: 2.5% → accepte ±2.5%)
    
    Retourne : [(target_elements, combinaisons, pourcentages_réels, score), ...]
    Trié par score croissant (meilleur en premier)
    """
    per_type = units_per_type(grid_x, grid_y, apt_areas, quantum=quantum, method=method)
    unique_values = sorted(set(per_type.values()))
    
    # Créer mapping valeur → types
    val_to_types: Dict[float, List[str]] = {}
    for apt, units in per_type.items():
        val_to_types.setdefault(units, []).append(apt)
    
    results = []
    start, end = search_range
    
    for target in range(start, end + 1):
        target_float = float(target)
        combos = all_sum_combinations(unique_values, target_float, quantum=quantum)
        
        if not combos:
            continue
        
        percentages = analyze_combinations_percentages(combos, val_to_types, apt_areas)
        if percentages is None:
            continue
        
        # Vérifier que chaque type est dans sa plage
        if not percentages_within_tolerance(percentages, target_percentages, percentage_tolerance):
            continue
        
        score = percentage_match_score(percentages, target_percentages)
        results.append((target_float, combos, percentages, score))
    
    results.sort(key=lambda x: x[3])
    return results

def mode_find_grid_dimensions(
    target_elements: float,
    apt_areas: Dict[str, float],
    target_percentages: Dict[str, float],
    fixed_dimension: Optional[Tuple[str, float]] = None,
    quantum: float = 0.5,
    method: str = "round",
    search_range: Tuple[float, float] = (2.0, 10.0),
    search_step: float = 0.1,
    percentage_tolerance: float = 2.5,
    round_variations: bool = False
) -> List[Tuple[float, float, List[Tuple[float, ...]], Dict[str, float], float]]:
    """
    target_elements fixé → trouve dimensions de grille optimales
    
    fixed_dimension : ('x', 3.0) ou ('y', 4.854) pour fixer une dimension
    percentage_tolerance : plage acceptable pour chaque type (ex: 2.5% → accepte ±2.5%)
    
    Retourne : [(grid_x, grid_y, combinaisons, pourcentages_réels, score), ...]
    Trié par score croissant (meilleur en premier)
    """
    results = []
    start, end = search_range
    steps = int((end - start) / search_step) + 1
    search_values = [start + i * search_step for i in range(steps)]
    
    if fixed_dimension:
        dim_name, dim_value = fixed_dimension
        if dim_name == 'x':
            for y in search_values:
                results.extend(_evaluate_grid(dim_value, y, target_elements, apt_areas, 
                                             target_percentages, quantum, method, percentage_tolerance, round_variations))
        else:
            for x in search_values:
                results.extend(_evaluate_grid(x, dim_value, target_elements, apt_areas, 
                                             target_percentages, quantum, method, percentage_tolerance, round_variations))
    else:
        for x in search_values:
            for y in search_values:
                results.extend(_evaluate_grid(x, y, target_elements, apt_areas, 
                                             target_percentages, quantum, method, percentage_tolerance, round_variations))
    
    results.sort(key=lambda x: x[4])
    return results

def _evaluate_grid(
    grid_x: float,
    grid_y: float,
    target_elements: float,
    apt_areas: Dict[str, float],
    target_percentages: Dict[str, float],
    quantum: float,
    method: str,
    percentage_tolerance: float,
    round_variations: bool
) -> List[Tuple[float, float, List[Tuple[float, ...]], Dict[str, float], float]]:
    """Helper pour évaluer une grille donnée"""
    try:
        results: List[Tuple[float, float, List[Tuple[float, ...]], Dict[str, float], float]] = []
        
        if not round_variations:
            per_type = units_per_type(grid_x, grid_y, apt_areas, quantum=quantum, method=method)
            unique_values = sorted(set(per_type.values()))
            
            val_to_types: Dict[float, List[str]] = {}
            for apt, units in per_type.items():
                val_to_types.setdefault(units, []).append(apt)
            
            combos = all_sum_combinations(unique_values, target_elements, quantum=quantum)
            
            if not combos:
                return []
            
            percentages = analyze_combinations_percentages(combos, val_to_types, apt_areas)
            if percentages is None:
                return []
            
            if not percentages_within_tolerance(percentages, target_percentages, percentage_tolerance):
                return []
            
            score = percentage_match_score(percentages, target_percentages)
            return [(grid_x, grid_y, combos, percentages, score)]
        
        # Variante: explorer floor/ceil (+ quantum si exact)
        cell_area = grid_x * grid_y
        if cell_area <= 0:
            return []
        
        from itertools import product
        types_list: List[str] = []
        candidates_per_type: List[List[float]] = []
        
        for apt, area in apt_areas.items():
            if area <= 0:
                return []
            raw_units = area / cell_area
            lower = quantize(raw_units, quantum=quantum, method="floor")
            upper = quantize(raw_units, quantum=quantum, method="ceil")
            if lower == upper:
                # exact: tester valeur exacte et + quantum
                candidates = [float(lower), float(lower + quantum)]
            else:
                candidates = sorted({float(lower), float(upper)})
            types_list.append(apt)
            candidates_per_type.append(candidates)
        
        # Cache local des combinaisons par set d'unités (clé entière)
        scale = round(1.0 / quantum)
        combos_by_values_key: Dict[Tuple[int, ...], List[Tuple[float, ...]]] = {}

        for choice in product(*candidates_per_type):
            scenario_per_type = {apt: units for apt, units in zip(types_list, choice)}
            unique_values = sorted(set(scenario_per_type.values()))
            
            val_to_types: Dict[float, List[str]] = {}
            for apt, units in scenario_per_type.items():
                val_to_types.setdefault(units, []).append(apt)
            # Ambiguïté: si une valeur d'unités correspond à plusieurs types, inutile de poursuivre
            if any(len(t) != 1 for t in val_to_types.values()):
                continue
            
            key_int = tuple(sorted(int(round(v * scale)) for v in unique_values))
            if key_int in combos_by_values_key:
                combos = combos_by_values_key[key_int]
            else:
                combos = all_sum_combinations(unique_values, target_elements, quantum=quantum)
                combos_by_values_key[key_int] = combos
            if not combos:
                continue
            
            percentages = analyze_combinations_percentages(combos, val_to_types, apt_areas)
            if percentages is None:
                continue
            
            if not percentages_within_tolerance(percentages, target_percentages, percentage_tolerance):
                continue
            
            score = percentage_match_score(percentages, target_percentages)
            results.append((grid_x, grid_y, combos, percentages, score))
        
        return results
    except (ValueError, ZeroDivisionError):
        pass
    
    return []
