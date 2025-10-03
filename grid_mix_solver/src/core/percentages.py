"""
Calculs de pourcentages et scores
"""
from typing import Dict, List, Tuple, Optional


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
