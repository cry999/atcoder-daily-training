# >>> atcoder-stat >>>
# started_at  = 2026-07-18T20:37:12+09:00
# solved_at   = 2026-07-18T20:42:50+09:00
# duration_ms = 338120
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N = int(input())
deck = [int(input()) for _ in range(N)]

INF = 10**18
L = [INF] * (N + 1)
L[0] = 0

for c in deck:
    i = bisect_left(L, c)
    L[i] = c

for x in range(N):
    if L[x + 1] == INF:
        print(N - x)
        break
else:
    print(0)
