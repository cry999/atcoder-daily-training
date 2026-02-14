N, M, L = map(int, input().split())

(*A,) = map(int, input().split())

dp = [[float("inf")] * M for _ in range(L + 1)]
dp[0][0] = 0

# ope[i][m]: A[i], A[i+L], ..., A[i+kL] の全てを M で割ったあまりが m になるために必要な操作回数。
ope = [[0] * M for _ in range(N)]
for i in range(L):
    for d in range(i, N, L):
        for m in range(M):
            a = A[d] % M
            if m >= a:
                ope[i][m] += m - a
            else:
                ope[i][m] += m + M - a

for i in range(L):
    for j in range(M):
        for m in range(M):
            dp[i + 1][j] = min(dp[i + 1][j], ope[i][m] + dp[i][(j - m) % M])

print(dp[L][0])
