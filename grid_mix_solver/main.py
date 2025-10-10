"""
Point d'entrée principal refactorisé pour le solveur de mix d'appartements
"""
from src.explorers.grid_explorer import explore_solutions

# ═══════════════════════════════════════════════════════════════════════════
# PARAMÈTRES DE CONFIGURATION - À MODIFIER SELON VOS BESOINS
# ═══════════════════════════════════════════════════════════════════════════

# Plages de recherche pour les dimensions de grille
search_range_x = (3.6, 3.6)
search_range_y = (3.6, 3.6)
search_step = 0.1

# Plage de recherche pour le nombre d'éléments de grille
target_elements_range = (160, 180)

# Surfaces des appartements (en m²)
apt_areas = {
    #"1p": 30,
    "2.5p": 60,
    "3.5p": 80,
    "4.5p": 95,
    #"5.5p": 110
}

# Facteur de conversion net → surface de plancher
net_to_floor_factor = 1.12
apt_floor_areas = {apt: area * net_to_floor_factor for apt, area in apt_areas.items()}

# Pourcentages cibles (imposés par le programme du concours)
target_percentages = {
    #"1p": 5,
    "2.5p": 40.0,
    "3.5p": 25.0,
    "4.5p": 35.0,
    #"5.5p": 7
}

# Tolérance de pourcentage
# Ancien comportement: une seule valeur (ex: 15.0) = ±15 points de % pour tous
# Nouveau: vous pouvez définir par type soit une tolérance symétrique, soit un range absolu
# Exemples:
# percentage_tolerance = 15.0
# percentage_tolerance = {"2.5p": 12.0, "3.5p": 8.0, "4.5p": 10.0}
# percentage_tolerance = {"2.5p": (35.0, 45.0), "3.5p": (20.0, 30.0), "4.5p": (30.0, 40.0)}
percentage_tolerance = {
    "2.5p": (35.0, 45.0),
    "3.5p": (20.0, 30.0),
    "4.5p": (30.0, 40.0)
}

# Paramètres de quantification
quantum = 0.5
method = "round"
round_variations = False
# Activer la recherche exhaustive de combinaisons
search_combinations = True
# Restreindre le nombre d'appartements par combinaison (min, max) ou None
combination_length_range = (3, 12)

# Contraintes du projet
nombre_logements = 160
max_etages_par_batiment = 4.5

# Affichage et sauvegarde des résultats
max_solutions_displayed = 100
save_to_file = True
output_directory = "results"


# ═══════════════════════════════════════════════════════════════════════════
# EXÉCUTION - NE PAS MODIFIER CETTE SECTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    solutions, output_path = explore_solutions(
        apt_areas=apt_floor_areas,
        target_percentages=target_percentages,
        quantum=quantum,
        method=method,
        search_range_x=search_range_x,
        search_range_y=search_range_y,
        search_step=search_step,
        target_elements_range=target_elements_range,
        percentage_tolerance=percentage_tolerance,
        combination_length_range=combination_length_range,
        max_solutions_displayed=max_solutions_displayed,
        save_to_file=save_to_file,
        output_directory=output_directory,
        nombre_logements=nombre_logements,
        max_etages_par_batiment=max_etages_par_batiment,
        round_variations=round_variations,
        search_combinations=search_combinations
    )


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENTATION DES PARAMÈTRES
# ═══════════════════════════════════════════════════════════════════════════

