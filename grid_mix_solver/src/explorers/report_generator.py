"""
Générateur de rapports détaillés
"""
from typing import List, Optional, TextIO
from datetime import datetime
import os
import math
import shutil
import re

from ..core.types import Solution, SolverConfig, ProjectAnalysis


class ReportGenerator:
    """Générateur de rapports pour les solutions"""
    
    def __init__(self, config: SolverConfig):
        self.config = config
    
    def generate_report(
        self, 
        solutions: List[Solution], 
        output_path: Optional[str] = None
    ) -> str:
        """Génère un rapport complet des solutions"""
        
        # Créer le dossier de sortie si nécessaire
        if self.config.save_to_file and not os.path.exists(self.config.output_directory):
            os.makedirs(self.config.output_directory)
        
        # Générer le nom de fichier avec timestamp
        timestamp: Optional[str] = None
        if output_path is None and self.config.save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"solutions_{timestamp}.txt"
            output_path = os.path.join(self.config.output_directory, output_filename)
        elif output_path is not None and self.config.save_to_file:
            # Tenter d'extraire le timestamp du chemin fourni
            m = re.search(r"solutions_(\d{8}_\d{6})\\.txt$", output_path)
            if m:
                timestamp = m.group(1)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ouvrir le fichier de sortie
        log_file = open(output_path, 'w', encoding='utf-8') if self.config.save_to_file else None
        
        try:
            # En-tête console simplifié
            self._print_console_header()
            
            # En-tête fichier détaillé
            if log_file:
                self._write_file_header(log_file)
            
            # Traitement des solutions
            if solutions:
                self._process_solutions(solutions, log_file)
            else:
                self._write_no_solutions(log_file)
            
            # Sauvegarder une copie des paramètres (main.py) avec le même timestamp
            if self.config.save_to_file and timestamp:
                try:
                    project_root = os.getcwd()
                    src_params = os.path.join(project_root, "main.py")
                    if os.path.exists(src_params):
                        params_filename = f"main_{timestamp}.py"
                        dst_params = os.path.join(self.config.output_directory, params_filename)
                        shutil.copyfile(src_params, dst_params)
                        print(f"📎 Paramètres sauvegardés dans : {dst_params}")
                        if log_file:
                            log_file.write(f"Paramètres (copie de main.py) : {dst_params}\n")
                except Exception:
                    # Ne pas interrompre le flux si la copie échoue
                    pass

            # Message console simplifié
            if solutions:
                best = solutions[0]
                print(f"\n✅ {len(solutions)} solution(s) trouvée(s)")
                print(f"🏆 Meilleure : Grille {best.grid_x:g}×{best.grid_y:.3f}m, {best.target_elements} éléments, score {best.score:.2f}")
            else:
                print("\n❌ Aucune solution trouvée")
            
            return output_path
            
        finally:
            if log_file:
                log_file.close()
                if self.config.save_to_file:
                    print(f"💾 Résultats détaillés dans : {output_path}")
    
    def _print_console_header(self):
        """Affiche l'en-tête console simplifié"""
        print("═" * 80)
        print("RECHERCHE DE CONFIGURATION OPTIMALE")
        print("═" * 80)
        print(f"🎯 Cibles : {self.config.target_percentages}")
        
        x_fixed = self.config.search_range_x.is_fixed
        y_fixed = self.config.search_range_y.is_fixed
        
        if x_fixed and y_fixed:
            print(f"📐 Grille fixée : {self.config.search_range_x.min_val:g} × {self.config.search_range_y.min_val:g} m")
        elif x_fixed:
            print(f"📐 grid_x fixé : {self.config.search_range_x.min_val:g} m, grid_y : {self.config.search_range_y.min_val:g}-{self.config.search_range_y.max_val:g} m")
        elif y_fixed:
            print(f"📐 grid_y fixé : {self.config.search_range_y.min_val:g} m, grid_x : {self.config.search_range_x.min_val:g}-{self.config.search_range_x.max_val:g} m")
        else:
            print(f"📐 grid_x : {self.config.search_range_x.min_val:g}-{self.config.search_range_x.max_val:g} m, grid_y : {self.config.search_range_y.min_val:g}-{self.config.search_range_y.max_val:g} m")
        
        print(f"🔍 Éléments de grille : {self.config.target_elements_range[0]}-{self.config.target_elements_range[1]}")
        print()
    
    def _write_file_header(self, log_file: TextIO):
        """Écrit l'en-tête détaillé dans le fichier"""
        log_file.write("═" * 80 + "\n")
        log_file.write("RECHERCHE DE CONFIGURATION OPTIMALE\n")
        log_file.write("═" * 80 + "\n\n")
        log_file.write(f"📋 Pourcentages imposés : {self.config.target_percentages}\n")
        # Affichage tolérance: accepter float, dict de float, dict de range
        tol = self.config.percentage_tolerance
        if isinstance(tol, (int, float)):
            log_file.write(f"🎯 Tolérance par type : ±{float(tol)}%\n")
        elif isinstance(tol, dict):
            pretty = {}
            for k, v in tol.items():
                if isinstance(v, (int, float)):
                    pretty[k] = f"±{float(v)}%"
                else:
                    pretty[k] = f"[{v[0]}, {v[1]}]%"
            log_file.write(f"🎯 Tolérance par type : {pretty}\n")
        else:
            log_file.write(f"🎯 Tolérance par type : {tol}\n")
        log_file.write(f"📐 Plages de recherche :\n")
        log_file.write(f"   • grid_x : {self.config.search_range_x.min_val:g} à {self.config.search_range_x.max_val:g} m")
        if self.config.search_range_x.is_fixed:
            log_file.write(" (fixé)")
        log_file.write("\n")
        log_file.write(f"   • grid_y : {self.config.search_range_y.min_val:g} à {self.config.search_range_y.max_val:g} m")
        if self.config.search_range_y.is_fixed:
            log_file.write(" (fixé)")
        log_file.write("\n")
        log_file.write(f"   • pas : {self.config.search_range_x.step:g} m\n")
        log_file.write(f"🔍 Recherche : target_elements (unités de grille) de {self.config.target_elements_range[0]} à {self.config.target_elements_range[1]}\n\n")
        log_file.write("ℹ️  NOTE : 1 'élément' = 1 unité de grille (pas 1 appartement)\n")
        log_file.write("   Exemple : 16 éléments peuvent donner 3 appartements (4+5+7 unités)\n\n")
    
    def _process_solutions(self, solutions: List[Solution], log_file: Optional[TextIO]):
        """Traite et affiche les solutions"""
        if log_file:
            log_file.write("\n" + "═" * 80 + "\n")
            log_file.write(f"📊 RÉSULTATS : {len(solutions)} solution(s) trouvée(s)\n")
            log_file.write("═" * 80 + "\n\n")
        
        for i, solution in enumerate(solutions[:self.config.max_solutions_displayed], 1):
            self._write_solution(solution, i, log_file)
        
        if len(solutions) > self.config.max_solutions_displayed and log_file:
            log_file.write(f"... et {len(solutions) - self.config.max_solutions_displayed} autre(s) solution(s)\n\n")
        
        # Résumé de la meilleure
        if log_file:
            best = solutions[0]
            log_file.write("═" * 80 + "\n")
            log_file.write("💡 RECOMMANDATION : Solution optimale\n")
            log_file.write("═" * 80 + "\n")
            log_file.write(f"Utiliser une grille de {best.grid_x:g} × {best.grid_y:.3f} m avec {best.target_elements} éléments de grille\n")
            log_file.write(f"Précision : score de {best.score:.2f} (plus bas = meilleur)\n")
            if best.combinations:
                nb_apts = len(best.combinations[0])
                log_file.write(f"Nombre d'appartements (exemple) : {nb_apts}\n")
    
    def _write_solution(self, solution: Solution, index: int, log_file: Optional[TextIO]):
        """Écrit une solution dans le fichier"""
        if not log_file:
            return
        
        # Calculer les unités par type pour cette grille
        from ..core.grid import units_per_type
        from ..core.types import GridConfig
        
        per_type = units_per_type(
            GridConfig(solution.grid_x, solution.grid_y), 
            self.config.apt_areas, 
            quantum=self.config.quantum, 
            method=self.config.method
        )
        
        # Titre
        log_file.write(f"{'🏆' if index == 1 else '📌'} Solution {index} (score: {solution.score:.2f})\n")
        
        # Informations de base
        log_file.write(f"  └─ {solution.target_elements} éléments de grille\n")
        log_file.write(f"  └─ Grille : {solution.grid_x:g} × {solution.grid_y:.3f} m = {solution.cell_area:.3f} m² par cellule\n")
        
        # Informations sur étages et bâtiments
        if self.config.nombre_logements and self.config.max_etages_par_batiment:
            analysis = self._analyze_project(solution)
            self._write_project_analysis(analysis, log_file)
        
        log_file.write(f"\n")
        
        # Configuration des types d'appartements
        log_file.write(f"  └─ Configuration des types :\n")
        for apt in sorted(self.config.apt_areas.keys()):
            apt_area = self.config.apt_areas[apt]
            units = per_type.get(apt, 0.0)
            actual_sqm = units * solution.cell_area
            log_file.write(f"      • {apt} : {units:g} éléments de grille = {actual_sqm:.1f} m² (cible: {apt_area} m²)\n")
        log_file.write(f"\n")
        
        # Pourcentages
        log_file.write(f"  └─ Pourcentages de surface obtenus :\n")
        for apt in sorted(self.config.target_percentages.keys()):
            target_val = self.config.target_percentages[apt]
            actual_val = solution.percentages.get(apt, 0.0)
            diff = actual_val - target_val
            # Heuristique d'emoji selon respect tolérance (approx)
            ok = False
            tol = self.config.percentage_tolerance
            if isinstance(tol, (int, float)):
                ok = abs(diff) <= float(tol)
            elif isinstance(tol, dict):
                t = tol.get(apt)
                if isinstance(t, (int, float)):
                    ok = abs(diff) <= float(t)
                elif isinstance(t, tuple) and len(t) == 2:
                    ok = (t[0] <= actual_val <= t[1])
            emoji = "✓" if ok else "~"
            log_file.write(f"      {emoji} {apt}: {actual_val:5.1f}% (cible: {target_val:5.1f}%, écart: {diff:+5.1f}%)\n")
        log_file.write(f"\n")
        
        # Combinaisons
        log_file.write(f"  └─ {len(solution.combinations)} combinaison(s) possible(s) :\n")
        for j, combo in enumerate(solution.combinations, 1):
            combo_str = " + ".join(f"{v:g}" for v in combo) + f" = {sum(combo):g}"
            log_file.write(f"      {j}. {combo_str}\n")
        log_file.write(f"\n")
    
    def _analyze_project(self, solution: Solution) -> ProjectAnalysis:
        """Analyse un projet pour une solution donnée"""
        # Calculer le nombre de logements par type selon les pourcentages
        nb_par_type = {}
        surface_par_type = {}
        surface_totale_logements = 0
        
        for apt in self.config.apt_areas.keys():
            # Nombre de logements de ce type (arrondi)
            nb = round(self.config.nombre_logements * self.config.target_percentages[apt] / 100)
            nb_par_type[apt] = nb
            
            # Surface pour ce type
            surface = nb * self.config.apt_areas[apt]
            surface_par_type[apt] = surface
            surface_totale_logements += surface
        
        # Nombre total de cellules nécessaires
        total_cells_needed = surface_totale_logements / solution.cell_area
        
        # Nombre d'éléments par étage
        elements_par_etage = solution.target_elements
        
        # Nombre d'étages nécessaires
        nb_etages = math.ceil(total_cells_needed / elements_par_etage)
        
        # Nombre de bâtiments nécessaires (avec décimales)
        nb_batiments = nb_etages / self.config.max_etages_par_batiment
        
        # Empreintes au sol
        footprint_par_batiment = elements_par_etage * solution.cell_area
        nb_batiments_entiers = math.ceil(nb_batiments)
        empreinte_totale = nb_batiments_entiers * footprint_par_batiment
        
        return ProjectAnalysis(
            solution=solution,
            nombre_logements=self.config.nombre_logements,
            max_etages_par_batiment=self.config.max_etages_par_batiment,
            nb_par_type=nb_par_type,
            surface_par_type=surface_par_type,
            surface_totale_logements=surface_totale_logements,
            total_cells_needed=total_cells_needed,
            elements_par_etage=elements_par_etage,
            nb_etages=nb_etages,
            nb_batiments=nb_batiments,
            nb_batiments_entiers=nb_batiments_entiers,
            footprint_par_batiment=footprint_par_batiment,
            empreinte_totale=empreinte_totale
        )
    
    def _write_project_analysis(self, analysis: ProjectAnalysis, log_file: TextIO):
        """Écrit l'analyse du projet dans le fichier"""
        log_file.write(f"\n  └─ Organisation du projet :\n")
        log_file.write(f"      • Nombre total de logements : {analysis.nombre_logements}\n")
        log_file.write(f"      • Répartition par type (selon % cibles) :\n")
        for apt in sorted(analysis.nb_par_type.keys()):
            pct_cible = self.config.target_percentages[apt]
            nb = analysis.nb_par_type[apt]
            surf = analysis.surface_par_type[apt]
            log_file.write(f"         - {apt} : {nb} logements ({pct_cible}%) = {surf:.0f} m²\n")
        log_file.write(f"      • Surface totale logements : {analysis.surface_totale_logements:.0f} m²\n")
        log_file.write(f"      • Éléments par étage : {analysis.elements_par_etage}\n")
        log_file.write(f"      • Nombre d'étages nécessaires : {analysis.nb_etages}\n")
        log_file.write(f"      • Étages max par bâtiment : {analysis.max_etages_par_batiment}\n")
        log_file.write(f"      • Nombre de bâtiments : {analysis.nb_batiments:.2f}\n")
        log_file.write(f"      • Nombre de bâtiments (entiers) : {analysis.nb_batiments_entiers}\n")
        log_file.write(f"      • Empreinte au sol par bâtiment : {analysis.footprint_par_batiment:.0f} m²\n")
        log_file.write(f"      • Empreinte au sol totale : {analysis.empreinte_totale:.0f} m²\n")
    
    def _write_no_solutions(self, log_file: Optional[TextIO]):
        """Écrit le message quand aucune solution n'est trouvée"""
        if log_file:
            log_file.write("❌ Aucune solution trouvée avec les paramètres actuels.\n\n")
            log_file.write("💡 SUGGESTIONS pour trouver des solutions :\n")
            log_file.write("   • Assouplir percentage_tolerance (global ou par type)\n")
            log_file.write(f"   • Élargir target_elements_range (actuellement {self.config.target_elements_range} → essayer (5, 50))\n")
            log_file.write(f"   • Élargir search_range_x/y (actuellement x:{self.config.search_range_x.min_val}-{self.config.search_range_x.max_val}, y:{self.config.search_range_y.min_val}-{self.config.search_range_y.max_val})\n")
            log_file.write(f"   • Réduire search_step pour plus de précision (actuellement {self.config.search_range_x.step} → essayer 0.05)\n")
            if self.config.search_range_x.is_fixed or self.config.search_range_y.is_fixed:
                log_file.write(f"   • Essayer de ne fixer aucune dimension pour explorer x ET y librement\n")
            log_file.write("\n")
