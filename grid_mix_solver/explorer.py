"""
Module d'exploration pour trouver la configuration optimale
"""

from solver import mode_find_grid_dimensions, units_per_type
from datetime import datetime
import os


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
    max_solutions_displayed=10,
    save_to_file=True,
    output_directory="results",
    nombre_logements=None,
    max_etages_par_batiment=None,
    round_variations=False
):
    """
    Explore différentes configurations pour trouver celle qui respecte les pourcentages cibles.
    
    Returns:
        tuple: (all_solutions, output_path)
    """
    
    def fmt_combo(combo):
        """Formatte une combinaison pour l'affichage"""
        return " + ".join(f"{v:g}" for v in combo) + f" = {sum(combo):g}"
    
    # Créer le dossier de sortie si nécessaire
    if save_to_file and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Générer le nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"solutions_{timestamp}.txt" if save_to_file else None
    output_path = os.path.join(output_directory, output_filename) if save_to_file else None
    
    # Fonction pour écrire à la fois à l'écran et dans le fichier
    def print_and_log(message="", file_handle=None):
        print(message)
        if file_handle:
            file_handle.write(message + "\n")
    
    # Ouvrir le fichier de sortie
    log_file = open(output_path, 'w', encoding='utf-8') if save_to_file else None
    
    # Déterminer si une dimension est fixée
    x_fixed = (search_range_x[0] == search_range_x[1])
    y_fixed = (search_range_y[0] == search_range_y[1])
    
    # En-tête console simplifié
    print("═" * 80)
    print("RECHERCHE DE CONFIGURATION OPTIMALE")
    print("═" * 80)
    print(f"🎯 Cibles : {target_percentages}")
    if x_fixed and y_fixed:
        print(f"📐 Grille fixée : {search_range_x[0]:g} × {search_range_y[0]:g} m")
    elif x_fixed:
        print(f"📐 grid_x fixé : {search_range_x[0]:g} m, grid_y : {search_range_y[0]:g}-{search_range_y[1]:g} m")
    elif y_fixed:
        print(f"📐 grid_y fixé : {search_range_y[0]:g} m, grid_x : {search_range_x[0]:g}-{search_range_x[1]:g} m")
    else:
        print(f"📐 grid_x : {search_range_x[0]:g}-{search_range_x[1]:g} m, grid_y : {search_range_y[0]:g}-{search_range_y[1]:g} m")
    print(f"🔍 Éléments de grille : {target_elements_range[0]}-{target_elements_range[1]}")
    print()
    
    # En-tête fichier détaillé
    if log_file:
        log_file.write("═" * 80 + "\n")
        log_file.write("RECHERCHE DE CONFIGURATION OPTIMALE\n")
        log_file.write("═" * 80 + "\n\n")
        log_file.write(f"📋 Pourcentages imposés : {target_percentages}\n")
        log_file.write(f"🎯 Tolérance par type : ±{percentage_tolerance}%\n")
        log_file.write(f"📐 Plages de recherche :\n")
        log_file.write(f"   • grid_x : {search_range_x[0]:g} à {search_range_x[1]:g} m")
        if x_fixed:
            log_file.write(" (fixé)")
        log_file.write("\n")
        log_file.write(f"   • grid_y : {search_range_y[0]:g} à {search_range_y[1]:g} m")
        if y_fixed:
            log_file.write(" (fixé)")
        log_file.write("\n")
        log_file.write(f"   • pas : {search_step:g} m\n")
        log_file.write(f"🔍 Recherche : target_elements (unités de grille) de {target_elements_range[0]} à {target_elements_range[1]}\n\n")
        log_file.write("ℹ️  NOTE : 1 'élément' = 1 unité de grille (pas 1 appartement)\n")
        log_file.write("   Exemple : 16 éléments peuvent donner 3 appartements (4+5+7 unités)\n\n")
    
    all_solutions = []
    
    # Explorer différents nombres d'éléments de grille
    for target_elem in range(target_elements_range[0], target_elements_range[1] + 1):
        print(f"🔎 {target_elem}", end=" ", flush=True)
        if log_file:
            log_file.write(f"🔎 Test avec {target_elem} éléments de grille... ")
            log_file.flush()
        
        results = []
        
        # Explorer en fixant y et variant x
        steps_y = int((search_range_y[1] - search_range_y[0]) / search_step) + 1 if search_range_y[0] != search_range_y[1] else 1
        for i in range(steps_y):
            y_val = search_range_y[0] + i * search_step
            results_y = mode_find_grid_dimensions(
                float(target_elem), apt_areas, target_percentages,
                fixed_dimension=('y', y_val),
                quantum=quantum, method=method,
                search_range=search_range_x, search_step=search_step,
                percentage_tolerance=percentage_tolerance,
                round_variations=round_variations
            )
            results.extend(results_y)
        
        if results:
            print(f"✅", end="")
            if log_file:
                log_file.write(f"✅ {len(results)} solution(s)\n")
                log_file.flush()
            all_solutions.extend([(target_elem, *r) for r in results])
        else:
            print(f"❌", end="")
            if log_file:
                log_file.write("❌\n")
                log_file.flush()
    
    # Trier par score (meilleur d'abord)
    all_solutions.sort(key=lambda x: x[5])
    
    # Affichage des résultats (fichier seulement)
    if log_file:
        log_file.write("\n" + "═" * 80 + "\n")
        log_file.write(f"📊 RÉSULTATS : {len(all_solutions)} solution(s) trouvée(s)\n")
        log_file.write("═" * 80 + "\n\n")
    
    if all_solutions:
        for i, (target, gx, gy, combos, pct, score) in enumerate(all_solutions[:max_solutions_displayed], 1):
            # Calculer les unités par type pour cette grille
            cell_area = gx * gy
            per_type = units_per_type(gx, gy, apt_areas, quantum=quantum, method=method)
            
            # Calculer étages et bâtiments si nombre de logements fourni
            if nombre_logements and max_etages_par_batiment:
                import math
                
                # Calculer le nombre de logements par type selon les pourcentages
                # et la surface totale réelle
                nb_par_type = {}
                surface_par_type = {}
                surface_totale_logements = 0
                
                for apt in apt_areas.keys():
                    # Nombre de logements de ce type (arrondi)
                    nb = round(nombre_logements * target_percentages[apt] / 100)
                    nb_par_type[apt] = nb
                    
                    # Surface pour ce type
                    surface = nb * apt_areas[apt]
                    surface_par_type[apt] = surface
                    surface_totale_logements += surface
                
                # Nombre total de cellules nécessaires
                total_cells_needed = surface_totale_logements / cell_area
                
                # Nombre d'éléments par étage
                elements_par_etage = target
                
                # Nombre d'étages nécessaires
                nb_etages = math.ceil(total_cells_needed / elements_par_etage)
                
                # Nombre de bâtiments nécessaires (avec décimales)
                nb_batiments = nb_etages / max_etages_par_batiment
                
                # Empreintes au sol
                footprint_par_batiment = elements_par_etage * cell_area
                nb_batiments_entiers = math.ceil(nb_batiments)
                empreinte_totale = nb_batiments_entiers * footprint_par_batiment
            
            # Titre (seulement dans le fichier)
            if log_file:
                log_file.write(f"{'🏆' if i == 1 else '📌'} Solution {i} (score: {score:.2f})\n")
            
            # Informations de base (fichier seulement)
            if log_file:
                log_file.write(f"  └─ {target} éléments de grille\n")
                log_file.write(f"  └─ Grille : {gx:g} × {gy:.3f} m = {cell_area:.3f} m² par cellule\n")
                
                # Informations sur étages et bâtiments
                if nombre_logements and max_etages_par_batiment:
                    log_file.write(f"\n  └─ Organisation du projet :\n")
                    log_file.write(f"      • Nombre total de logements : {nombre_logements}\n")
                    log_file.write(f"      • Répartition par type (selon % cibles) :\n")
                    for apt in sorted(nb_par_type.keys()):
                        pct_cible = target_percentages[apt]
                        nb = nb_par_type[apt]
                        surf = surface_par_type[apt]
                        log_file.write(f"         - {apt} : {nb} logements ({pct_cible}%) = {surf:.0f} m²\n")
                    log_file.write(f"      • Surface totale logements : {surface_totale_logements:.0f} m²\n")
                    log_file.write(f"      • Éléments par étage : {elements_par_etage}\n")
                    log_file.write(f"      • Nombre d'étages nécessaires : {nb_etages}\n")
                    log_file.write(f"      • Étages max par bâtiment : {max_etages_par_batiment}\n")
                    log_file.write(f"      • Nombre de bâtiments : {nb_batiments:.2f}\n")
                    log_file.write(f"      • Nombre de bâtiments (entiers) : {nb_batiments_entiers}\n")
                    log_file.write(f"      • Empreinte au sol par bâtiment : {footprint_par_batiment:.0f} m²\n")
                    log_file.write(f"      • Empreinte au sol totale : {empreinte_totale:.0f} m²\n")
                
                log_file.write(f"\n")
            
            # Configuration des types d'appartements (fichier seulement)
            if log_file:
                log_file.write(f"  └─ Configuration des types :\n")
                for apt in sorted(apt_areas.keys()):
                    apt_area = apt_areas[apt]
                    units = per_type.get(apt, 0.0)
                    actual_sqm = units * cell_area
                    log_file.write(f"      • {apt} : {units:g} éléments de grille = {actual_sqm:.1f} m² (cible: {apt_area} m²)\n")
                log_file.write(f"\n")
            
            # Pourcentages (fichier seulement)
            if log_file:
                log_file.write(f"  └─ Pourcentages de surface obtenus :\n")
                for apt in sorted(target_percentages.keys()):
                    target_val = target_percentages[apt]
                    actual_val = pct.get(apt, 0.0)
                    diff = actual_val - target_val
                    emoji = "✓" if abs(diff) <= percentage_tolerance/2 else "~"
                    log_file.write(f"      {emoji} {apt}: {actual_val:5.1f}% (cible: {target_val:5.1f}%, écart: {diff:+5.1f}%)\n")
                log_file.write(f"\n")
            
            # Combinaisons (fichier seulement)
            if log_file:
                log_file.write(f"  └─ {len(combos)} combinaison(s) possible(s) :\n")
                for j, combo in enumerate(combos, 1):
                    log_file.write(f"      {j}. {fmt_combo(combo)}\n")
                log_file.write(f"\n")
        
        if len(all_solutions) > max_solutions_displayed:
            if log_file:
                log_file.write(f"... et {len(all_solutions) - max_solutions_displayed} autre(s) solution(s)\n\n")
        
        # Résumé de la meilleure (fichier seulement)
        best = all_solutions[0]
        target, gx, gy, combos, pct, score = best
        if log_file:
            log_file.write("═" * 80 + "\n")
            log_file.write("💡 RECOMMANDATION : Solution optimale\n")
            log_file.write("═" * 80 + "\n")
            log_file.write(f"Utiliser une grille de {gx:g} × {gy:.3f} m avec {target} éléments de grille\n")
            log_file.write(f"Précision : score de {score:.2f} (plus bas = meilleur)\n")
            if combos:
                nb_apts = len(combos[0])
                log_file.write(f"Nombre d'appartements (exemple) : {nb_apts}\n")
        
        # Message console simplifié
        print(f"\n✅ {len(all_solutions)} solution(s) trouvée(s)")
        print(f"🏆 Meilleure : Grille {gx:g}×{gy:.3f}m, {target} éléments, score {score:.2f}")
        
    else:
        print("\n❌ Aucune solution trouvée")
        if log_file:
            log_file.write("❌ Aucune solution trouvée avec les paramètres actuels.\n\n")
            log_file.write("💡 SUGGESTIONS pour trouver des solutions :\n")
            log_file.write(f"   • Augmenter percentage_tolerance (actuellement {percentage_tolerance}% → essayer 10.0 ou 15.0)\n")
            log_file.write(f"   • Élargir target_elements_range (actuellement {target_elements_range} → essayer (5, 50))\n")
            log_file.write(f"   • Élargir search_range_x/y (actuellement x:{search_range_x}, y:{search_range_y})\n")
            log_file.write(f"   • Réduire search_step pour plus de précision (actuellement {search_step} → essayer 0.05)\n")
            if x_fixed or y_fixed:
                log_file.write(f"   • Essayer de ne fixer aucune dimension pour explorer x ET y librement\n")
            log_file.write("\n")
    
    # Fermer le fichier et afficher le chemin
    if log_file:
        log_file.close()
        print(f"💾 Résultats détaillés dans : {output_path}")
    
    return all_solutions, output_path
