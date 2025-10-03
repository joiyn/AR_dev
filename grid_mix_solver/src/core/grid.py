"""
Calculs de grille et unités
"""
from typing import Dict
from .types import GridConfig


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
    grid_config: GridConfig, 
    apt_areas: Dict[str, float],
    quantum: float = 0.5,
    method: str = "round"
) -> Dict[str, float]:
    """Calcule le nombre d'unités de grille par type d'appartement"""
    if grid_config.area <= 0:
        raise ValueError("grid_x and grid_y must be positive")
    
    res = {}
    for apt, area in apt_areas.items():
        if area <= 0:
            raise ValueError(f"Area for '{apt}' must be positive")
        raw_units = area / grid_config.area
        res[apt] = float(quantize(raw_units, quantum=quantum, method=method))
    return res


def units_per_type_legacy(
    grid_x: float, grid_y: float, 
    apt_areas: Dict[str, float],
    quantum: float = 0.5,
    method: str = "round"
) -> Dict[str, float]:
    """Version legacy pour compatibilité avec l'ancien code"""
    grid_config = GridConfig(grid_x, grid_y)
    return units_per_type(grid_config, apt_areas, quantum, method)
