"""Compare random-cut reflection formula with all small binary orders."""
from itertools import combinations
from math import comb

checks = 0
for needed in range(9):
    for forbidden in range(9):
        observed = 0
        for selected in combinations(range(needed + forbidden), needed):
            selected = set(selected)
            value = best = needed
            for index in range(needed + forbidden):
                value += -1 if index in selected else 1
                best = min(best, value)
            observed += best
        observed /= comb(needed + forbidden, needed)
        lo, hi = sorted((needed, forbidden))
        ratio = 1.0
        theory = float(lo)
        for offset in range(lo):
            ratio *= (lo - offset) / (hi + offset + 1)
            theory -= ratio
        assert abs(theory - observed) < 1e-10, (needed, forbidden, theory, observed)
        checks += 1
print('random-cut formula checks:', checks)
