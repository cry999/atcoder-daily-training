# >>> atcoder-stat >>>
# started_at  = 2026-10-01T10:20:14+09:00
# solved_at   = 2026-10-01T11:21:07+09:00
# duration_ms = 3653546
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import sys
from atcoder.dsu import DSU

input = sys.stdin.readline


N, M = map(int, input().split())
(*A,) = map(int, input().split())

uf = DSU(N)

g = [[] for _ in range(N)]
edges = []
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    edges.append((u, v))
    if A[u] == A[v]:
        uf.merge(u, v)

for u, v in edges:
    ru, rv = uf.leader(u), uf.leader(v)
    if A[ru] < A[rv]:
        g[ru].append(rv)
    if A[rv] < A[ru]:
        g[rv].append(ru)


start = uf.leader(0)
goal = uf.leader(N - 1)

dp = [0] * N
dp[start] = 1
for u in sorted(range(N), key=lambda u: A[u]):
    if dp[u] == 0:
        continue
    for v in g[u]:
        dp[v] = max(dp[v], dp[u] + 1)

print(dp[goal])
