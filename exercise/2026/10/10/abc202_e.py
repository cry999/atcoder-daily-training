# >>> atcoder-stat >>>
# started_at  = 2026-10-10T11:56:11+09:00
# solved_at   = 2026-10-10T13:15:55+09:00
# duration_ms = 4784994
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left
import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**6)


N = int(input())
(*P,) = map(int, input().split())
g = [[] for _ in range(N)]
for i in range(1, N):
    g[P[i - 1] - 1].append(i)


tin = [0] * N
tout = [0] * N
by_depth = [[] for _ in range(N)]


def dfs(u: int, n: int = 0, d: int = 0):
    tin[u] = n
    by_depth[d].append(tin[u])
    for v in g[u]:
        n = dfs(v, n + 1, d + 1)
    tout[u] = n + 1
    return n


dfs(0)
print(f"[DEBUG] {by_depth=}")
Q = int(input())
for _ in range(Q):
    u, d = map(int, input().split())
    u -= 1

    ans = bisect_left(by_depth[d], tout[u]) - bisect_left(by_depth[d], tin[u])
    print(ans)
