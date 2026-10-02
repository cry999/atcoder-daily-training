# >>> atcoder-stat >>>
# started_at  = 2026-10-02T08:43:04+09:00
# solved_at   = 2026-10-02T08:57:00+09:00
# duration_ms = 836046
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from atcoder.dsu import DSU

input = sys.stdin.readline


N, M = map(int, input().split())
(*A,) = map(int, input().split())
E = []
for _ in range(M):
    u, v = map(int, input().split())
    E.append((u - 1, v - 1))

# 考察
# 1. 広義単調増加なので、A[i] <= A[j] を満たす方向 i -> j だけ残した有向グラフと考え直して良い
# 2. 広義のままだと A[i] = A[j] で i と j の間に辺がある時にどう扱うかが面倒。
# 3. 2 の解決のために、A[i] = A[j] かつ i と j の間に辺がある場合は縮退して一つの頂点とみなす。
# 4. あとは、DFS で各頂点からの長さを考えればいい？

dsu = DSU(N)
for u, v in E:
    if A[u] == A[v]:
        dsu.merge(u, v)

g = [[] for _ in range(N)]
for u, v in E:
    u, v = dsu.leader(u), dsu.leader(v)
    if A[u] < A[v]:
        g[u].append(v)
    if A[u] > A[v]:
        g[v].append(u)

order = sorted(range(N), key=lambda u: A[u])
dp = [0] * N
dp[dsu.leader(0)] = 1
for u in order:
    if u != dsu.leader(u):
        continue
    if dp[u] <= 0:
        continue
    for v in g[u]:
        dp[v] = max(dp[v], dp[u] + 1)

print(dp[dsu.leader(N - 1)])
