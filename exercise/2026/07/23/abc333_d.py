# >>> atcoder-stat >>>
# started_at  = 2026-07-23T11:46:27+09:00
# solved_at   = 2026-07-23T12:10:46+09:00
# duration_ms = 1459190
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**7)

N = int(input())
g = [[] for _ in range(N)]

edges = [0] * N
for _ in range(N - 1):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].append(v)
    g[v].append(u)
    edges[u] += 1
    edges[v] += 1

leaves = []
dp = [1] * N
for u in range(N):
    if edges[u] == 1:  # leaf
        leaves.append(u)


visited = [False] * N
for u in leaves:
    visited[u] = True
    if u == 0:
        continue
    for v in g[u]:
        if visited[v]:
            # 訪問済み
            continue
        print(f"[DEBUG] {u=} -> {v=}")
        dp[v] += dp[u]
        edges[v] -= 1
        print(f"[DEBUG] {edges[v]=}")
        if edges[v] != 1:
            continue
        leaves.append(v)

max_depth = 0
for v in g[0]:
    max_depth = max(max_depth, dp[v])

print(N - max_depth)
