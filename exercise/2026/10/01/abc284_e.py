# >>> atcoder-stat >>>
# started_at  = 2026-10-01T09:03:15+09:00
# solved_at   = 2026-10-01T09:18:31+09:00
# duration_ms = 916527
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**6)


MAX = 10**6
N, M = map(int, input().split())
g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].append(v)
    g[v].append(u)

visited = [False] * N


def dfs(u: int, count: int) -> int:
    print(f"[DEBUG] dfs({u=}, {count=})")
    visited[u] = True
    routes = 1
    if routes >= MAX:
        return MAX

    for v in g[u]:
        if visited[v]:
            continue
        print(f"[DEBUG] in:  {u=} -> {v=}")
        routes += dfs(v, count)
        print(f"[DEBUG] out: {u=} <- {v=}")
        if routes >= MAX:
            return MAX

    visited[u] = False
    return routes


print(dfs(0, 0))
