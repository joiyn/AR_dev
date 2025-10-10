"""
Calculs de pourcentages et scores
"""
from typing import Dict, List, Tuple, Optional, Union


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
    percentage_tolerance: Union[float, Dict[str, Union[float, Tuple[float, float]]]] = 2.5
) -> bool:
    """
    Vérifie que chaque pourcentage réel respecte la tolérance.

    Modes supportés pour percentage_tolerance:
      - float: tolérance symétrique globale ±tol
      - Dict[str, float]: tolérance symétrique par type
      - Dict[str, (min, max)]: bornes absolues par type
    """
    all_types = set(actual.keys()) | set(target.keys())
    for apt in all_types:
        actual_val = actual.get(apt, 0.0)
        target_val = target.get(apt, 0.0)

        if isinstance(percentage_tolerance, (int, float)):
            tol = float(percentage_tolerance)
            if abs(actual_val - target_val) > tol:
                return False
        elif isinstance(percentage_tolerance, dict):
            tol_spec = percentage_tolerance.get(apt)
            if tol_spec is None:
                # Par défaut: 0 si non spécifié
                if abs(actual_val - target_val) > 0:
                    return False
            else:
                if isinstance(tol_spec, (int, float)):
                    if abs(actual_val - target_val) > float(tol_spec):
                        return False
                else:
                    # Tuple[min%, max%]
                    min_allowed, max_allowed = tol_spec
                    if not (min_allowed <= actual_val <= max_allowed):
                        return False
        else:
            # Forme inattendue
            return False
    return True
