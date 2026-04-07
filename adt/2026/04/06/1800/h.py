MOD = 998244353

N, M, K = map(int, input().split())
cannot = [set() for _ in range(N)]

for _ in range(M):
    u, v = map(lambda x: int(x) - 1, input().split())
    cannot[u].add(v)
    cannot[v].add(u)

# dp[i][j] := A0=0, Ai=j である場合の数
# dp[i+1][j] := sum(dp[i][j] for j in range(N)) - sum(dp[i][k] for k in cannot[i])
dp = [[0] * N for _ in range(K + 1)]
dp[0][0] = 1

for k in range(K):
    ni = sum(dp[k]) % MOD
    for j in range(N):
        dp[k + 1][j] = ni - dp[k][j]
        dp[k + 1][j] %= MOD

    for j in range(N):
        for c in cannot[j]:
            dp[k + 1][c] -= dp[k][j]
            dp[k + 1][c] %= MOD

print(dp[K][0])