"""
┌─────────────────────────────────────────────────────────────────────────┐
│ PLAGES DE RECHERCHE POUR LES DIMENSIONS DE LA GRILLE                │
└─────────────────────────────────────────────────────────────────────────┘

🎯 FONCTIONNEMENT :
   Pour FIXER une dimension : mettre (valeur, valeur)
   Pour EXPLORER une dimension : mettre (min, max)

📐 EXEMPLES :
   search_range_x = (3.0, 3.0)
   → La largeur est FIXÉE à 3.0m
   → Le script ne testera que x=3.0m

   search_range_x = (2.5, 4.0)
   → La largeur est VARIABLE entre 2.5m et 4.0m
   → Avec search_step=0.5, testera : 2.5m, 3.0m, 3.5m, 4.0m

💡 CAS D'USAGE :
   • (3.0, 3.0) si votre module structurel impose une largeur de 3m
   • (2.5, 4.0) si vous explorez différentes largeurs possibles

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH_STEP : Pas d'exploration pour les dimensions (en mètres)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Teste toutes les 10cm (précis, temps raisonnable)


┌─────────────────────────────────────────────────────────────────────────┐
│ PLAGE DE RECHERCHE POUR LE NOMBRE D'ÉLÉMENTS DE GRILLE              │
└─────────────────────────────────────────────────────────────────────────┘
Définit combien d'unités de grille au total le script va tester

⚠️ ATTENTION : "élément" = "unité de grille" ≠ "appartement" !

🏗️ EXEMPLE CONCRET avec grille 3×5m (15m² par cellule) :

   Calcul des unités par type :
   • 2.5p = 60m² / 15m² = 4 unités
   • 3.5p = 80m² / 15m² = 5.3 → arrondi à 5.5 unités
   • 4.5p = 95m² / 15m² = 6.3 → arrondi à 6.5 unités
   • 5.5p = 110m² / 15m² = 7.3 → arrondi à 7.5 unités

   Si target_elements = 16 :
   → Combinaisons possibles :
      • 4 + 5.5 + 6.5 = 16 → 3 appartements (1×2.5p + 1×3.5p + 1×4.5p)
      • 4 + 4 + 4 + 4 = 16 → 4 appartements (4×2.5p)
      • 5.5 + 5.5 + 5 = 16 → erreur, pas possible avec quantum=0.5
      etc.

   Si target_elements = 26 :
   → Plus de combinaisons possibles, plus d'appartements au total


┌─────────────────────────────────────────────────────────────────────────┐
│ SURFACES DES APPARTEMENTS (en m²)                                    │
└─────────────────────────────────────────────────────────────────────────┘
Ces valeurs définissent la surface de référence pour chaque type d'appartement.
Le script va chercher des grilles qui, en multipliant les "unités de grille" 
par la surface d'une cellule, donnent une surface proche de ces valeurs.

📐 EXEMPLE :
   Si apt_areas = {"2.5p": 60} et que la grille fait 3×5m (=15m² par cellule)
   → Le script calculera que 2.5p = 60/15 = 4 unités de grille
   → Un appartement 2.5p occupera 4 cellules = 4×15m² = 60m² ✓


┌─────────────────────────────────────────────────────────────────────────┐
│ FACTEUR NET → SURFACE DE PLANCHER                                   │
└─────────────────────────────────────────────────────────────────────────┘
Les surfaces ci-dessus sont NETTES (sans murs). Pour les calculs, on peut
convertir en surfaces de plancher via un facteur multiplicatif.
Exemple : 1.12 = +12% par rapport au net.


┌─────────────────────────────────────────────────────────────────────────┐
│ POURCENTAGES CIBLES (imposés par le programme du concours)          │
└─────────────────────────────────────────────────────────────────────────┘
Ces pourcentages définissent la répartition souhaitée des surfaces par type
d'appartement dans le projet final.


┌─────────────────────────────────────────────────────────────────────────┐
│ TOLÉRANCE DE POURCENTAGE                                             │
└─────────────────────────────────────────────────────────────────────────┘
Écart maximum accepté pour CHAQUE type d'appartement (en points de %)


┌─────────────────────────────────────────────────────────────────────────┐
│ PARAMÈTRES DE QUANTIFICATION                                         │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUANTUM : Précision de la quantification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Détermine par quels multiples les unités de grille peuvent être arrondies

🔢 EXEMPLE avec grille 3×5m (15m² par cellule) et quantum différents :

   Pour un 2.5p de 60m² → 60/15 = 4.0 unités brutes
   • quantum = 1.0 → arrondi à 4.0 (multiples de 1)
   • quantum = 0.5 → arrondi à 4.0 (multiples de 0.5 : 3.5, 4.0, 4.5...)
   • quantum = 0.1 → arrondi à 4.0 (multiples de 0.1 : 3.9, 4.0, 4.1...)

   Pour un 3.5p de 80m² → 80/15 = 5.33 unités brutes
   • quantum = 1.0 → arrondi à 5.0
   • quantum = 0.5 → arrondi à 5.5 ← MEILLEURE PRÉCISION
   • quantum = 0.1 → arrondi à 5.3

⚡ IMPACT SUR LA VITESSE :
   quantum = 1.0   → Très rapide (teste 10, 11, 12...)
   quantum = 0.5   → Rapide (teste 10, 10.5, 11, 11.5...) ← RECOMMANDÉ
   quantum = 0.1   → TRÈS LENT (teste 10.0, 10.1, 10.2, 10.3...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
METHOD : Méthode d'arrondi pour convertir surface → unités de grille
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 EXEMPLE avec 80m² / 15m² = 5.33 unités brutes et quantum = 0.5 :
   • method = "round" → arrondit au plus proche → 5.33 devient 5.5
   • method = "floor" → arrondit vers le bas → 5.33 devient 5.0
   • method = "ceil"  → arrondit vers le haut → 5.33 devient 5.5

💡 CONSEIL : Utilisez "round" (par défaut) dans la plupart des cas

Explorer des variations d'arrondi (Option 2) :
Si True, teste pour chaque type l'option floor/ceil (et +quantum si exact)


┌─────────────────────────────────────────────────────────────────────────┐
│ CONTRAINTES DU PROJET                                                 │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOMBRE_LOGEMENTS : Nombre total de logements du projet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏗️ EXEMPLE :
   nombre_logements = 130
   → Le projet doit contenir 130 appartements au total
   → Le script calculera :
      • La surface totale des logements (en fonction du mix)
      • Le nombre d'étages nécessaires
      • Le nombre de bâtiments nécessaires

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAX_ETAGES_PAR_BATIMENT : Nombre maximum d'étages par bâtiment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 FONCTIONNEMENT :
   Un étage = target_elements unités de grille en horizontal
   Le script calcule combien d'étages sont nécessaires pour loger tous les appartements

📊 EXEMPLE :
   nombre_logements = 130, target_elements = 31
   → Total cellules nécessaires = surface_totale / surface_cellule
   → Nombre d'étages = cellules_totales / 31
   
   Si ça donne 35 étages nécessaires et max_etages_par_batiment = 4 :
   → Il faudra 35/4 = 9 bâtiments (arrondis au supérieur)
   → 8 bâtiments de 4 étages + 1 bâtiment de 3 étages


┌─────────────────────────────────────────────────────────────────────────┐
│ AFFICHAGE ET SAUVEGARDE DES RÉSULTATS                                │
└─────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAVE_TO_FILE : Activer/désactiver la sauvegarde
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 EXEMPLE :
   save_to_file = True
   → Crée un fichier "results/solutions_20250930_154532.txt"
   → Affiche aussi un résumé dans la console

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT_DIRECTORY : Dossier de sauvegarde
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 EXEMPLE :
   output_directory = "results"
   → Fichiers sauvegardés dans : results/solutions_AAAAMMJJ_HHMMSS.txt
   → Exemple : results/solutions_20250930_153704.txt
"""
