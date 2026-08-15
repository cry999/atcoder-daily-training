# >>> atcoder-stat >>>
# started_at  = 2026-08-08T11:30:48+09:00
# solved_at   = 2026-08-08T11:37:48+09:00
# duration_ms = 420532
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
S, T, X = S - 1, T - 1, X - 1

g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].append(v)
    g[v].append(u)

dp = [[0] * 2 for _ in range(N)]
dp[S][0] = 1

for _ in range(K):
    ndp = [[0] * 2 for _ in range(N)]

    for u in range(N):
        for v in g[u]:
            if v == X:
                ndp[v][0] += dp[u][1]
                ndp[v][1] += dp[u][0]
            else:
                ndp[v][0] += dp[u][0]
                ndp[v][1] += dp[u][1]

    dp = [[x % MOD, y % MOD] for x, y in ndp]

print(dp[T][0])
