# >>> atcoder-stat >>>
# started_at  = 2026-07-17T19:09:04+09:00
# solved_at   = 2026-07-17T19:16:11+09:00
# duration_ms = 427488
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353


N, M, K, S, T, X = map(int, input().split())
S -= 1
T -= 1
X -= 1
g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

dp = [[0] * 2 for _ in range(N)]
dp[S][0] = 1

for _ in range(K):
    ndp = [[0] * 2 for _ in range(N)]

    for u in range(N):
        for v in g[u]:
            if v != X:
                ndp[v][0] += dp[u][0]
                ndp[v][1] += dp[u][1]
            else:
                ndp[v][0] += dp[u][1]
                ndp[v][1] += dp[u][0]

            ndp[v][0] %= MOD
            ndp[v][1] %= MOD

    dp = ndp

print(dp[T][0])
