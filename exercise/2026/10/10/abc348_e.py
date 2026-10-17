# >>> atcoder-stat >>>
# started_at  = 2026-10-10T15:43:04+09:00
# solved_at   = 2026-10-10T20:52:43+09:00
# duration_ms = 18579102
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

sys.setrecursionlimit(10**6)


N = int(input())
g = [[] for _ in range(N)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g[a].append(b)
    g[b].append(a)
(*C,) = map(int, input().split())

dp = [0] * N
sub = [0] * N


def dfs(u: int, p: int = -1):
    sub[u] = C[u]
    for v in g[u]:
        if v == p:
            continue
        dfs(v, u)
        sub[u] += sub[v]
        dp[u] += dp[v] + sub[v]
    return


dfs(0)

f = [0] * N
f[0] = dp[0]

total = sum(C)

q = [(0, -1)]
for u, p in q:
    for v in g[u]:
        if v == p:
            continue
        f[v] = f[u] + total - 2 * sub[v]
        q.append((v, u))

print(min(f))
