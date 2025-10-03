"""
Algorithmes de combinaisons
"""
from itertools import combinations_with_replacement
from typing import Dict, List, Tuple
from functools import lru_cache, reduce
import math

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
