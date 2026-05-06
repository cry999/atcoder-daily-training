MOD = 998244353

N, M, K, S, T, X = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

# dp[u][k][d]: 頂点 u に k 回の移動かつ X を経由した回数を 2 で割ったあまりが d の状態で辿り着く場合の数
dp = [[[0, 0] for _ in range(K + 1)] for _ in range(N + 1)]
dp[S][0][0] = 1

for k in range(K):
    for u in range(1, N + 1):
        for d in range(2):
            for v in g[u]:
                # u -> v
                if v == X:
                    dp[v][k + 1][1 - d] += dp[u][k][d]
                    dp[v][k + 1][1 - d] %= MOD
                else:
                    dp[v][k + 1][d] += dp[u][k][d]
                    dp[v][k + 1][d] %= MOD

print(dp[T][K][0])
