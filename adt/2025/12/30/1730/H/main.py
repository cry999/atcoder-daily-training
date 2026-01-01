N, M, L = map(int, input().split())
(*A,) = map(int, input().split())

f = [[0] * M for _ in range(L)]
for i in range(N):
    for j in range(M):
        f[i % L][j] += j - (A[i] % M)
        if j < A[i] % M:
            f[i % L][j] += M

dp = [[float("inf")] * M for _ in range(L + 1)]
dp[0][0] = 0
for i in range(L):
    for j in range(M):
        for k in range(M):
            dp[i + 1][(k + j) % M] = min(
                dp[i + 1][(k + j) % M],
                dp[i][k] + f[i][j],
            )

print(dp[L][0])
