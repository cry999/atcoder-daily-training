# >>> atcoder-stat >>>
# started_at  = 2026-07-06T17:03:27+09:00
# solved_at   = 2026-07-06T17:08:34+09:00
# duration_ms = 307450
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from itertools import permutations
from math import sqrt, perm

n = int(input())
towns = [tuple(map(int, input().split())) for _ in range(n)]

total_dist = 0
for seq in permutations(range(n)):
    x0, y0 = towns[seq[0]]
    dist = 0
    for i in seq:
        x, y = towns[i]
        dist += sqrt((x0 - x) ** 2 + (y0 - y) ** 2)
        x0, y0 = x, y
    total_dist += dist

print(total_dist / perm(n))
