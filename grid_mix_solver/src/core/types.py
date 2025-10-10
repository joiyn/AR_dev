"""
Types et interfaces pour le solveur de mix d'appartements
"""
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class GridConfig:
    """Configuration d'une grille"""
    x: float
    y: float
    
    @property
    def area(self) -> float:
        return self.x * self.y


@dataclass
class ApartmentType:
    """Type d'appartement avec sa surface"""
    name: str
    area: float


@dataclass
class SearchRange:
    """Plage de recherche pour une dimension"""
    min_val: float
    max_val: float
    step: float = 0.1
    
    @property
    def is_fixed(self) -> bool:
        return self.min_val == self.max_val


@dataclass
class SolverConfig:
    """Configuration complète du solveur"""
    # Surfaces des appartements
    apt_areas: Dict[str, float]
    
    # Pourcentages cibles
    target_percentages: Dict[str, float]
    
    # Paramètres de recherche
    search_range_x: SearchRange
    search_range_y: SearchRange
    target_elements_range: Tuple[int, int]
    
    # Paramètres de calcul
    quantum: float = 0.5
    method: str = "round"
    # Peut être:
    # - float: tolérance globale symétrique (± valeur en points de %)
    # - Dict[str, float]: tolérance symétrique par type (± valeur)
    # - Dict[str, Tuple[float, float]]: bornes absolues (min%, max%) par type
    percentage_tolerance: Union[
        float,
        Dict[str, Union[float, Tuple[float, float]]]
    ] = 2.0
    round_variations: bool = False
    # Recherche exhaustive de toutes les combinaisons possibles
    # Si False, on cherche seulement une combinaison valide (beaucoup plus rapide)
    search_combinations: bool = True
    
    # Paramètres de projet
    nombre_logements: Optional[int] = None
    max_etages_par_batiment: Optional[float] = None
    net_to_floor_factor: float = 1.12
    
    # Paramètres de sortie
    max_solutions_displayed: int = 100
    save_to_file: bool = True
    output_directory: str = "results"


@dataclass
class Solution:
    """Une solution trouvée par le solveur"""
    target_elements: int
    grid_x: float
    grid_y: float
    combinations: List[Tuple[float, ...]]
    percentages: Dict[str, float]
    score: float
    
    @property
    def grid_config(self) -> GridConfig:
        return GridConfig(self.grid_x, self.grid_y)
    
    @property
    def cell_area(self) -> float:
        return self.grid_x * self.grid_y


@dataclass
class ProjectAnalysis:
    """Analyse d'un projet pour une solution donnée"""
    solution: Solution
    nombre_logements: int
    max_etages_par_batiment: float
    
    # Calculs dérivés
    nb_par_type: Dict[str, int]
    surface_par_type: Dict[str, float]
    surface_totale_logements: float
    total_cells_needed: float
    elements_par_etage: int
    nb_etages: int
    nb_batiments: float
    nb_batiments_entiers: int
    footprint_par_batiment: float
    empreinte_totale: float
