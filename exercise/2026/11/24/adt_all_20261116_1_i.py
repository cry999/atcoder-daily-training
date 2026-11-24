# >>> atcoder-stat >>>
# started_at  = 2026-11-24T09:28:44+09:00
# solved_at   = 2026-11-24T09:48:17+09:00
# duration_ms = 1173003
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import functools
import sys

sys.setrecursionlimit(10**6)

N, M = map(int, input().split())
g: list[list[int]] = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

(*W,) = map(int, input().split())
(*A,) = map(int, input().split())


INF = 10**18


@functools.cache
def dfs(u: int) -> int:
    dp = [-INF] * W[u]
    dp[0] = 0
    for v in g[u]:
        if W[v] >= W[u]:
            continue
        c = dfs(v)
        for w in range(W[u] - 1, W[v] - 1, -1):
            dp[w] = max(dp[w], dp[w - W[v]] + c)

    return max(dp) + 1


ans = 0
for u in range(N):
    print(f"[DEBUG] {u=} {dfs(u)=}")
    if A[u] == 0:
        continue
    ans += A[u] * dfs(u)
print(ans)
