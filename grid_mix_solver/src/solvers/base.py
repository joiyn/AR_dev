"""
Classe de base pour les solveurs
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from ..core.types import SolverConfig, Solution


class BaseSolver(ABC):
    """Classe de base pour tous les solveurs"""
    
    def __init__(self, config: SolverConfig):
        self.config = config
    
    @abstractmethod
    def solve(self) -> List[Solution]:
        """Résout le problème et retourne les solutions"""
        pass
    
    def _create_solution(
        self,
        target_elements: int,
        grid_x: float,
        grid_y: float,
        combinations: List[Tuple[float, ...]],
        percentages: Dict[str, float],
        score: float
    ) -> Solution:
        """Crée une solution à partir des paramètres"""
        return Solution(
            target_elements=target_elements,
            grid_x=grid_x,
            grid_y=grid_y,
            combinations=combinations,
            percentages=percentages,
            score=score
        )
