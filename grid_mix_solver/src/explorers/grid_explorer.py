"""
Explorateur de grilles - Interface principale refactorisée
"""
from typing import List, Tuple, Optional

from ..core.types import SolverConfig, SearchRange
from ..solvers.grid_solver import GridSolver
from .report_generator import ReportGenerator


def explore_solutions(
    apt_areas,
    target_percentages,
    quantum=0.5,
    method="round",
    search_range_x=(2.5, 4.0),
    search_range_y=(3.0, 6.0),
    search_step=0.1,
    target_elements_range=(10, 35),
    percentage_tolerance=7.0,
    max_combinations_per_solution=3,
    max_solutions_displayed=10,
    save_to_file=True,
    output_directory="results",
    nombre_logements=None,
    max_etages_par_batiment=None,
    round_variations=False,
    search_combinations=True
) -> Tuple[List, Optional[str]]:
    """
    Explore différentes configurations pour trouver celle qui respecte les pourcentages cibles.
    
    Cette fonction maintient la compatibilité avec l'ancienne interface.
    
    Returns:
        tuple: (all_solutions, output_path)
    """
    
    # Convertir les paramètres en configuration
    config = SolverConfig(
        apt_areas=apt_areas,
        target_percentages=target_percentages,
        search_range_x=SearchRange(search_range_x[0], search_range_x[1], search_step),
        search_range_y=SearchRange(search_range_y[0], search_range_y[1], search_step),
        target_elements_range=target_elements_range,
        quantum=quantum,
        method=method,
        percentage_tolerance=percentage_tolerance,
        max_combinations_per_solution=max_combinations_per_solution,
        round_variations=round_variations,
        search_combinations=search_combinations,
        nombre_logements=nombre_logements,
        max_etages_par_batiment=max_etages_par_batiment,
        max_solutions_displayed=max_solutions_displayed,
        save_to_file=save_to_file,
        output_directory=output_directory
    )
    
    # Créer le solveur et résoudre
    solver = GridSolver(config)
    solutions = solver.solve()
    
    # Générer le rapport
    report_generator = ReportGenerator(config)
    output_path = report_generator.generate_report(solutions)
    
    # Convertir les solutions en format legacy pour compatibilité
    legacy_solutions = []
    for solution in solutions:
        legacy_solution = (
            solution.target_elements,
            solution.grid_x,
            solution.grid_y,
            solution.combinations,
            solution.percentages,
            solution.score
        )
        legacy_solutions.append(legacy_solution)
    
    return legacy_solutions, output_path
