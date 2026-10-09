# >>> atcoder-stat >>>
# started_at  = 2026-10-09T08:42:41+09:00
# solved_at   = 2026-10-09T08:48:43+09:00
# duration_ms = 362641
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU

N, M = map(int, input().split())
edges = []
for _ in range(M):
    a, b, c = map(int, input().split())
    edges.append((c, a - 1, b - 1))

edges.sort()

dsu = DSU(N)
ans = 0
for c, a, b in edges:
    if c <= 0 or not dsu.same(a, b):
        dsu.merge(a, b)
    else:
        ans += c
print(ans)
