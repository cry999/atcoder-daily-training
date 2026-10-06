# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:00:38+09:00
# solved_at   = 2026-10-03T11:07:42+09:00
# duration_ms = 424888
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU
import sys

input = sys.stdin.readline


# 考察
# 1. A[u] < A[v] となる u -> v だけ残した有向グラフと考えていい
# 2. A[u] == A[v] で u と v に辺がある場合は、縮退する。


N, M = map(int, input().split())
(*A,) = map(int, input().split())

dsu = DSU(N)
edges = []
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    if A[u] == A[v]:
        dsu.merge(u, v)
    else:
        edges.append((u, v))


g = [[] for _ in range(N)]
for u, v in edges:
    ru, rv = dsu.leader(u), dsu.leader(v)
    if A[ru] < A[rv]:
        g[ru].append(rv)
    else:
        g[rv].append(ru)

dist = [0] * N
dist[dsu.leader(0)] = 1
for u in sorted(range(N), key=lambda x: A[x]):
    if u != dsu.leader(u):
        continue
    if dist[u] == 0:
        continue
    for v in g[u]:
        dist[v] = max(dist[v], dist[u] + 1)

print(dist[dsu.leader(N - 1)])
